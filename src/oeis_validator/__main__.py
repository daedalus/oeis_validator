from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from oeis_validator.demo import DEMO_BAD, DEMO_GOOD
from oeis_validator.parser import parse_entries, parse_entry
from oeis_validator.reporter import print_coverage, report
from oeis_validator.rules import validate

if TYPE_CHECKING:
    from oeis_validator.models import Issue


def _filter_issues(
    issues: list[Issue],
    no_error: bool = False,
    no_warning: bool = False,
    no_info: bool = False,
) -> list[Issue]:
    return [
        i
        for i in issues
        if not (no_error and i.level == "ERROR")
        and not (no_warning and i.level == "WARNING")
        and not (no_info and i.level == "INFO")
    ]


def main() -> int:
    """CLI entry point for the OEIS validator.

    Usage:
        ``oeis-validator <file.txt>`` — validate a file
        ``echo '%I A...' | oeis-validator`` — validate from stdin
        ``oeis-validator --demo`` — run built-in test suite
        ``oeis-validator --coverage`` — print rule coverage table
        ``oeis-validator --no-warning file.txt`` — suppress warnings
        ``oeis-validator --no-error --no-info file.txt`` — show warnings only

    Returns:
        Exit code: 0 for pass (no errors after filtering), 1 for failure,
        2 for file-not-found.
    """
    args = sys.argv[1:]
    no_error = "--no-error" in args
    no_warning = "--no-warning" in args
    no_info = "--no-info" in args

    if "--coverage" in args:
        print_coverage()
        return 0

    if "--demo" in args:
        print("=== Demo 1: Well-formed entry ===\n")
        issues = validate(parse_entry(DEMO_GOOD))
        report(parse_entry(DEMO_GOOD), _filter_issues(issues, no_error, no_warning, no_info))
        print()
        print("=== Demo 2: Entry with deliberate errors ===\n")
        issues = validate(parse_entry(DEMO_BAD))
        report(parse_entry(DEMO_BAD), _filter_issues(issues, no_error, no_warning, no_info))
        print()
        print("=== Demo 3: Multi-entry file ===\n")
        for e in parse_entries(DEMO_GOOD + "\n" + DEMO_BAD):
            issues = validate(e)
            report(e, _filter_issues(issues, no_error, no_warning, no_info))
            print()
        return 0

    if args and not args[0].startswith("-"):
        try:
            with open(args[0], encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            print(f"File not found: {args[0]}", file=sys.stderr)
            return 2
    else:
        if sys.stdin.isatty():
            print(__doc__)
            return 0
        text = sys.stdin.read()

    entries = parse_entries(text)
    rc = 0
    for entry in entries:
        issues = validate(entry)
        filtered = _filter_issues(issues, no_error, no_warning, no_info)
        rc |= report(entry, filtered)
        if len(entries) > 1:
            print()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
