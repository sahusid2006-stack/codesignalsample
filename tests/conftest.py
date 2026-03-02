from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def pytest_ignore_collect(collection_path: Path, config) -> bool:  # type: ignore[no-untyped-def]
    include_hidden = os.getenv("INCLUDE_HIDDEN", "0") == "1"
    return "tests/hidden" in str(collection_path).replace("\\", "/") and not include_hidden
