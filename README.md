# oeis-validator

Validate OEIS entries against the internal format specification and style sheet.

[![PyPI](https://img.shields.io/pypi/v/oeis_validator.svg)](https://pypi.org/project/oeis_validator/)
[![Python](https://img.shields.io/pypi/pyversions/oeis_validator.svg)](https://pypi.org/project/oeis_validator/)
[![Coverage](https://codecov.io/gh/daedalus/oeis_validator/branch/master/graph/badge.svg)](https://codecov.io/gh/daedalus/oeis_validator)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/master/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/daedalus/oeis_validator)

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

# Run built-in demos
oeis-validator --demo

# Show rule coverage
oeis-validator --coverage
```

## API

```python
from oeis_validator import parse_entry, validate, report

entry = parse_entry(text)
issues = validate(entry)
exit_code = report(entry, issues)
```

## Development

```bash
git clone https://github.com/daedalus/oeis_validator.git
cd oeis_validator
pip install -e ".[test]"

# run tests
pytest

# format
ruff format src/ tests/

# lint + type check
prospector --with-tool ruff --with-tool mypy src/
semgrep --config=auto --severity=ERROR src/

# find unused code
vulture --min-confidence 90 src/
```
