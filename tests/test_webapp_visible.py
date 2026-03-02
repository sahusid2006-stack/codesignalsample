from __future__ import annotations

from app import _html_exercise, _html_index


def test_index_page_render() -> None:
    html = _html_index()
    assert "Prompt Engineering Assessment Simulator" in html
    assert "Level 1" in html


def test_exercise_page_render() -> None:
    html = _html_exercise("L1-E1")
    assert "L1-E1" in html
    assert "Save Prompt" in html
