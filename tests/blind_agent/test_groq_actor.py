from __future__ import annotations

import json
import urllib.error
import urllib.request
from email.message import Message
from io import BytesIO
from pathlib import Path
from typing import Any, cast

import pytest

from tools.blind_agent import groq_actor


def test_actor_reads_runs_python_and_creates_only_approved_outputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    output = workspace / "output"
    output.mkdir(parents=True)
    (workspace / "public.txt").write_text("allowlisted", encoding="utf-8")
    monkeypatch.setattr(groq_actor, "WORKSPACE", workspace)
    monkeypatch.setattr(groq_actor, "OUTPUT", output)

    assert "public.txt" in groq_actor.list_workspace()
    page = json.loads(groq_actor.read_file("public.txt"))
    assert page == {
        "path": "public.txt",
        "line_start": 1,
        "line_end": 1,
        "total_lines": 1,
        "content": "1: allowlisted",
    }
    result = json.loads(
        groq_actor.run_python(
            "from pathlib import Path; import json; out=Path('output'); "
            "(out/'candidates.json').write_text(json.dumps({})); "
            "(out/'discovery_metrics.json').write_text(json.dumps({})); "
            "(out/'run_report.md').write_text('report')"
        )
    )
    assert result["returncode"] == 0
    assert {path.name for path in output.iterdir()} == groq_actor.OUTPUT_NAMES


def test_run_python_removes_provider_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    output = workspace / "output"
    output.mkdir(parents=True)
    monkeypatch.setattr(groq_actor, "WORKSPACE", workspace)
    monkeypatch.setattr(groq_actor, "OUTPUT", output)
    credential_names = (
        "GROQ_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        # Not a provider key: this is a pattern match (API_KEY/SECRET/TOKEN/PASSWORD/...), not a
        # fixed 4-name blocklist, so an unrelated credential must be stripped too.
        "AWS_SECRET_ACCESS_KEY",
        "SOME_SERVICE_TOKEN",
        "DB_PASSWORD",
    )
    for name in credential_names:
        monkeypatch.setenv(name, "must-not-reach-child")

    result = json.loads(groq_actor.run_python("import os; print(','.join(sorted(os.environ)))"))

    assert result["returncode"] == 0
    surviving = set(result["stdout"].strip().split(","))
    assert surviving.isdisjoint(credential_names)


def test_paginated_read_matches_gpt_oss_call_and_preserves_isolation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = workspace / "engine.py"
    source.write_text("\n".join(f"line-{number}" for number in range(1, 501)), encoding="utf-8")
    (workspace / "link.py").symlink_to(source)
    monkeypatch.setattr(groq_actor, "WORKSPACE", workspace)

    page = json.loads(
        groq_actor.dispatch(
            "read_file",
            json.dumps({"path": "engine.py", "line_start": 200, "line_end": 400}),
        )
    )

    assert page["line_start"] == 200
    assert page["line_end"] == 400
    assert page["content"].splitlines()[0] == "200: line-200"
    assert page["content"].splitlines()[-1] == "400: line-400"
    with pytest.raises(ValueError, match="at most"):
        groq_actor.read_file("engine.py", 1, groq_actor.MAX_PAGE_LINES + 1)
    with pytest.raises(ValueError, match="1-based"):
        groq_actor.read_file("engine.py", 0, 1)
    with pytest.raises(ValueError, match="regular workspace file"):
        groq_actor.read_file("link.py", 1, 2)
    with pytest.raises(ValueError, match="safe workspace-relative"):
        groq_actor.read_file("../engine.py", 1, 2)


def test_bounded_search_matches_generated_gpt_oss_call_and_preserves_isolation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    source = workspace / "packages" / "analytics" / "src" / "policy_analytics" / "discovery"
    source.mkdir(parents=True)
    engine = source / "engine.py"
    engine.write_text("x = 1\ndef _eligible(value):\n    return value\n", encoding="utf-8")
    (source / "link.py").symlink_to(engine)
    monkeypatch.setattr(groq_actor, "WORKSPACE", workspace)

    result = json.loads(
        groq_actor.dispatch(
            "search",
            json.dumps(
                {
                    "path": "packages/analytics/src/policy_analytics/discovery",
                    "query": "def _eligible",
                }
            ),
        )
    )

    assert result["matches"] == [
        {
            "path": "packages/analytics/src/policy_analytics/discovery/engine.py",
            "line": 2,
            "text": "def _eligible(value):",
        }
    ]
    assert result["files_scanned"] == 1
    with pytest.raises(ValueError, match="safe workspace-relative"):
        groq_actor.search("../discovery", "eligible")
    with pytest.raises(ValueError, match="non-symlink"):
        groq_actor.search("packages/analytics/src/policy_analytics/discovery/link.py", "eligible")
    with pytest.raises(ValueError, match="between"):
        groq_actor.search("packages", "eligible", groq_actor.MAX_SEARCH_MATCHES + 1)


def test_actor_rejects_unapproved_output(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = tmp_path / "workspace"
    output = workspace / "output"
    output.mkdir(parents=True)
    monkeypatch.setattr(groq_actor, "WORKSPACE", workspace)
    monkeypatch.setattr(groq_actor, "OUTPUT", output)

    with pytest.raises(RuntimeError, match="unapproved output"):
        groq_actor.run_python("from pathlib import Path; Path('output/extra.txt').write_text('x')")


def test_http_error_body_is_safe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "gsk-sensitive-value")
    message = groq_actor.safe_http_error(
        401, "authorization Bearer gsk-sensitive-value; key=gsk-sensitive-value\ninvalid request"
    )
    assert message == (
        "Groq HTTP 401: authorization Bearer [REDACTED]; key=[REDACTED] invalid request"
    )
    assert "gsk-sensitive-value" not in message


def test_provider_request_is_bounded_and_retries_429(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "test-only")
    headers = Message()
    headers["Retry-After"] = "0"
    rate_limit = urllib.error.HTTPError(
        "https://api.groq.com/openai/v1/chat/completions",
        429,
        "rate limited",
        headers,
        BytesIO(b'{"error":{"message":"wait"}}'),
    )
    requests: list[urllib.request.Request] = []

    class Response:
        def __enter__(self) -> Response:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"choices":[{"message":{"role":"assistant","content":"ok"}}]}'

    attempts = iter([rate_limit, Response()])

    def fake_urlopen(request: urllib.request.Request, timeout: int) -> Response:
        assert timeout == 180
        requests.append(request)
        outcome = next(attempts)
        if isinstance(outcome, urllib.error.HTTPError):
            raise outcome
        return outcome

    sleeps: list[float] = []
    monkeypatch.setattr(groq_actor.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(groq_actor.time, "sleep", sleeps.append)
    messages = [{"role": "user", "content": "x" * 30_000}]

    result = groq_actor.provider_completion("test-model", messages)

    assert result["choices"]
    assert sleeps == [0.0]
    assert len(requests) == 2
    request = requests[-1]
    data = request.data
    assert isinstance(data, bytes)
    payload = json.loads(data)
    assert payload["max_completion_tokens"] == groq_actor.MAX_COMPLETION_TOKENS
    assert len(json.dumps(payload["messages"])) <= groq_actor.MAX_CONTEXT_CHARS
    assert request.get_header("User-agent") == groq_actor.USER_AGENT


def test_provider_classifies_tool_use_failed_as_recoverable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "test-only")
    error = urllib.error.HTTPError(
        "https://api.groq.com/openai/v1/chat/completions",
        400,
        "bad request",
        Message(),
        BytesIO(b'{"error":{"code":"tool_use_failed","message":"bad tool"}}'),
    )

    def fake_urlopen(_request: urllib.request.Request, timeout: int) -> None:
        assert timeout == 180
        raise error

    monkeypatch.setattr(groq_actor.urllib.request, "urlopen", fake_urlopen)

    with pytest.raises(groq_actor.ToolUseFailedError, match="tool_use_failed"):
        groq_actor.provider_completion("test-model", [{"role": "user", "content": "go"}])


def test_actor_loop_uses_tools_until_all_artifacts_exist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    output = workspace / "output"
    output.mkdir(parents=True)
    (workspace / "public.txt").write_text("allowlisted", encoding="utf-8")
    monkeypatch.setattr(groq_actor, "WORKSPACE", workspace)
    monkeypatch.setattr(groq_actor, "OUTPUT", output)
    monkeypatch.setenv("GROQ_API_KEY", "test-only")
    responses = iter(
        [
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": "list-1",
                                    "type": "function",
                                    "function": {
                                        "name": "list_workspace",
                                        "arguments": "{}",
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": "read-1",
                                    "type": "function",
                                    "function": {
                                        "name": "read_file",
                                        "arguments": json.dumps({"path": "public.txt"}),
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": "python-1",
                                    "type": "function",
                                    "function": {
                                        "name": "run_python",
                                        "arguments": json.dumps(
                                            {
                                                "code": (
                                                    "from pathlib import Path; import json; "
                                                    "out=Path('output'); "
                                                    "(out/'candidates.json').write_text('{}'); "
                                                    "(out/'discovery_metrics.json')"
                                                    ".write_text('{}'); "
                                                    "(out/'run_report.md').write_text('report')"
                                                )
                                            }
                                        ),
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
            {"choices": [{"message": {"role": "assistant", "content": "done"}}]},
        ]
    )

    def fake_completion(
        _model: str,
        _messages: list[dict[str, Any]],
        _tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return next(responses)

    monkeypatch.setattr(groq_actor, "provider_completion", fake_completion)

    groq_actor.run("test-model")

    assert {path.name for path in output.iterdir()} == groq_actor.OUTPUT_NAMES


def test_actor_recovers_from_tool_use_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "workspace"
    output = workspace / "output"
    output.mkdir(parents=True)
    monkeypatch.setattr(groq_actor, "WORKSPACE", workspace)
    monkeypatch.setattr(groq_actor, "OUTPUT", output)
    monkeypatch.setenv("GROQ_API_KEY", "test-only")
    responses: list[object] = [
        groq_actor.ToolUseFailedError("Groq HTTP 400: tool_use_failed"),
        {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": "python-1",
                                "type": "function",
                                "function": {
                                    "name": "run_python",
                                    "arguments": json.dumps(
                                        {
                                            "code": (
                                                "from pathlib import Path; out=Path('output'); "
                                                "(out/'candidates.json').write_text('{}'); "
                                                "(out/'discovery_metrics.json').write_text('{}'); "
                                                "(out/'run_report.md').write_text('report')"
                                            )
                                        }
                                    ),
                                },
                            }
                        ],
                    }
                }
            ]
        },
        {"choices": [{"message": {"role": "assistant", "content": "done"}}]},
    ]
    seen_messages: list[list[dict[str, Any]]] = []

    def fake_completion(
        _model: str,
        messages: list[dict[str, Any]],
        _tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        seen_messages.append(messages)
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        assert isinstance(response, dict)
        return cast(dict[str, Any], response)

    monkeypatch.setattr(groq_actor, "provider_completion", fake_completion)

    groq_actor.run("test-model")

    assert any(
        "Available tools: list_workspace, read_file, search, run_python" in message["content"]
        for messages in seen_messages
        for message in messages
        if message.get("role") == "user"
    )
