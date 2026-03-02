from __future__ import annotations

from src.tasks.task1 import solve

VALID = {"BILLING", "BUG", "FEATURE_REQUEST", "OTHER"}


def expected_label(text: str) -> str:
    lower = text.lower()
    billing_terms = ["charge", "charged", "refund", "invoice", "payment", "billing"]
    bug_terms = ["error", "crash", "broken", "bug", "fails", "failing"]
    feature_terms = ["feature", "add", "support", "would love", "could you", "request"]

    if any(t in lower for t in billing_terms):
        return "BILLING"
    if any(t in lower for t in bug_terms):
        return "BUG"
    if any(t in lower for t in feature_terms):
        return "FEATURE_REQUEST"
    return "OTHER"


def assert_valid_output(output: str) -> None:
    assert output in VALID
    assert "\n" not in output
    assert output == output.strip()


def test_task1_visible_cases() -> None:
    cases = [
        "I was charged twice this month. Please issue a refund.",
        "The app crashes every time I open settings.",
        "Could you add dark mode support?",
        "Just saying thanks for your service.",
        "My invoice PDF is missing.",
        "Feature request: add export to CSV.",
    ]
    for text in cases:
        out = solve(text)
        assert_valid_output(out)
        assert out == expected_label(text)
