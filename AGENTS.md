# AGENTS.md — oeis_validator

## Overview

Validate OEIS draft entries against the internal format specification and style sheet. Parses `.txt` files in OEIS internal format and checks all 19 field tags for compliance, consistency, and style adherence.

## Commands

| Command | Description |
|---------|------------|
| `pytest` | Run test suite |
| `ruff format` | Format code |
| `prospector --with-tool ruff --with-tool mypy src/` | Lint + type check (with blending) |
| `semgrep --config=auto src/` | Security and pattern scanning |
| `vulture --min-confidence 90 src/` | Dead/unused code detection |

## Development

```bash
# Setup
pip install -e ".[test]"

# Test
pytest

# Format
ruff format src/ tests/

# Lint + type check (prospector runs ruff check + mypy together)
prospector --with-tool ruff --with-tool mypy src/
semgrep --config=auto --severity=ERROR src/

# find unused code
vulture --min-confidence 90 src/
```

## Testing

pytest-based suite with 90+ tests covering all validation rules, edge cases (empty input, multi-entry, malformed lines), and CLI modes. Hypothesis property-based tests for data model invariants.

## Code Style

- Format: ruff format
- Lint + Type check: prospector (runs ruff check + mypy with blending)
- Docstrings: Google style

## Release

```bash
# Bump version
bumpversion patch  # or minor/major
git tag v<version>
git push && git push --tags
```
