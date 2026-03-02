from __future__ import annotations

import os
import json
import os
from typing import Any
from urllib import request

from src.cache import get_cached_response, set_cached_response


class LLMClientError(RuntimeError):
    pass


def _extract_text_from_claude(payload: dict[str, Any]) -> str:
    content = payload.get("content", [])
    parts: list[str] = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
    return "".join(parts)


def _claude_complete(system_prompt: str, user_prompt: str, model: str, max_tokens: int = 256) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise LLMClientError("ANTHROPIC_API_KEY is required for Claude API calls.")

    try:
        import anthropic
    except Exception as exc:
        raise LLMClientError(
            "Anthropic SDK is not installed. Run: python -m pip install anthropic"
        ) from exc

    client = anthropic.Anthropic(api_key=api_key)
    try:
        message = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=0.0,
            top_p=1.0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:
        msg = str(exc)
        if "404" in msg or "not_found" in msg.lower():
            raise LLMClientError(
                f"Claude API request failed: {exc}. Check MODEL='{model}' is available to your account."
            ) from exc
        raise LLMClientError(f"Claude API request failed: {exc}") from exc

    content = getattr(message, "content", None)
    if not content:
        raise LLMClientError("Claude response had empty content.")

    texts = []
    for block in content:
        text = getattr(block, "text", None)
        if text is not None:
            texts.append(str(text))
    output = "".join(texts)

    if output == "":
        raise LLMClientError("Claude response did not contain text content.")
    return output
    body = {
        "model": model,
        "system": system_prompt,
        "temperature": 0,
        "top_p": 1,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    req = request.Request(
        url="https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw)
    except Exception as exc:  # network/provider errors
        raise LLMClientError(f"Claude API request failed: {exc}") from exc

    text = _extract_text_from_claude(payload)
    if text == "":
        raise LLMClientError(f"Claude response did not contain text content: {payload}")
    return text


def complete(system_prompt: str, user_prompt: str, input_text: str, model: str) -> str:
    rendered_user_prompt = user_prompt.replace("{INPUT}", input_text)
    cache_enabled = os.getenv("CACHE", "1") != "0"

    if cache_enabled:
        cached = get_cached_response(model, system_prompt, rendered_user_prompt, input_text)
        if cached is not None:
            return cached

    output = _claude_complete(system_prompt=system_prompt, user_prompt=rendered_user_prompt, model=model)

    if cache_enabled:
        set_cached_response(model, system_prompt, rendered_user_prompt, input_text, output)

    return output
