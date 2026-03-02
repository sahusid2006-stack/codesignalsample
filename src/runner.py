from __future__ import annotations

import os
from pathlib import Path

from src.llm_client import complete

PROMPT_DIR = Path("src/prompts")
DEFAULT_MODEL = "claude-3-5-haiku-latest"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_task(task_id: str, input_text: str) -> str:
    model = os.getenv("MODEL", DEFAULT_MODEL)
    system_prompt = _read_text(PROMPT_DIR / "system_prompt.txt")
    user_prompt = _read_text(PROMPT_DIR / f"{task_id}_prompt.txt")
    return complete(system_prompt=system_prompt, user_prompt=user_prompt, input_text=input_text, model=model)
