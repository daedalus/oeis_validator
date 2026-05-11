from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from oeis_validator import __version__
from oeis_validator.models import OEISEntry
from oeis_validator.parser import parse_entry
from oeis_validator.rules import validate

HERE = Path(__file__).parent


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_cli_stdin() -> None:
    text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 nonn\n%A A000001 Auth"
    result = subprocess.run(
        [sys.executable, "-m", "oeis_validator"],
        input=text,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0


def test_cli_stdin_with_errors() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "oeis_validator"],
        input="%I A000001\n%S A000001 1,2,3\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 nonn\n%A A000001 Auth",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 1


def test_cli_demo() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "oeis_validator", "--demo"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert "Demo 1" in result.stdout
    assert "Demo 2" in result.stdout
    assert "Demo 3" in result.stdout


def test_cli_coverage() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "oeis_validator", "--coverage"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert "Coverage:" in result.stdout


def test_cli_file_not_found() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "oeis_validator", "nonexistent.txt"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2


def test_cli_file(tmp_path: Path) -> None:
    text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 nonn\n%A A000001 Auth"
    f = tmp_path / "test.txt"
    f.write_text(text)
    result = subprocess.run(
        [sys.executable, "-m", "oeis_validator", str(f)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0


class TestIntegration:
    """Integration tests — parse + validate real-world sequences."""

    def test_a000010(self) -> None:
        text = """\
%I A000010
%S A000010 1,1,2,2,4,2,6,4,6,4,10,4,12,6,8,8,16,6,18,8,12,10,22,8,20,12,18,12,
%T A000010 28,8,30,16,20,16,24,12,36,18,24,16,40,12,42,20,24,22,46,16,42,20,32,
%U A000010 24,52,18,40,24,36,28,58,16,60,30,36,32,48,20,66,32,44
%N A000010 Euler totient function phi(n): count numbers <= n and prime to n.
%O A000010 1,3
%K A000010 nonn,mult,core
%A A000010 N. J. A. Sloane
"""
        entry = parse_entry(text)
        assert entry.a_number == "A000010"
        issues = validate(entry)
        errors = [i for i in issues if i.level == "ERROR"]
        assert len(errors) == 0

    def test_multi_entry_round_trip(self) -> None:
        multi = """\
%I A000001
%S A000001 1,2,3,4,5,6,7,8,9,10
%N A000001 First.
%O A000001 1,3
%K A000001 nonn
%A A000001 Author

%I A000002
%S A000002 2,4,6,8,10,12,14,16,18,20
%N A000002 Second.
%O A000002 1,3
%K A000002 nonn
%A A000002 Author2
"""
        from oeis_validator.parser import parse_entries

        entries = parse_entries(multi)
        assert len(entries) == 2
        for e in entries:
            errors = [i for i in validate(e) if i.level == "ERROR"]
            assert len(errors) == 0
