from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any, cast

WORKSPACE = Path("/workspace")
OUTPUT = WORKSPACE / "output"
OUTPUT_NAMES = {"candidates.json", "discovery_metrics.json", "run_report.md"}
MAX_TOOL_STEPS = 40
MAX_TOOL_OUTPUT = 4_000
MAX_PAGE_LINES = 250
MAX_SEARCH_FILES = 100
MAX_SEARCH_BYTES = 2_000_000
MAX_SEARCH_MATCHES = 50
MAX_SEARCH_QUERY_CHARS = 200
MAX_COMPLETION_TOKENS = 1_024
MAX_CONTEXT_CHARS = 18_000
MAX_CONTEXT_GROUPS = 6
MAX_RATE_LIMIT_RETRIES = 3
MAX_RETRY_SECONDS = 30.0
MAX_HTTP_ERROR_BODY = 4_000
MAX_TOOL_USE_RECOVERIES = 2
USER_AGENT = "policy-blind-agent/1.0 blind-benchmark"


class ToolUseFailedError(RuntimeError):
    """Recoverable provider rejection of a generated tool call."""


def _workspace_path(value: str) -> Path:
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise ValueError("path must be a safe workspace-relative path")
    path = WORKSPACE.joinpath(*relative.parts)
    if path.is_symlink() or not path.is_file():
        raise ValueError("path must identify a regular workspace file")
    return path


def _check_outputs() -> None:
    for path in OUTPUT.rglob("*"):
        if path.is_symlink():
            raise RuntimeError(f"output symlink is forbidden: {path.name}")
        if path.is_dir():
            if path != OUTPUT:
                raise RuntimeError(f"nested output directory is forbidden: {path.name}")
            continue
        relative = path.relative_to(OUTPUT).as_posix()
        if relative not in OUTPUT_NAMES:
            raise RuntimeError(f"unapproved output artifact: {relative}")


def list_workspace() -> str:
    return json.dumps(
        sorted(
            path.relative_to(WORKSPACE).as_posix()
            for path in WORKSPACE.rglob("*")
            if path.is_file() and not path.is_symlink()
        )
    )


def read_file(path: str, line_start: object = 1, line_end: object = None) -> str:
    if isinstance(line_start, bool) or not isinstance(line_start, int) or line_start < 1:
        raise ValueError("line_start must be a 1-based positive integer")
    if line_end is None:
        line_end = line_start + MAX_PAGE_LINES - 1
    if isinstance(line_end, bool) or not isinstance(line_end, int) or line_end < line_start:
        raise ValueError(
            "line_end must be an inclusive integer greater than or equal to line_start"
        )
    if line_end - line_start + 1 > MAX_PAGE_LINES:
        raise ValueError(f"read_file page may contain at most {MAX_PAGE_LINES} lines")
    lines = _workspace_path(path).read_text(encoding="utf-8").splitlines()
    actual_end = min(line_end, len(lines))
    selected = lines[line_start - 1 : actual_end]
    return json.dumps(
        {
            "path": path,
            "line_start": line_start,
            "line_end": actual_end,
            "total_lines": len(lines),
            "content": "\n".join(
                f"{number}: {line}" for number, line in enumerate(selected, start=line_start)
            )[:MAX_TOOL_OUTPUT],
        }
    )


def search(path: str, query: str, max_matches: object = 20) -> str:
    if not query or len(query) > MAX_SEARCH_QUERY_CHARS:
        raise ValueError(f"query must contain 1-{MAX_SEARCH_QUERY_CHARS} characters")
    if isinstance(max_matches, bool) or not isinstance(max_matches, int):
        raise ValueError("max_matches must be an integer")
    if not 1 <= max_matches <= MAX_SEARCH_MATCHES:
        raise ValueError(f"max_matches must be between 1 and {MAX_SEARCH_MATCHES}")
    relative = PurePosixPath(path)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError("path must be a safe workspace-relative path")
    root = WORKSPACE.joinpath(*relative.parts) if relative.parts else WORKSPACE
    if root.is_symlink() or not root.exists():
        raise ValueError("search path must identify an existing non-symlink workspace path")
    if root.is_file():
        candidates = [root]
    elif root.is_dir():
        candidates = sorted(root.rglob("*"))
    else:
        raise ValueError("search path must identify a regular file or directory")
    matches: list[dict[str, object]] = []
    files_scanned = 0
    bytes_scanned = 0
    for candidate in candidates:
        if candidate.is_symlink() or not candidate.is_file():
            continue
        if files_scanned >= MAX_SEARCH_FILES:
            break
        size = candidate.stat().st_size
        if bytes_scanned + size > MAX_SEARCH_BYTES:
            break
        files_scanned += 1
        bytes_scanned += size
        try:
            lines = candidate.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, start=1):
            if query in line:
                matches.append(
                    {
                        "path": candidate.relative_to(WORKSPACE).as_posix(),
                        "line": number,
                        "text": line[:500],
                    }
                )
                if len(matches) >= max_matches:
                    break
        if len(matches) >= max_matches:
            break
    return json.dumps(
        {
            "query": query,
            "path": path,
            "matches": matches,
            "files_scanned": files_scanned,
            "bytes_scanned": bytes_scanned,
            "truncated": len(matches) >= max_matches,
        }
    )[:MAX_TOOL_OUTPUT]


# Pattern rather than an exact name list: this is defense in depth (the actor itself is retired
# from the shipped image; see infra/docker/blind-agent.Dockerfile), so a fixed 4-name blocklist
# would silently stop protecting anything the moment a 5th provider key or an unrelated secret
# (AWS_SECRET_ACCESS_KEY, DATABASE_URL-style credentials, a signing/private key, ...) shows up in
# the parent environment.
_CREDENTIAL_ENV_NAME = re.compile(
    r"(API[_-]?KEY|SECRET|TOKEN|PASSWORD|PASSWD|ACCESS[_-]?KEY|PRIVATE[_-]?KEY|CREDENTIAL)",
    re.IGNORECASE,
)


def run_python(code: str) -> str:
    child_environment = {
        key: value for key, value in os.environ.items() if not _CREDENTIAL_ENV_NAME.search(key)
    }
    completed = subprocess.run(
        ["python", "-c", code],
        cwd=WORKSPACE,
        capture_output=True,
        check=False,
        text=True,
        timeout=180,
        env=child_environment,
    )
    _check_outputs()
    result = {
        "returncode": completed.returncode,
        "stdout": completed.stdout[-MAX_TOOL_OUTPUT:],
        "stderr": completed.stderr[-MAX_TOOL_OUTPUT:],
    }
    return json.dumps(result)


TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": (
                "Search literal text in a workspace-relative regular file or directory. Results, "
                "files, bytes, and returned text are bounded; symlinks are never followed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "query": {"type": "string", "minLength": 1, "maxLength": 200},
                    "max_matches": {"type": "integer", "minimum": 1, "maximum": 50},
                },
                "required": ["path", "query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_workspace",
            "description": "List every regular file in the allowlisted workspace.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read a bounded page of a UTF-8 allowlisted workspace file. line_start and "
                "line_end are 1-based and inclusive; a page contains at most 250 lines."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "line_start": {"type": "integer", "minimum": 1},
                    "line_end": {"type": "integer", "minimum": 1},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": (
                "Execute Python in /workspace. Inputs are read-only; only the three approved "
                "files directly under /workspace/output may be created."
            ),
            "parameters": {
                "type": "object",
                "properties": {"code": {"type": "string"}},
                "required": ["code"],
                "additionalProperties": False,
            },
        },
    },
]


def dispatch(name: str, arguments: str) -> str:
    payload = json.loads(arguments or "{}")
    if name == "list_workspace":
        return list_workspace()
    if name == "read_file":
        line_start = payload.get("line_start", 1)
        line_end = payload.get("line_end")
        return read_file(str(payload["path"]), cast(int, line_start), cast(int | None, line_end))
    if name == "search":
        return search(str(payload["path"]), str(payload["query"]), payload.get("max_matches", 20))
    if name == "run_python":
        return run_python(str(payload["code"]))
    raise ValueError(f"unknown tool: {name}")


def bounded_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compacted = cast(list[dict[str, Any]], json.loads(json.dumps(messages)))
    for message in compacted:
        content = message.get("content")
        if isinstance(content, str) and len(content) > MAX_TOOL_OUTPUT:
            message["content"] = content[:MAX_TOOL_OUTPUT] + "...[truncated]"
        calls = message.get("tool_calls")
        if isinstance(calls, list):
            for raw_call in cast(list[object], calls):
                if not isinstance(raw_call, dict):
                    continue
                call = cast(dict[str, Any], raw_call)
                function = call.get("function")
                if isinstance(function, dict):
                    typed_function = cast(dict[str, Any], function)
                    arguments = typed_function.get("arguments")
                    if isinstance(arguments, str) and len(arguments) > MAX_TOOL_OUTPUT:
                        typed_function["arguments"] = json.dumps(
                            {"omitted": "executed tool arguments"}
                        )
    system = compacted[:1]
    groups: list[list[dict[str, Any]]] = []
    for message in compacted[1:]:
        if message.get("role") == "tool" and groups:
            groups[-1].append(message)
        else:
            groups.append([message])
    selected = groups[-MAX_CONTEXT_GROUPS:]
    while (
        selected
        and len(json.dumps(system + [item for group in selected for item in group]))
        > MAX_CONTEXT_CHARS
    ):
        selected.pop(0)
    result = system + [item for group in selected for item in group]
    if len(json.dumps(result)) > MAX_CONTEXT_CHARS:
        raise RuntimeError("blind actor context exceeds the configured budget")
    return result


def retry_delay(exc: urllib.error.HTTPError, attempt: int) -> float:
    raw = exc.headers.get("Retry-After")
    try:
        requested = float(raw) if raw is not None else float(2**attempt)
    except ValueError:
        requested = float(2**attempt)
    return min(max(requested, 0.0), MAX_RETRY_SECONDS)


def provider_completion(
    model: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": bounded_messages(messages),
        "temperature": 0.1,
        "max_completion_tokens": MAX_COMPLETION_TOKENS,
    }
    if tools is not None:
        payload.update({"tools": tools, "tool_choice": "auto"})
    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        request = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=180) as response:
                result: object = json.loads(response.read())
            break
        except urllib.error.HTTPError as exc:
            body = exc.read(MAX_HTTP_ERROR_BODY).decode("utf-8", errors="replace")
            if exc.code == 400 and "tool_use_failed" in body:
                raise ToolUseFailedError(safe_http_error(exc.code, body)) from None
            if exc.code != 429 or attempt == MAX_RATE_LIMIT_RETRIES:
                raise RuntimeError(safe_http_error(exc.code, body)) from None
            time.sleep(retry_delay(exc, attempt))
    else:
        raise RuntimeError("Groq retry loop terminated unexpectedly")
    if not isinstance(result, dict):
        raise RuntimeError("Groq returned an invalid response")
    return cast(dict[str, Any], result)


def safe_http_error(status: int, body: str) -> str:
    credential = os.environ.get("GROQ_API_KEY", "")
    if credential:
        body = body.replace(credential, "[REDACTED]")
    body = re.sub(r"(?i)bearer\s+[a-z0-9._~+/=-]+", "Bearer [REDACTED]", body)
    body = " ".join(body.split())[:MAX_HTTP_ERROR_BODY]
    return f"Groq HTTP {status}: {body or '<empty response body>'}"


def run(model: str, *, rehearsal: bool = False) -> None:
    if not os.environ.get("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is required")
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "You are the fresh Blind Discovery actor. Use the tools autonomously. First list "
                "the workspace, then read "
                "agents/ML_DISCOVERY_BLIND.md and BLIND_MANIFEST.json, inspect all relevant public "
                "inputs, run the frozen deterministic discovery implementation, and create exactly "
                "output/candidates.json, output/discovery_metrics.json, and output/run_report.md. "
                "Never claim causal validation or ground-truth comparison. Do not finish until all "
                "three artifacts exist."
                + (
                    " This is a non-benchmark infrastructure rehearsal. You must use "
                    "list_workspace; "
                    "read two bounded pages of public/rehearsal.py; call search with path='public' "
                    "and query='CREATE_REHEARSAL_OUTPUTS'; and execute public/rehearsal.py through "
                    "run_python. Do not invent analysis."
                    if rehearsal
                    else ""
                )
            ),
        }
    ]
    completed_capabilities: set[str] = set()
    paginated_pages: set[tuple[str, object, object]] = set()
    recoveries = 0
    inject_rehearsal_failure = rehearsal
    for _ in range(MAX_TOOL_STEPS):
        try:
            if inject_rehearsal_failure:
                inject_rehearsal_failure = False
                raise ToolUseFailedError("controlled rehearsal tool_use_failed")
            response = provider_completion(model, messages, TOOLS)
        except ToolUseFailedError as exc:
            if recoveries >= MAX_TOOL_USE_RECOVERIES:
                raise RuntimeError("Groq tool_use_failed recovery limit exceeded") from None
            recoveries += 1
            completed_capabilities.add("tool_use_failed_recovery")
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"A tool call was rejected ({exc}). Recover by issuing exactly one valid "
                        "call using only the declared tools and their JSON schemas. Available "
                        "tools: "
                        "list_workspace, read_file, search, run_python."
                    ),
                }
            )
            continue
        raw_choices: object = response.get("choices")
        if (
            not isinstance(raw_choices, list)
            or not raw_choices
            or not isinstance(raw_choices[0], dict)
        ):
            raise RuntimeError("Groq returned no completion choice")
        choices = cast(list[object], raw_choices)
        raw_message: object = cast(dict[str, Any], choices[0]).get("message")
        if not isinstance(raw_message, dict):
            raise RuntimeError("Groq returned an invalid assistant message")
        message = cast(dict[str, Any], raw_message)
        messages.append(message)
        raw_tool_calls: object = message.get("tool_calls")
        if not isinstance(raw_tool_calls, list) or not raw_tool_calls:
            _check_outputs()
            missing = sorted(name for name in OUTPUT_NAMES if not (OUTPUT / name).is_file())
            if missing:
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"The run is incomplete; create the missing artifacts: {missing}"
                        ),
                    }
                )
                continue
            if rehearsal:
                required = {
                    "list_workspace",
                    "paginated_read",
                    "search",
                    "run_python",
                    "tool_use_failed_recovery",
                }
                missing_capabilities = sorted(required - completed_capabilities)
                if missing_capabilities:
                    messages.append(
                        {
                            "role": "user",
                            "content": f"Rehearsal incomplete; exercise: {missing_capabilities}",
                        }
                    )
                    continue
            return
        for raw_call in cast(list[object], raw_tool_calls):
            if not isinstance(raw_call, dict):
                raise RuntimeError("Groq returned an invalid tool call")
            call = cast(dict[str, Any], raw_call)
            raw_function: object = call.get("function")
            if not isinstance(raw_function, dict):
                raise RuntimeError("Groq returned an invalid tool function")
            function = cast(dict[str, Any], raw_function)
            function_name = str(function.get("name"))
            try:
                raw_audit_arguments: object = json.loads(str(function.get("arguments", "{}")))
            except json.JSONDecodeError:
                raw_audit_arguments = {}
            audit_arguments = (
                cast(dict[str, object], raw_audit_arguments)
                if isinstance(raw_audit_arguments, dict)
                else {}
            )
            call_id: object = call.get("id")
            if not isinstance(call_id, str):
                raise RuntimeError("Groq tool call has no ID")
            try:
                result = dispatch(function_name, str(function.get("arguments", "{}")))
                if function_name == "list_workspace":
                    completed_capabilities.add("list_workspace")
                elif function_name == "read_file" and (
                    "line_start" in audit_arguments or "line_end" in audit_arguments
                ):
                    paginated_pages.add(
                        (
                            str(audit_arguments.get("path")),
                            audit_arguments.get("line_start"),
                            audit_arguments.get("line_end"),
                        )
                    )
                    if len(paginated_pages) >= 2:
                        completed_capabilities.add("paginated_read")
                elif function_name in {"search", "run_python"}:
                    completed_capabilities.add(function_name)
            except Exception as exc:  # tool errors must be returned to the actor for recovery
                result = json.dumps({"error": str(exc)})
            messages.append({"role": "tool", "tool_call_id": call_id, "content": result})
    raise RuntimeError("blind actor exceeded the tool-step limit")


def preflight(model: str) -> None:
    if not os.environ.get("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY is required")
    response = provider_completion(
        model,
        [
            {
                "role": "user",
                "content": (
                    "Call read_file exactly once for agents/ML_DISCOVERY_BLIND.md with "
                    "line_start=1 and line_end=20."
                ),
            }
        ],
        TOOLS,
    )
    choices: object = response.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise RuntimeError("Groq preflight returned no choices")
    message: object = cast(dict[str, Any], choices[0]).get("message")
    if not isinstance(message, dict):
        raise RuntimeError("Groq model returned an invalid preflight message")
    typed_message = cast(dict[str, Any], message)
    tool_calls = typed_message.get("tool_calls")
    if not isinstance(tool_calls, list) or not tool_calls:
        raise RuntimeError("Groq model did not produce the required tool call")
    first_call = cast(dict[str, Any], cast(list[object], tool_calls)[0])
    call_id = first_call.get("id")
    if not isinstance(call_id, str):
        raise RuntimeError("Groq preflight tool call has no ID")
    first_function: object = first_call.get("function")
    if not isinstance(first_function, dict):
        raise RuntimeError("Groq preflight tool call has no function")
    typed_first_function = cast(dict[str, Any], first_function)
    first_arguments = json.loads(str(typed_first_function.get("arguments", "{}")))
    if typed_first_function.get("name") != "read_file" or first_arguments != {
        "path": "agents/ML_DISCOVERY_BLIND.md",
        "line_start": 1,
        "line_end": 20,
    }:
        raise RuntimeError("Groq model did not produce the required paginated read")
    messages = [
        {
            "role": "user",
            "content": (
                "Call read_file exactly once for agents/ML_DISCOVERY_BLIND.md with "
                "line_start=1 and line_end=20."
            ),
        },
        typed_message,
        {
            "role": "tool",
            "tool_call_id": call_id,
            "content": json.dumps(
                {
                    "path": "agents/ML_DISCOVERY_BLIND.md",
                    "line_start": 1,
                    "line_end": 20,
                    "total_lines": 40,
                    "content": "1: preflight fixture",
                }
            ),
        },
        {
            "role": "user",
            "content": (
                "Now call read_file once for the same path with line_start=21 and line_end=40."
            ),
        },
    ]
    second = provider_completion(model, messages, TOOLS)
    second_choices: object = second.get("choices")
    if (
        not isinstance(second_choices, list)
        or not second_choices
        or not isinstance(second_choices[0], dict)
    ):
        raise RuntimeError("Groq sequential preflight returned no choices")
    second_message: object = cast(dict[str, Any], second_choices[0]).get("message")
    if not isinstance(second_message, dict):
        raise RuntimeError("Groq sequential preflight returned an invalid message")
    typed_second_message = cast(dict[str, Any], second_message)
    second_tool_calls = typed_second_message.get("tool_calls")
    if not isinstance(second_tool_calls, list) or not second_tool_calls:
        raise RuntimeError("Groq model did not complete the second tool turn")
    second_call = cast(dict[str, Any], cast(list[object], second_tool_calls)[0])
    second_function: object = second_call.get("function")
    if not isinstance(second_function, dict):
        raise RuntimeError("Groq second preflight tool call has no function")
    typed_second_function = cast(dict[str, Any], second_function)
    second_arguments = json.loads(str(typed_second_function.get("arguments", "{}")))
    if typed_second_function.get("name") != "read_file" or second_arguments != {
        "path": "agents/ML_DISCOVERY_BLIND.md",
        "line_start": 21,
        "line_end": 40,
    }:
        raise RuntimeError("Groq model did not produce the second paginated read")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--rehearsal", action="store_true")
    args = parser.parse_args()
    preflight(args.model) if args.preflight else run(args.model, rehearsal=args.rehearsal)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"BLIND_ACTOR_ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
