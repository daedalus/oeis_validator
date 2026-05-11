from __future__ import annotations

import sys

from oeis_validator.demo import DEMO_BAD, DEMO_GOOD
from oeis_validator.parser import parse_entries, parse_entry
from oeis_validator.reporter import print_coverage, report
from oeis_validator.rules import validate


def main() -> int:
    """CLI entry point for the OEIS validator.

    Usage:
        ``oeis-validator <file.txt>`` — validate a file
        ``echo '%I A...' | oeis-validator`` — validate from stdin
        ``oeis-validator --demo`` — run built-in test suite
        ``oeis-validator --coverage`` — print rule coverage table

    Returns:
        Exit code: 0 for pass (no errors), 1 for failure (errors found),
        2 for file-not-found.
    """
    args = sys.argv[1:]

    if "--coverage" in args:
        print_coverage()
        return 0

    if "--demo" in args:
        print("=== Demo 1: Well-formed entry ===\n")
        report(parse_entry(DEMO_GOOD), validate(parse_entry(DEMO_GOOD)))
        print()
        print("=== Demo 2: Entry with deliberate errors ===\n")
        report(parse_entry(DEMO_BAD), validate(parse_entry(DEMO_BAD)))
        print()
        print("=== Demo 3: Multi-entry file ===\n")
        for e in parse_entries(DEMO_GOOD + "\n" + DEMO_BAD):
            report(e, validate(e))
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
        rc |= report(entry, validate(entry))
        if len(entries) > 1:
            print()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
