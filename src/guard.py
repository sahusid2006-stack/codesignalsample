from __future__ import annotations

import subprocess
import sys

ALLOWED_PREFIX = "src/prompts/"


def _run_git_cmd(args: list[str]) -> list[str]:
    result = subprocess.run(["git", *args], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"Git command failed: {' '.join(args)}\n{result.stderr}")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def assert_only_prompt_files_changed() -> None:
    changed = set()
    changed.update(_run_git_cmd(["diff", "--name-only"]))
    changed.update(_run_git_cmd(["diff", "--cached", "--name-only"]))
    changed.update(_run_git_cmd(["ls-files", "--others", "--exclude-standard"]))

    disallowed = sorted(path for path in changed if not path.startswith(ALLOWED_PREFIX))

    if disallowed:
        message = (
            "Guard failed: only files under src/prompts/ may be modified. "
            f"Disallowed changes: {', '.join(disallowed)}"
        )
        print(message, file=sys.stderr)
        raise SystemExit(1)
