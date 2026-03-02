from __future__ import annotations

import os

from src.cache import get_cached_response, set_cached_response


class LLMClientError(RuntimeError):
    pass


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
