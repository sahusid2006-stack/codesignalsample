from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

CACHE_FILE = Path(".cache/responses.json")


def _cache_key(model: str, system_prompt: str, user_prompt: str, input_text: str) -> str:
    raw = "||".join([model, system_prompt, user_prompt, input_text])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_cache() -> dict[str, str]:
    if not CACHE_FILE.exists():
        return {}
    with CACHE_FILE.open("r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return {}
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


def _save_cache(cache: dict[str, str]) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_FILE.open("w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def get_cached_response(model: str, system_prompt: str, user_prompt: str, input_text: str) -> Optional[str]:
    key = _cache_key(model, system_prompt, user_prompt, input_text)
    cache = _load_cache()
    return cache.get(key)


def set_cached_response(model: str, system_prompt: str, user_prompt: str, input_text: str, output: str) -> None:
    key = _cache_key(model, system_prompt, user_prompt, input_text)
    cache = _load_cache()
    cache[key] = output
    _save_cache(cache)
