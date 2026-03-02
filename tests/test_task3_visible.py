from __future__ import annotations

import re

from src.tasks.task3 import solve


def expected_output(payload: str) -> str:
    snippet_match = re.search(r"SNIPPET:\s*(.+)", payload)
    question_match = re.search(r"QUESTION:\s*(.+)", payload)
    assert snippet_match and question_match
    snippet = snippet_match.group(1).strip().strip('"')
    question = question_match.group(1).strip()

    m_ship = re.search(r"When does (.+) ship\?", question)
    if m_ship:
        product = m_ship.group(1)
        m = re.search(rf"{re.escape(product)} ships on ([^.]+)\.", snippet)
        return m.group(1) if m else "UNKNOWN"

    m_capital = re.search(r"What is the capital of (.+)\?", question)
    if m_capital:
        country = m_capital.group(1)
        m = re.search(rf"The capital of {re.escape(country)} is ([^.]+)\.", snippet)
        return m.group(1) if m else "UNKNOWN"

    return "UNKNOWN"


def assert_format(output: str) -> None:
    assert "\n" not in output
    assert output == output.strip()
    assert output != ""


def test_task3_visible_cases() -> None:
    cases = [
        'SNIPPET: "Plan A ships on April 3."\nQUESTION: "When does Plan A ship?"',
        'SNIPPET: "Plan A ships on April 3."\nQUESTION: "When does Plan B ship?"',
        'SNIPPET: "The capital of Peru is Lima."\nQUESTION: "What is the capital of Peru?"',
        'SNIPPET: "The capital of Peru is Lima."\nQUESTION: "What is the capital of Chile?"',
        'SNIPPET: "Nothing useful here."\nQUESTION: "When does Plan A ship?"',
        'SNIPPET: "Widget X ships on June 1."\nQUESTION: "When does Widget X ship?"',
    ]

    for payload in cases:
        output = solve(payload)
        assert_format(output)
        assert output == expected_output(payload)
