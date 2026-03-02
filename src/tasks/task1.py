from __future__ import annotations

from src.runner import run_task

TASK_ID = "task1"


def solve(input_text: str) -> str:
    return run_task(TASK_ID, input_text)
