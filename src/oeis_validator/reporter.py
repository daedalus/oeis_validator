from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from oeis_validator.models import Issue, OEISEntry

COVERAGE_TABLE: list[tuple[str, str, str]] = [
    ("PARSER", "%I required", "COVERED"),
    ("PARSER", "A-number = A + 6 digits", "COVERED"),
    ("PARSER", "M/N-number format in %I", "COVERED"),
    ("PARSER", "%S required", "COVERED"),
    ("PARSER", "%T/%U optional continuation", "COVERED"),
    ("PARSER", "Max 3 data lines (S,T,U)", "COVERED"),
    ("PARSER", "Terms: commas, no spaces (S/T/U)", "COVERED"),
    ("PARSER", "No tabs in data", "COVERED"),
    ("PARSER", "Terms must be integers", "COVERED"),
    ("PARSER", "At least 4 terms required", "COVERED"),
    ("PARSER", "~260 chars of data recommended", "COVERED"),
    ("PARSER", "Every-other-term zeros advisory", "COVERED"),
    ("PARSER", "Fractions -> frac kw + %Y links", "COVERED"),
    ("PARSER", "Multi-entry file support", "COVERED"),
    ("NAME", "%N required", "COVERED"),
    ("NAME", "Only one %N line", "COVERED"),
    ("NAME", "Must not be empty", "COVERED"),
    ("NAME", "Ends with punctuation", "COVERED"),
    ("NAME", "a(n) notation (not a_n, a[n])", "COVERED"),
    ("NAME", "No first-person language", "COVERED"),
    ("NAME", "'The number of' advisory", "COVERED"),
    ("NAME", "Avoid vanity self-naming", "NOT COVERED (editorial judgment)"),
    ("NAME", "Prefer concise math definitions", "NOT COVERED (stylistic)"),
    ("OFFSET", "%O required", "COVERED"),
    ("OFFSET", "Two-part offset a,b", "COVERED"),
    ("OFFSET", "offset_b cross-checked vs data", "COVERED"),
    ("OFFSET", "cofr -> offset 0", "COVERED"),
    ("OFFSET", "cons -> offset 0 or 1", "COVERED"),
    ("OFFSET", "Don't repeat range in formulas", "NOT COVERED (NLP required)"),
    ("KEYWORDS", "%K required", "COVERED"),
    ("KEYWORDS", "nonn or sign required", "COVERED"),
    ("KEYWORDS", "nonn XOR sign", "COVERED"),
    ("KEYWORDS", "sign when negatives present", "COVERED"),
    ("KEYWORDS", "All 30 valid keywords recognized", "COVERED"),
    ("KEYWORDS", "frac -> %Y cross-reference", "COVERED"),
    ("KEYWORDS", "more XOR full", "COVERED"),
    ("KEYWORDS", "fini -> full advisory", "COVERED"),
    ("KEYWORDS", "tabl/tabf -> %e advisory", "COVERED"),
    ("KEYWORDS", "cons/cofr -> %e advisory", "COVERED"),
    ("KEYWORDS", "dead/dupe advisory", "COVERED"),
    ("KEYWORDS", "base -> %C advisory", "COVERED"),
    ("KEYWORDS", "mult -> documentation advisory", "COVERED"),
    ("KEYWORDS", "bref advisory", "COVERED"),
    ("AUTHOR", "%A required", "COVERED"),
    ("AUTHOR", "Name present (not just email)", "COVERED"),
    ("AUTHOR", "Field not modified after approval", "NOT COVERED (editorial)"),
    ("FORMULA", "a(n) notation", "COVERED"),
    ("FORMULA", "G.f./E.g.f. labeled", "COVERED"),
    ("FORMULA", "A(x) for g.f. variable", "COVERED"),
    ("FORMULA", "cons: Equals formula", "COVERED"),
    ("LINKS", "URLs require <a href=...>", "COVERED"),
    ("LINKS", "Empty anchor title warned", "COVERED"),
    ("LINKS", "http vs https advisory", "COVERED"),
    ("LINKS", "b-file link placed first", "COVERED"),
    ("LINKS", "Index entries placed last", "COVERED"),
    ("LINKS", "Anchor structure validated", "COVERED"),
    ("LINKS", "Alphabetized by author", "NOT COVERED (NLP required)"),
    ("LINKS", "Broken link detection", "NOT COVERED (HTTP required)"),
    ("LINKS", "No hidden-program links", "NOT COVERED (HTTP required)"),
    ("LINKS", "Stable URLs preferred", "NOT COVERED (HTTP required)"),
    ("REFS", "URLs in %D -> move to %H", "COVERED"),
    ("REFS", "arXiv in %D -> add %H link", "COVERED"),
    ("REFS", "Each reference on separate %D line", "COVERED (parser-enforced)"),
    ("REFS", "Alphabetized by author", "NOT COVERED (NLP required)"),
    ("XREF", "6-digit A-numbers in %Y", "COVERED"),
    ("XREF", "Comma+space between A-numbers", "COVERED"),
    ("XREF", "No duplicate A-numbers in %Y", "COVERED"),
    ("XREF", "frac -> %Y links to companion seq", "COVERED"),
    ("COMMENTS", "Multi-paragraph (Start)/(End)", "COVERED"),
    ("COMMENTS", "Signature format: - _Name_, Date", "COVERED"),
    ("COMMENTS", "Chronological ordering", "NOT COVERED (no timestamps)"),
    ("COMMENTS", "Non-author comments signed+dated", "NOT COVERED (no authorship ctx)"),
    ("EXTENSIONS", "%E field parsed (no validation yet)", "COVERED"),
    ("EXTENSIONS", "No URLs in %E", "COVERED"),
    ("EXTENSIONS", "Extension entries dated", "COVERED"),
    ("EXAMPLES", "Don't restate definition", "COVERED"),
    ("EXAMPLES", "tabl/cons/cofr -> show in %e", "COVERED (via %K checks)"),
    ("PROGRAMS", "Language label (LANG) in %o", "COVERED"),
    ("PROGRAMS", "Wolfram Alpha patterns warned", "COVERED"),
    ("PROGRAMS", "Maple program signed/dated (year req.)", "COVERED"),
    ("PROGRAMS", "Mathematica program signed/dated (yr req.)", "COVERED"),
    ("PROGRAMS", "%o program has comment + year", "COVERED"),
    ("PROGRAMS", "Programs self-contained", "NOT COVERED (static analysis)"),
    ("PROGRAMS", "Indentation preserved (2+ spaces)", "NOT COVERED (display only)"),
    ("GLOBAL", "Unknown field tags warned", "COVERED"),
    ("GLOBAL", "Line format: %x Annnnnn content", "COVERED"),
    ("GLOBAL", "Multi-entry file support", "COVERED"),
    ("GLOBAL", "Tabs anywhere", "COVERED"),
    ("GLOBAL", "Non-ASCII in content fields only", "COVERED"),
    ("GLOBAL", "Well-defined / general interest", "NOT COVERED (editorial)"),
    ("STYLE", "'counts the number of' warned", "COVERED"),
    ("STYLE", "'be integer' warned", "COVERED"),
    ("STYLE", "'greater or equal' warned", "COVERED"),
    ("STYLE", "'less or equal' warned", "COVERED"),
    ("STYLE", "'couples of' warned", "COVERED"),
    ("STYLE", "'respectfully' warned", "COVERED"),
    ("STYLE", "'triplets of' warned", "COVERED"),
    ("STYLE", "'amount of' warned", "COVERED"),
    ("STYLE", "'fulfills' warned", "COVERED"),
    ("STYLE", "'allows to' warned", "COVERED"),
    ("STYLE", "'except' (missing for) warned", "COVERED"),
    ("STYLE", "'unique' warned for 'distinct'", "COVERED"),
    ("STYLE", "'its' vs 'it\\'s' warned", "COVERED"),
    ("STYLE", "'p(n)' ambiguity warned", "COVERED"),
    ("STYLE", "Non-ASCII characters rejected", "COVERED"),
]


def report(entry: OEISEntry, issues: list[Issue]) -> int:
    """Print a human-readable validation report to stdout.

    Displays the entry header (name, data preview, offset, keywords),
    then each issue grouped by severity (ERROR, WARNING, INFO), then
    a summary line with counts.

    Args:
        entry: The parsed entry that was validated.
        issues: List of ``Issue`` objects returned by :func:`validate`.

    Returns:
        1 if any errors were found, 0 otherwise.
    """
    errors = [i for i in issues if i.level == "ERROR"]
    warnings = [i for i in issues if i.level == "WARNING"]
    infos = [i for i in issues if i.level == "INFO"]

    anum = entry.a_number or "(unknown)"
    print(f"═══ OEIS Validator v0.1.0 — {anum} ═══")
    if entry.name:
        print(f"    Name    : {entry.name[:90]}")
    preview = ", ".join(entry.sequence_terms[:10])
    if len(entry.sequence_terms) > 10:
        preview += ", ..."
    print(f"    Data    : {preview}")
    print(
        f"    Terms   : {len(entry.sequence_terms)}"
        f"   Offset: {entry.offset_a}"
        f"   Keywords: {', '.join(entry.keywords) or '(none)'}"
    )
    print()

    if not issues:
        print("  \u2713  No issues found.")
    else:
        for i in sorted(
            issues, key=lambda x: ("ERROR" != x.level, "WARNING" != x.level)
        ):
            sym = {"ERROR": "\u2717", "WARNING": "\u26a0", "INFO": "\u2139"}.get(
                i.level, "?"
            )
            print(f"  {sym}  {i}")
        print()
        print(
            f"  Summary: {len(errors)} error(s)  "
            f"{len(warnings)} warning(s)  "
            f"{len(infos)} info(s)"
        )

    return 1 if errors else 0


def print_coverage() -> None:
    """Print the rule coverage table with COVERED / NOT COVERED status.

    Shows every validation rule the project tracks, grouped by category,
    with a final coverage percentage.
    """
    covered = sum(1 for r in COVERAGE_TABLE if r[2].startswith("COVERED"))
    total = len(COVERAGE_TABLE)
    print(f"  {'CATEGORY':<12} {'RULE':<50} STATUS")
    print("  " + "\u2500" * 95)
    for cat, rule, status in COVERAGE_TABLE:
        sym = "\u2713" if status.startswith("COVERED") else "\u2717"
        print(f"  {sym} {cat:<12} {rule:<50} {status}")
    print()
    print(f"  Coverage: {covered}/{total} ({100 * covered // total}%)")
