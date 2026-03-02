from __future__ import annotations

from app import _html_exercise, _html_index


def test_index_page_render() -> None:
    html = _html_index()
    assert "Prompt Engineering Assessment Simulator" in html
    assert "Level 1" in html
    assert "L4-E10" in html


def test_exercise_page_render_includes_instruction() -> None:
    html = _html_exercise("L1-E01")
    assert "L1-E01" in html
    assert "Save Prompt" in html
    assert "Prompt Instructions" in html
    assert "Extract only the purchase order number" in html
