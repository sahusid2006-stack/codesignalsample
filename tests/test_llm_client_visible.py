from __future__ import annotations

import sys
import types

import pytest

from src.llm_client import LLMClientError, _claude_complete


class _FakeBlock:
    def __init__(self, text: str):
        self.text = text


class _FakeMessage:
    def __init__(self, text: str):
        self.content = [_FakeBlock(text)]


class _FakeMessages:
    def create(self, **kwargs):
        return _FakeMessage("OK")


class _FakeAnthropicClient:
    def __init__(self, api_key: str):
        self.messages = _FakeMessages()


class _FakeAnthropicModule:
    Anthropic = _FakeAnthropicClient


def test_claude_complete_uses_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setitem(sys.modules, "anthropic", _FakeAnthropicModule())
    out = _claude_complete(system_prompt="sys", user_prompt="hello", model="claude-3-5-haiku-latest")
    assert out == "OK"


def test_claude_complete_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMClientError):
        _claude_complete(system_prompt="sys", user_prompt="hello", model="claude-3-5-haiku-latest")


def test_claude_complete_model_not_found_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    class _ErrMsgs:
        def create(self, **kwargs):
            raise RuntimeError("HTTP Error 404: Not Found")

    class _ErrClient:
        def __init__(self, api_key: str):
            self.messages = _ErrMsgs()

    mod = types.SimpleNamespace(Anthropic=_ErrClient)
    monkeypatch.setitem(sys.modules, "anthropic", mod)

    with pytest.raises(LLMClientError) as exc:
        _claude_complete(system_prompt="sys", user_prompt="hello", model="bad-model")
    assert "Check MODEL='bad-model'" in str(exc.value)
