from __future__ import annotations

import sys

import pytest

from oeis_validator import __version__
from oeis_validator.demo import DEMO_BAD, DEMO_GOOD
from oeis_validator.models import Issue, OEISEntry
from oeis_validator.parser import parse_entries, parse_entry
from oeis_validator.reporter import report
from oeis_validator.rules import validate


class TestDemo:
    def test_demo_good_nonempty(self) -> None:
        assert len(DEMO_GOOD) > 0

    def test_demo_bad_nonempty(self) -> None:
        assert len(DEMO_BAD) > 0

    def test_demo_good_is_valid_entry(self) -> None:
        entry = parse_entry(DEMO_GOOD)
        assert entry.a_number == "A123456"
        assert entry.name is not None

    def test_demo_bad_has_errors(self) -> None:
        entry = parse_entry(DEMO_BAD)
        issues = validate(entry)
        errors = [i for i in issues if i.level == "ERROR"]
        assert len(errors) > 0


class TestMainCoverage:
    """Direct tests of __main__.main() to increase coverage."""

    def test_main_demo(self) -> None:
        from oeis_validator.__main__ import main

        old_argv = sys.argv
        try:
            sys.argv = ["oeis-validator", "--demo"]
            rc = main()
            assert rc == 0
        finally:
            sys.argv = old_argv

    def test_main_coverage(self) -> None:
        from oeis_validator.__main__ import main

        old_argv = sys.argv
        try:
            sys.argv = ["oeis-validator", "--coverage"]
            rc = main()
            assert rc == 0
        finally:
            sys.argv = old_argv

    def test_main_no_args_no_stdin(self, mocker) -> None:
        from oeis_validator.__main__ import main

        old_argv = sys.argv
        try:
            sys.argv = ["oeis-validator"]
            import io

            mock_stdin = io.StringIO("")
            mocker.patch.object(mock_stdin, "isatty", return_value=True)
            mocker.patch("sys.stdin", mock_stdin)
            rc = main()
            assert rc == 0
        finally:
            sys.argv = old_argv

    def test_main_stdin(self, mocker) -> None:
        from oeis_validator.__main__ import main

        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 nonn\n%A A000001 Auth"
        old_argv = sys.argv
        try:
            sys.argv = ["oeis-validator"]
            import io

            mock_stdin = io.StringIO(text)
            mocker.patch.object(mock_stdin, "isatty", return_value=False)
            mocker.patch("sys.stdin", mock_stdin)
            rc = main()
            assert rc == 0
        finally:
            sys.argv = old_argv

    def test_main_stdin_with_errors(self, mocker) -> None:
        from oeis_validator.__main__ import main

        text = "%I A000001\n%S A000001 1,2,3\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 nonn\n%A A000001 Auth"
        old_argv = sys.argv
        try:
            sys.argv = ["oeis-validator"]
            import io

            mock_stdin = io.StringIO(text)
            mocker.patch.object(mock_stdin, "isatty", return_value=False)
            mocker.patch("sys.stdin", mock_stdin)
            rc = main()
            assert rc == 1
        finally:
            sys.argv = old_argv


class TestAdditionalRuleCoverage:
    """Additional tests targeting uncovered branches in rules.py."""

    def test_cons_keyword_with_offset(self) -> None:
        e = parse_entry(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 cons\n%A A000001 Auth"
        )
        issues = validate(e)
        infos = [i for i in issues if i.level == "INFO"]
        assert any("cons" in i.message for i in infos)

    def test_cofr_keyword_with_offset(self) -> None:
        e = parse_entry(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 cofr\n%A A000001 Auth"
        )
        issues = validate(e)
        warns = [i for i in issues if i.level == "WARNING"]
        assert any("cofr" in i.message.lower() for i in warns)

    def test_every_other_term_zero_info(self) -> None:
        e = parse_entry(
            "%I A000001\n%S A000001 1,0,3,0,5,0,7,0\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 nonn\n%A A000001 Auth"
        )
        issues = validate(e)
        infos = [i for i in issues if i.level == "INFO"]
        assert any("2nd" in i.message for i in infos)

    def test_non_ascii_in_S(self) -> None:
        e = parse_entry(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 nonn\n%A A000001 Auth"
        )
        _ = validate(e)

    def test_report_entry_no_name(self, capsys) -> None:
        entry = OEISEntry(raw_lines=[], a_number="A999999")
        rc = report(entry, [])
        captured = capsys.readouterr()
        assert "A999999" in captured.out
        assert rc == 0

    def test_report_empty_keywords(self, capsys) -> None:
        entry = OEISEntry(
            raw_lines=[], a_number="A000001", keywords=[], sequence_terms=["1", "2"]
        )
        rc = report(entry, [])
        captured = capsys.readouterr()
        assert "(none)" in captured.out
        assert rc == 0
