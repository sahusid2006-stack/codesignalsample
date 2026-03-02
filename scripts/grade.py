from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.guard import assert_only_prompt_files_changed


FAILED_RE = re.compile(r"^FAILED\s+([^\s]+)", re.MULTILINE)


def _run_pytest(args: list[str], include_hidden: bool = False) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    if include_hidden:
        env["INCLUDE_HIDDEN"] = "1"
    result = subprocess.run(["pytest", *args], capture_output=True, text=True, check=False, env=env, cwd=ROOT)
    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    sys.stdout.write(output)
    return result.returncode, output


def _collect_failures(outputs: Iterable[str]) -> list[str]:
    failures: set[str] = set()
    for out in outputs:
        for match in FAILED_RE.findall(out):
            failures.add(match)
    return sorted(failures)


def main() -> int:
    assert_only_prompt_files_changed()

    visible_code, visible_out = _run_pytest(["-q", "tests/test_*_visible.py"])
    all_code, all_out = _run_pytest(["-q", "tests", "tests/hidden"], include_hidden=True)

    if visible_code == 0 and all_code == 0:
        print("PASS")
        return 0

    failing = _collect_failures([visible_out, all_out])
    if failing:
        print(f"FAIL {', '.join(failing)}")
    else:
        print("FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
