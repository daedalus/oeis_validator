from __future__ import annotations

from oeis_validator.models import OEISEntry
from oeis_validator.parser import _make_entry, parse_entries, parse_entry

SINGLE_GOOD = """\
%I A123456
%S A123456 1,1,2,5,14,42,132,429,1430,4862,
%T A123456 16796,58786,208012,742900,2674440
%N A123456 Catalan numbers: a(n) = binomial(2n,n)/(n+1).
%O A123456 0,3
%K A123456 nonn,core,easy
%A A123456 N. J. A. Sloane
"""

MULTI = """\
%I A000001
%S A000001 1,2,3,4,5,6,7,8,9,10
%N A000001 First ten positive integers.
%O A000001 1,4
%K A000001 nonn
%A A000001 Author

%I A000002
%S A000002 2,4,6,8,10,12,14,16,18,20
%N A000002 First ten even numbers.
%O A000002 1,4
%K A000002 nonn
%A A000002 Another Author
"""


class TestParseEntry:
    def test_single_entry(self) -> None:
        entry = parse_entry(SINGLE_GOOD)
        assert entry.a_number == "A123456"
        assert entry.name == "Catalan numbers: a(n) = binomial(2n,n)/(n+1)."
        assert entry.offset_a == 0
        assert entry.offset_b == 3
        assert "nonn" in entry.keywords
        assert "core" in entry.keywords
        assert "easy" in entry.keywords
        assert entry.author == "N. J. A. Sloane"
        assert len(entry.sequence_terms) == 15
        assert entry.sequence_ints[0] == 1
        assert "I" in entry.fields
        assert "S" in entry.fields
        assert "T" in entry.fields
        assert "N" in entry.fields
        assert "O" in entry.fields
        assert "K" in entry.fields
        assert "A" in entry.fields

    def test_empty_input(self) -> None:
        entry = parse_entry("")
        assert isinstance(entry, OEISEntry)
        assert entry.a_number is None
        assert entry.fields == {}

    def test_whitespace_only(self) -> None:
        entry = parse_entry("   \n\n  \n")
        assert isinstance(entry, OEISEntry)
        assert entry.a_number is None

    def test_malformed_lines_skipped(self) -> None:
        text = "garbage\n%%I A123456\n%I A123456 test\n%S A123456 1,2,3,4"
        entry = parse_entry(text)
        assert entry.a_number == "A123456"
        assert entry.fields.get("I") == ["test"]


class TestParseEntries:
    def test_multi_entry(self) -> None:
        entries = parse_entries(MULTI)
        assert len(entries) == 2
        assert entries[0].a_number == "A000001"
        assert entries[1].a_number == "A000002"
        assert entries[0].name == "First ten positive integers."
        assert entries[1].name == "First ten even numbers."

    def test_same_anumber_merged(self) -> None:
        """Lines with the same A-number are treated as one block."""
        text = """\
%I A000001
%S A000001 1,2,3,4
%N A000001 First
%I A000001
%S A000001 5,6,7,8
"""
        entries = parse_entries(text)
        assert len(entries) == 1

    def test_no_tags(self) -> None:
        entries = parse_entries("hello\nworld")
        assert len(entries) == 1

    def test_empty_input(self) -> None:
        entries = parse_entries("")
        assert len(entries) == 1


class TestMakeEntry:
    def test_non_integer_terms_skipped(self) -> None:
        entry = _make_entry(["%S A000001 1,foo,3,4,bar"])
        assert entry.sequence_terms == ["1", "foo", "3", "4", "bar"]
        assert entry.sequence_ints == [1, 3, 4]

    def test_no_sequence_data(self) -> None:
        entry = _make_entry(["%I A000001", "%N A000001 Test"])
        assert entry.sequence_terms == []
        assert entry.sequence_ints == []

    def test_offset_parse(self) -> None:
        entry = _make_entry(["%O A000001 2,5"])
        assert entry.offset_a == 2
        assert entry.offset_b == 5

    def test_offset_single_value(self) -> None:
        entry = _make_entry(["%O A000001 1"])
        assert entry.offset_a == 1
        assert entry.offset_b is None

    def test_offset_non_numeric(self) -> None:
        entry = _make_entry(["%O A000001 abc,def"])
        assert entry.offset_a is None
        assert entry.offset_b is None

    def test_keywords_parsed(self) -> None:
        entry = _make_entry(["%K A000001 nonn,core, NICE ,  tabl  "])
        assert entry.keywords == ["nonn", "core", "nice", "tabl"]

    def test_author_parsed(self) -> None:
        entry = _make_entry(["%A A000001 N. J. A. Sloane"])
        assert entry.author == "N. J. A. Sloane"

    def test_multiple_name_lines_joined(self) -> None:
        entry = _make_entry(
            [
                "%N A000001 First line",
                "%N A000001 second line",
            ]
        )
        assert entry.name == "First line second line"
