from __future__ import annotations

from collections import Counter

from src.exercises import EXERCISES


def test_exercise_catalog_has_all_levels_and_counts() -> None:
    counts = Counter(e.level for e in EXERCISES)
    assert counts == {1: 10, 2: 10, 3: 10, 4: 10}


def test_exercise_catalog_ids_unique_and_instructions_present() -> None:
    ids = [e.exercise_id for e in EXERCISES]
    assert len(ids) == len(set(ids))
    assert all(e.instructions.strip() for e in EXERCISES)
    assert all(e.input_text.strip() for e in EXERCISES)
