# oeis-validator

Validate OEIS entries against the internal format specification and style
sheet. Parses `.txt` files in OEIS internal format and checks all 19 field tags
for compliance, consistency, and style adherence.

[![PyPI](https://img.shields.io/pypi/v/oeis_validator.svg)](https://pypi.org/project/oeis_validator/)
[![Python](https://img.shields.io/pypi/pyversions/oeis_validator.svg)](https://pypi.org/project/oeis_validator/)
[![Coverage](https://img.shields.io/badge/coverage-88%25-brightgreen.svg)](https://github.com/daedalus/oeis_validator)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/master/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-188%20passing-brightgreen.svg)](https://github.com/daedalus/oeis_validator)

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
| A000005 (divisors) | 24 | `%o` |
| A000010 (totient) | 12 | `%o`, `%H` |
| A000040 (primes) | 28 | `%o`, `%D`, `%H`, `%Y` |
| A000041 (partitions) | 50 | `%o`, `%H` |
| A000045 (Fibonacci) | 49 | `%o`, `%H`, `%Y` |
| A000108 (Catalan) | 30 | `%o`, `%H`, `%F` |
| A000203 (sigma) | 16 | `%o`, `%H`, `%Y` |
| A000217 (triangular) | 16 | `%o`, `%Y` |
| A000290 (squares) | 4 | `%o`, `%Y` |
| A001222 (Omega) | 14 | `%o` |

## Development

```bash
git clone https://github.com/daedalus/oeis_validator.git
cd oeis_validator
pip install -e ".[test]"

# run tests (188+ passing)
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

The test suite (`tests/test_adversarial.py`) validates the parser and validator
against 52 adversarial scenarios across six categories:

| Category | Examples |
|---|---|
| **Parser** | Null bytes, BOM, mixed `\r\n`/`\n`, RTL overrides, HTML injection, shell injection, 100-term sequences, negative zero, 50 repeated `%S` lines |
| **Rules** | Mixed valid/invalid keywords, contradictory keyword pairs, offset > sequence length, 100 cross-references with duplicates, fake language labels, URL-free references |
| **Style** | Case-variant pattern matching, false-positive avoidance for `except for`/`its`/`p(n)` in formulas |
| **CLI** | Binary input, empty stdin, large stdin, directory as file, weird filenames, unknown flags, multiple file args |
| **Multi-entry** | 50-entry bulk parse, mixed keyword sets per entry |
| **Regression** | Warning-count snapshots per data file, style-sheet field whitelist |
