# oeis-validator

Validate OEIS entries against the internal format specification and style
sheet. Parses `.txt` files in OEIS internal format and checks all 19 field tags
for compliance, consistency, and style adherence.

[![PyPI](https://img.shields.io/pypi/v/oeis_validator.svg)](https://pypi.org/project/oeis_validator/)
[![Python](https://img.shields.io/pypi/pyversions/oeis_validator.svg)](https://pypi.org/project/oeis_validator/)
[![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen.svg)](https://github.com/daedalus/oeis_validator)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/master/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-221%20passing-brightgreen.svg)](https://github.com/daedalus/oeis_validator)
[![DeepWiki](https://img.shields.io/badge/docs-DeepWiki-blue.svg)](https://deepwiki.com/daedalus/oeis_validator)

## Architecture

The validator operates as a linear pipeline:

```
Raw text → Parser → OEISEntry → Rules Engine → list[Issue] → Reporter → Report
```

- **Parser** (`parser.py`) — identifies OEIS field tags via regex, aggregates multi-line fields, normalizes sequence data into integers
- **Data Models** (`models.py`) — `OEISEntry` holds parsed state (A-number, terms, offsets, keywords); `Issue` represents a single finding with level and code
- **Rules Engine** (`rules.py`) — 90+ checks for structural requirements, keyword logic, style patterns, notation conventions
- **Reporter & CLI** (`reporter.py`, `__main__.py`) — renders issues, handles argument parsing, determines exit code

## Features

- **All 19 field tags** — `%I`, `%S`, `%N`, `%C`, `%D`, `%F`, `%H`, `%I`, `%K`,
  `%L`, `%M`, `%N`, `%O`, `%P`, `%R`, `%S`, `%T`, `%U`, `%Y`
- **30 keyword checks** — validates `%K` against the official keyword list
- **14 style patterns** — catches common OEIS style-sheet violations:
  `counts the number of`, `greater or equal`, `less or equal`, `couples of`,
  `respectfully`, `triplets of`, `amount of`, `fulfills`, `allows to`,
  `except` (missing for), `unique` vs `distinct`, `its` vs `it's`,
  `p(n)` ambiguity, `be integer` (missing article)
- **Non-ASCII detection** — rejects stray Unicode in data/keyword fields
- **Reference cross-checks** — URLs in `%D`, duplicate A-numbers in `%Y`,
  b-file ordering in `%H`, `a_n`/`a[n]` notation in `%F`
- **Program validation** — missing language labels in `%o`, unsigned programs
- **CLI modes** — file input, stdin, `--demo`, `--coverage`
- **Adversarial resilience** — null bytes, BOM, mixed line endings, RTL
  overrides, shell injection attempts, binary input, 50-entry bulk parsing
- **Zero dependencies** — pure Python stdlib

## Install

```bash
pip install oeis-validator
```

## Usage

```bash
# Validate a file
oeis-validator entry.txt

# Validate from stdin
echo '%I A000001 %S A000001 1,1,2,3,5' | oeis-validator

# Run built-in demos (good entry, bad entry, multi-entry)
oeis-validator --demo

# Show rule coverage table
oeis-validator --coverage
```

## API

```python
from oeis_validator import parse_entry, validate, report

entry = parse_entry(text)
issues = validate(entry)
exit_code = report(entry, issues)
```

## Real-world validation

The `data/` directory contains 10 real OEIS sequences fetched from the OEIS
server. The validator produces **0 ERROR-level issues** on all of them. Each
warning is cross-checked against the official style sheet (`.oeis_style_sheet.txt`):

| Sequence | Warnings | Fields warned |
|---|---|---|
| A000005 (divisors) | 0 | — |
| A000010 (totient) | 1 | `%H` |
| A000040 (primes) | 5 | `%o`, `%D`, `%H`, `%Y` |
| A000041 (partitions) | 1 | `%H` |
| A000045 (Fibonacci) | 2 | `%H`, `%Y` |
| A000108 (Catalan) | 1 | `%H` |
| A000203 (sigma) | 5 | `%o`, `%H`, `%Y` |
| A000217 (triangular) | 3 | `%o`, `%Y` |
| A000290 (squares) | 1 | `%Y` |
| A001222 (Omega) | 0 | — |

## Development

```bash
git clone https://github.com/daedalus/oeis_validator.git
cd oeis_validator
pip install -e ".[test]"

# run tests (221+ passing)
pytest -v

# format
ruff format src/ tests/

# lint + type check
prospector --with-tool ruff --with-tool mypy src/
semgrep --config=auto --severity=ERROR src/

# find unused code
vulture --min-confidence 90 src/
```

## Threat model (adversarial tests)

The test suite (`tests/test_adversarial.py`) validates the parser, rules, and
CLI against 85 adversarial scenarios across six categories:

| Category | Tests | Examples |
|---|---|---|
| **Parser** | 28 | Null bytes, BOM, mixed `\r\n`/`\n`, RTL overrides, HTML/shell injection, 100-term sequences, negative zero, 50 repeated `%S` lines, zero-width chars, Unicode normalization, deeply nested parens (5000), 10K-char fields, ASCII art in comments, case-varying tags, invalid tag chars, EOF mid-tag, backslash continuation, whitespace-only fields |
| **Rules** | 23 | Mixed valid/invalid keywords, contradictory keyword pairs, offset > sequence length, 100/500 cross-references with/without duplicates, fake language labels, URL-free refs, all 19 tags stress test, signed programs (no false positive), cons/frac/tabl advisories, bref edge case, self-cross-ref |
| **CLI** | 15 | Binary input, empty/large stdin, directory as file, BOM file, Latin-1 file, empty file, symlinks, unicode filenames, `--` separator, unknown flags |
| **Style** | 9 | Case-variant pattern matching (`AllOwS tO`), false-positive avoidance for `except for`, `its`, `p(n)` in formulas, multiple patterns in one field, patterns in comments |
| **Multi-entry** | 3 | 50-entry bulk parse, mixed keyword sets, blank-line separators |
| **Integration** | 4 | Parse→validate→report pipeline, mixed valid/invalid entries, all 10 data files, 1000-term sequence no-crash |
