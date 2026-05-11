from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from oeis_validator.models import Issue, OEISEntry


class TestIssue:
    def test_str_format(self) -> None:
        issue = Issue("ERROR", "%N", "Name is required.")
        assert str(issue) == "[ERROR] %N: Name is required."

    def test_str_warning(self) -> None:
        issue = Issue("WARNING", "%K", "Unrecognized keyword: 'foo'.")
        assert str(issue) == "[WARNING] %K: Unrecognized keyword: 'foo'."

    def test_str_info(self) -> None:
        issue = Issue("INFO", "global", "Consider adding more data.")
        assert str(issue) == "[INFO] global: Consider adding more data."


class TestOEISEntry:
    def test_defaults(self) -> None:
        entry = OEISEntry(raw_lines=[])
        assert entry.raw_lines == []
        assert entry.fields == {}
        assert entry.a_number is None
        assert entry.sequence_terms == []
        assert entry.sequence_ints == []
        assert entry.name is None
        assert entry.offset_a is None
        assert entry.offset_b is None
        assert entry.keywords == []
        assert entry.author is None

    def test_minimal_entry(self) -> None:
        entry = OEISEntry(
            raw_lines=["%I A123456", "%S A123456 1,2,3,4"],
            fields={"I": ["A123456"], "S": ["1,2,3,4"]},
            a_number="A123456",
            sequence_terms=["1", "2", "3", "4"],
            sequence_ints=[1, 2, 3, 4],
        )
        assert entry.a_number == "A123456"
        assert entry.sequence_ints == [1, 2, 3, 4]


@pytest.mark.parametrize(
    "level, field, message",
    [
        ("ERROR", "%I", "Missing identification line"),
        ("WARNING", "%O", "Suspicious offset"),
        ("INFO", "%K", "Keyword 'mult' advisory"),
    ],
)
def test_issue_parametrized(level: str, field: str, message: str) -> None:
    issue = Issue(level, field, message)
    assert issue.level == level
    assert issue.field == field


@given(st.text(alphabet="AEOIW", min_size=3, max_size=10))
def test_issue_level_random(level: str) -> None:
    issue = Issue(level, "%N", "test")
    assert issue.level == level
    assert issue.field == "%N"
