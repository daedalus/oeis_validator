from __future__ import annotations

from oeis_validator.models import Issue, OEISEntry
from oeis_validator.reporter import print_coverage, report


def test_report_no_issues(capsys) -> None:
    entry = OEISEntry(raw_lines=[], a_number="A000001")
    rc = report(entry, [])
    captured = capsys.readouterr()
    assert "No issues found" in captured.out
    assert rc == 0


def test_report_with_errors(capsys) -> None:
    entry = OEISEntry(raw_lines=[], a_number="A000001")
    issues = [Issue("ERROR", "%N", "Name required.")]
    rc = report(entry, issues)
    captured = capsys.readouterr()
    assert "Name required" in captured.out
    assert "Summary: 1 error(s)" in captured.out
    assert rc == 1


def test_report_with_warning(capsys) -> None:
    entry = OEISEntry(raw_lines=[], a_number="A000001")
    issues = [Issue("WARNING", "%O", "Suspicious offset.")]
    rc = report(entry, [i for i in issues])
    captured = capsys.readouterr()
    assert "Suspicious offset" in captured.out
    assert rc == 0


def test_report_with_info(capsys) -> None:
    entry = OEISEntry(raw_lines=[], a_number="A000001")
    issues = [Issue("INFO", "%K", "Keyword advisory.")]
    rc = report(entry, issues)
    captured = capsys.readouterr()
    assert "Keyword advisory" in captured.out
    assert rc == 0


def test_report_unknown_anumber(capsys) -> None:
    entry = OEISEntry(raw_lines=[])
    rc = report(entry, [])
    captured = capsys.readouterr()
    assert "(unknown)" in captured.out
    assert rc == 0


def test_report_with_name_preview(capsys) -> None:
    entry = OEISEntry(
        raw_lines=[],
        a_number="A000001",
        name="A very long name that should be truncated at ninety characters "
        "in the report preview to avoid overwhelming the terminal "
        "output of the validator",
    )
    rc = report(entry, [])
    captured = capsys.readouterr()
    assert len(captured.out.split("Name")) > 1
    assert rc == 0


def test_report_with_sequence_preview(capsys) -> None:
    entry = OEISEntry(
        raw_lines=[],
        a_number="A000001",
        sequence_terms=[str(i) for i in range(20)],
    )
    rc = report(entry, [])
    captured = capsys.readouterr()
    assert "..." in captured.out
    assert rc == 0


def test_coverage_output(capsys) -> None:
    print_coverage()
    captured = capsys.readouterr()
    assert "Coverage:" in captured.out
    assert "COVERED" in captured.out
