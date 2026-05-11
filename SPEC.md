# SPEC.md — oeis_validator

## Purpose

Validate OEIS (On-Line Encyclopedia of Integer Sequences) draft `.txt` entries against the internal format specification and the OEIS style sheet. Catches formatting errors, missing required fields, contradictory keywords, style violations, and data inconsistencies before submission.

## Scope

### What IS in scope
- Single-entry and multi-entry `.txt` files in OEIS internal format
- All 19 field tags: `%I`, `%S`, `%T`, `%U`, `%N`, `%D`, `%H`, `%F`, `%Y`, `%C`, `%e`, `%p`, `%t`, `%o`, `%K`, `%O`, `%A`, `%E`
- Keyword validation (30 recognized keywords)
- Sequence data integrity (integer-only, term count, offset consistency)
- Link/anchor structure for `%H` fields
- Style guide patterns in `%N` and `%C`
- Program field conventions (language labels, signatures, dates)
- Non-ASCII detection in core data fields
- Unknown tag detection
- Stdin and file-based input
- Demo mode with built-in good/bad examples
- Coverage table showing which rules are implemented

### What is NOT in scope
- Network reachability checks for URLs or links
- Editorial judgment of mathematical correctness or sequence interest
- NLP-based author ordering for `%D` or `%H`
- Chronological ordering verification of `%C` entries
- Dead code / unused variable detection in program fields
- Binary file or b-file validation

## Public API / Interface

### `models`

```
class Issue:
    level: str          # "ERROR" | "WARNING" | "INFO"
    field: str
    message: str
    def __str__() -> str

class OEISEntry:
    raw_lines: list[str]
    fields: dict[str, list[str]]
    a_number: str | None
    sequence_terms: list[str]
    sequence_ints: list[int]
    name: str | None
    offset_a: int | None
    offset_b: int | None
    keywords: list[str]
    author: str | None
```

### `parser`

```
parse_entries(text: str) -> list[OEISEntry]
    Split text into per-A-number blocks and parse each.
    Invariants: text is UTF-8 encoded OEIS internal format.
    Returns at least one entry even if no valid tags found.

parse_entry(text: str) -> OEISEntry
    Parse a single entry. Delegates to parse_entries and returns the first.
```

### `rules`

```
validate(entry: OEISEntry) -> list[Issue]
    Run all validation rules against a parsed entry.
    Returns a flat list of Issues (errors, warnings, infos).
```

### `reporter`

```
report(entry: OEISEntry, issues: list[Issue]) -> int
    Print human-readable validation report to stdout.
    Returns 1 if any errors, 0 otherwise.

print_coverage() -> None
    Print the rule coverage table showing which rules are implemented vs missing.
```

### `__main__` (CLI)

```
python -m oeis_validator <file.txt>     # validate a file
echo '%I A...' | python -m oeis_validator  # validate from stdin
python -m oeis_validator --demo         # run built-in test suite
python -m oeis_validator --coverage     # print rule coverage table
```

Exit codes:
- 0: validation passed (no errors; warnings/info ok)
- 1: validation failed (one or more errors)
- 2: file not found

## Data Formats

**Input:** OEIS internal format, a line-oriented tagged format. Each line begins with `%X`, a space, an A-number, a space, and content. Tags are single case-sensitive letters. Example:
```
%I A000010 M0299 N0111
%S A000010 1,1,2,2,4,2,6,4,6,4
%N A000010 Euler totient function phi(n)
%K A000010 nonn,core,mult
%O A000010 1,3
%A A000010 _N. J. A. Sloane_
```

**Output:** Human-readable validation report written to stdout with error/warning/info levels and per-field attribution.

## Edge Cases

1. **Empty input** — zero-length string produces a single entry with no fields, errors for all required tags.
2. **Multi-entry file** — file with multiple A-number blocks; each is validated independently.
3. **Malformed lines** — lines not matching `%X Annnnnn content` are silently skipped.
4. **No sequence data** — missing `%S` reports an error; `%T`/`%U` without `%S` are not separately required.
5. **Offset b mismatch** — `offset_b` claims the first term with |value|≥2 is at position X, but data shows otherwise.
6. **Both `nonn` and `sign`** — mutually exclusive keywords; error raised.
7. **Negative data without `sign` keyword** — error if any term < 0 and `sign` absent.
8. **Contradictory keywords** — `more` and `full` simultaneously.
9. **Tabs anywhere** — tab characters are not valid in the internal format.
10. **Non-ASCII in core fields** — characters > U+007F in `%N`, `%S`, `%T`, `%U`, `%K`, `%O` are flagged.
11. **Unknown field tag** — any tag not in the known 19-tag set produces a warning.
12. **Self-closing anchors** — `<a href=...></a>` with empty title text.
13. **Program without language label** — `%o` lines must start with `(LANG)`.
14. **Wolfram Alpha queries in Mathematica** — natural-language patterns like "sum the" in `%t`.
15. **Duplicate A-numbers in `%Y`** — same A-number listed more than once in cross-references.

## Performance & Constraints

- Pure stdlib — no third-party dependencies.
- Must handle files up to ~1 MB without excessive memory (streaming line-by-line internally).
- All regex patterns are compiled at module load time.
- Validation must complete in < 1 second for typical single-entry files.
