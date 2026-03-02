from __future__ import annotations

import json
import re

from src.tasks.task2 import solve

EXPECTED_KEYS = {"name", "email", "order_id"}
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
ORD_RE = re.compile(r"\bORD-\d{5}\b")
HASH_RE = re.compile(r"#(\d{5})\b")


def expected_entities(text: str) -> dict[str, str]:
    name = ""
    for pattern in [r"my name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", r"name[:\-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"]:
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            break

    email = ""
    m_email = EMAIL_RE.search(text)
    if m_email:
        email = m_email.group(0)

    order_id = ""
    m_ord = ORD_RE.search(text)
    if m_ord:
        order_id = m_ord.group(0)
    else:
        m_hash = HASH_RE.search(text)
        if m_hash:
            order_id = f"ORD-{m_hash.group(1)}"

    return {"name": name, "email": email, "order_id": order_id}


def assert_schema(output: str) -> dict[str, str]:
    parsed = json.loads(output)
    assert set(parsed.keys()) == EXPECTED_KEYS
    assert all(isinstance(v, str) for v in parsed.values())
    return parsed


def test_task2_visible_cases() -> None:
    cases = [
        "Hi, my name is Alice Johnson. Reach me at alice@example.com about ORD-12345.",
        "name: Bob Stone email bob.stone@company.org order #54321",
        "I forgot my order details. My name is Carla Diaz.",
        "No entities here.",
        "Contact: eva@mail.net. Issue with ORD-77777.",
        "name- David Li, no email, order #88888",
    ]
    for text in cases:
        output = solve(text)
        parsed = assert_schema(output)
        assert parsed == expected_entities(text)
