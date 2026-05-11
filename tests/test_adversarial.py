from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from oeis_validator.models import OEISEntry
from oeis_validator.parser import parse_entries, parse_entry
from oeis_validator.rules import validate

BASE = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"


def entry_from_text(text: str) -> OEISEntry:
    return parse_entry(text)


# ==============================================================
# Parser adversarial
# ==============================================================


class TestParserAdversarial:
    def test_null_byte_in_input(self) -> None:
        text = f"\0{BASE}"
        e = entry_from_text(text)
        assert e.a_number == "A000001"

    def test_bom_in_input(self) -> None:
        text = "\ufeff" + BASE
        e = entry_from_text(text)
        assert e.a_number == "A000001"

    def test_mixed_line_endings(self) -> None:
        text = "%I A000001\r\n%S A000001 1,2,3,4,5\r%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\r\n%A A000001 Auth"
        e = entry_from_text(text)
        assert e.a_number == "A000001"

    def test_unidirectional_overrides(self) -> None:
        text = BASE.replace("Test", "Te\u202est\u202e")
        e = entry_from_text(text)
        issues = list(validate(e))
        errors = [i for i in issues if i.level == "ERROR"]
        assert len(errors) == 0

    def test_very_long_a_number(self) -> None:
        text = "%I A0000019999999999\n%S A0000019999999999 1,2,3,4,5\n%N A0000019999999999 Test.\n%O A0000019999999999 1,2\n%K A0000019999999999 nonn\n%A A0000019999999999 Auth"
        e = entry_from_text(text)
        assert e.a_number is not None

    def test_tag_no_space(self) -> None:
        text = "%SA000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        assert e.sequence_terms == []

    def test_html_injection_in_name(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 <script>alert('xss')</script>\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        issues = list(validate(e))
        errors = [i for i in issues if i.level == "ERROR"]
        assert len(errors) == 0  # should parse without crash

    def test_shell_injection_in_field(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%C A000001 `rm -rf /`; $(cat /etc/passwd)"
        e = entry_from_text(text)
        issues = list(validate(e))
        errors = [i for i in issues if i.level == "ERROR"]
        assert len(errors) == 0

    def test_100_sequence_terms(self) -> None:
        terms = ",".join(str(i) for i in range(100))
        text = f"%I A000001\n%S A000001 {terms}\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        assert len(e.sequence_terms) == 100
        assert e.sequence_ints[-1] == 99

    def test_gigantic_term_values(self) -> None:
        huge = 10**100
        text = f"%I A000001\n%S A000001 1,{huge},3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        assert e.sequence_ints[1] == huge

    def test_negative_zero_term(self) -> None:
        text = "%I A000001\n%S A000001 1,-0,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        issues = list(validate(e))
        errs = [i for i in issues if i.level == "ERROR"]
        assert len(errs) == 0

    def test_leading_zeros_in_terms(self) -> None:
        text = "%I A000001\n%S A000001 001,002,003,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        assert e.sequence_ints[0] == 1
        assert e.sequence_ints[2] == 3

    def test_repeated_s_lines(self) -> None:
        lines = ["%I A000001"]
        for i in range(40):
            lines.append(f"%S A000001 {i*5+1},{i*5+2},{i*5+3},{i*5+4},{i*5+5}")
        lines += [
            "%N A000001 Test.",
            "%O A000001 1,2",
            "%K A000001 nonn",
            "%A A000001 Auth",
        ]
        text = "\n".join(lines)
        e = entry_from_text(text)
        assert len(e.sequence_terms) == 200

    def test_wrong_anumber_on_subfields(self) -> None:
        text = "%I A000001\n%S A999999 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        assert e.a_number == "A000001"

    def test_eof_mid_tag(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 T"
        e = entry_from_text(text)
        assert e.name is not None

    def test_backslash_continuation_lines(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 This is a\\\ncontinued name.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        issues = list(validate(e))
        errs = [i for i in issues if i.level == "ERROR"]
        assert len(errs) == 0

    def test_utf8_variable_length(self) -> None:
        text = "%I A000001\n%S A000001 1,\U0001f600,3,4,5\n%N A000001 Test \U0001f600.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("Non-ASCII" in i.message for i in warns)

    def test_empty_data_field(self) -> None:
        text = "%I A000001\n%S A000001 \n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("4 terms" in i.message for i in errs)


# ==============================================================
# Rules adversarial
# ==============================================================


class TestRulesAdversarial:
    def test_all_keywords_mixed_with_invalid(self) -> None:
        all_kw = "nonn,core,easy,more,full,hard,bref,uned,obsc"
        text = f"%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 {all_kw},fakeword,anotherbad\n%A A000001 Auth"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        fake_warns = [w for w in warns if "fakeword" in w.message or "anotherbad" in w.message]
        assert len(fake_warns) == 2

    def test_more_and_full_together(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn,more,full\n%A A000001 Auth"
        e = entry_from_text(text)
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("contradictory" in i.message for i in errs)

    def test_offset_larger_than_sequence(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 100,200\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("offset" in i.message.lower() or "looks wrong" in i.message for i in warns)

    def test_negative_offset(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 -1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert len(errs) == 0  # should not crash

    def test_100_cross_references(self) -> None:
        refs = ", ".join(f"A{i:06d}" for i in range(1, 101))
        text = f"%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%Y A000001 {refs}"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        dup_warns = [w for w in warns if "duplicate" in w.message]
        assert len(dup_warns) == 0  # no duplicates in 1..100

    def test_duplicates_among_100_refs(self) -> None:
        refs = ", ".join(["A000001"] * 50 + ["A000002"] * 50)
        text = f"%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%Y A000001 {refs}"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        dup_warns = [w for w in warns if "duplicate" in w.message]
        assert len(dup_warns) >= 2

    def test_fake_language_label_in_o(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%o A000001 (NOTALANG) some code"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        prog_warns = [w for w in warns if "language label" in w.message]
        assert len(prog_warns) == 0  # (NOTALANG) matches parenthetical pattern

    def test_no_language_label_in_o_valid_program(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%o A000001 (PARI) nxt_prime(100)"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        prog_warns = [w for w in warns if "language label" in w.message]
        assert len(prog_warns) == 0

    def test_style_patterns_not_crashing_on_nonsense(self) -> None:
        nonsense = "\uffff\ufffe" * 50 + " \x00unique "
        text = f"%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 {nonsense}\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        e = entry_from_text(text)
        issues = list(validate(e))
        warns = [i for i in issues if i.level == "WARNING"]
        assert any("Non-ASCII" in i.message or "unique" in i.message for i in warns)

    def test_url_like_text_not_in_d(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%D A000001 No http here"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        d_warns = [w for w in warns if w.field == "%D"]
        assert len(d_warns) == 0

    def test_url_in_e_not_in_h(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%E A000001 See https://example.com"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        e_warns = [w for w in warns if w.field == "%E"]
        assert any("URL" in w.message for w in e_warns)

    def test_all_19_tags_present(self) -> None:
        tags = [
            "%I A000001",
            "%S A000001 1,2,3,4,5",
            "%T A000001 6,7,8,9,10",
            "%U A000001 11,12,13,14,15",
            "%N A000001 All tags present.",
            "%C A000001 A comment.",
            "%D A000001 A reference.",
            "%F A000001 A formula.",
            "%H A000001 A link.",
            "%K A000001 nonn",
            "%L A000001 1,2,3",
            "%M A000001 1",
            "%O A000001 1,2",
            "%P A000001 A pseudo.",
            "%R A000001 A remark.",
            "%Y A000001 A000001",
            "%A A000001 Auth",
            "%o A000001 (PARI) code",
            "%p A000001 # Maple program.",
            "%t A000001 (* Mathematica *)",
        ]
        text = "\n".join(tags)
        e = entry_from_text(text)
        # Should not crash with all tags present
        issues = list(validate(e))
        errs = [i for i in issues if i.level == "ERROR"]
        assert len(errs) == 0, f"Errors: {[(i.field, i.message) for i in errs]}"

    def test_multiple_o_fields_false_positive_language(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%o A000001 (PARI) code\n%o A000001 (Python) code"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        o_warns = [w for w in warns if w.field == "%o"]
        assert len(o_warns) == 0  # both have valid language labels

    def test_signed_program_no_false_warning(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%o A000001 (Python) # Author, Jan 01 2020\n%o A000001 (PARI) \\\\ Author, Jan 01 2020"
        e = entry_from_text(text)
        warns = [i for i in validate(e) if i.level == "WARNING"]
        o_warns = [w for w in warns if w.field == "%o"]
        assert len(o_warns) == 0


# ==============================================================
# CLI adversarial
# ==============================================================


class TestCliAdversarial:
    def test_binary_input(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "oeis_validator"],
            input=b"\x00\x01\x02\xff\xfe\xfd\xfc",
            capture_output=True,
            timeout=10,
        )
        # binary input produces no valid entry → error exit
        assert result.returncode == 1

    def test_empty_stdin(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "oeis_validator"],
            input=b"",
            capture_output=True,
            timeout=10,
        )
        # empty input produces no valid entry → error exit
        assert result.returncode == 1

    def test_very_long_stdin(self) -> None:
        long_data = ("%I A000001\n%S A000001 " + ",".join(str(i) for i in range(10000))
                     + "\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n")
        result = subprocess.run(
            [sys.executable, "-m", "oeis_validator"],
            input=long_data.encode(),
            capture_output=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_directory_as_file(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "oeis_validator", "."],
            capture_output=True,
            timeout=10,
        )
        # directory can't be opened as text file
        assert result.returncode != 0

    def test_missing_file(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "oeis_validator", "/nonexistent/foo.txt"],
            capture_output=True,
            timeout=10,
        )
        assert result.returncode == 2

    def test_file_with_weird_name(self, tmp_path: Path) -> None:
        p = tmp_path / "-test\nfile.txt"
        p.write_text("%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth")
        result = subprocess.run(
            [sys.executable, "-m", "oeis_validator", str(p)],
            capture_output=True,
            timeout=10,
        )
        assert result.returncode == 0

    def test_demo_and_coverage_both(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "oeis_validator", "--demo", "--coverage"],
            capture_output=True,
            timeout=10,
        )
        assert result.returncode == 0

    def test_unknown_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "oeis_validator", "--nonexistent"],
            capture_output=True,
            timeout=10,
        )
        assert result.returncode in (0, 1, 2)

    def test_multiple_file_args(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "oeis_validator", "file1.txt", "file2.txt"],
            capture_output=True,
            timeout=10,
        )
        assert result.returncode in (0, 1, 2)


# ==============================================================
# Style pattern adversarial
# ==============================================================


class TestStylePatternAdversarial:
    @pytest.mark.parametrize(
        "text",
        [
            "This AllOwS tO compute",
            "a function that allows\tto bypass",
        ],
    )
    def test_allows_to_variations(self, text: str) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 " + text + "\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("allows us to" in i.message for i in warns)

    @pytest.mark.parametrize(
        "text",
        [
            "Except for special cases",
            "Except when n=2",
            "Except that it is known",
        ],
    )
    def test_except_ok_variations(self, text: str) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 " + text + "\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert not any("except for" in i.message for i in warns)

    @pytest.mark.parametrize(
        "text",
        [
            "Three UNIQUE terms",
            "Unique values counted",
        ],
    )
    def test_unique_variations(self, text: str) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 " + text + "\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("distinct" in i.message for i in warns)

    def test_its_correct_usage_no_false_warning(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 The sequence and its author.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        its_warns = [w for w in warns if "its" in w.message and "it's" not in w.message.lower()]
        assert len(its_warns) == 0

    def test_p_of_n_not_in_formula(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%F A000001 p(n) = sum_{k=0}^n ...\n%N A000001 Some sequence.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        p_warns = [w for w in warns if "prime(n)" in w.message]
        assert len(p_warns) == 0  # p(n) in formula is fine


# ==============================================================
# Multi-entry adversarial
# ==============================================================


class TestMultiEntryAdversarial:
    def test_50_entries(self) -> None:
        blocks = []
        for i in range(1, 51):
            blocks.append(
                f"%I A{i:06d}\n"
                f"%S A{i:06d} 1,2,3,4,5\n"
                f"%N A{i:06d} Sequence {i}.\n"
                f"%O A{i:06d} 1,2\n"
                f"%K A{i:06d} nonn\n"
                f"%A A{i:06d} Author {i}"
            )
        text = "\n\n".join(blocks)
        entries = parse_entries(text)
        assert len(entries) == 50
        for entry in entries:
            errs = [i for i in validate(entry) if i.level == "ERROR"]
            assert len(errs) == 0

    def test_entries_with_different_keyword_sets(self) -> None:
        text = "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Pos.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n\n%I A000002\n%S A000002 -1,-2,-3,-4,-5\n%N A000002 Neg.\n%O A000002 1,2\n%K A000002 sign\n%A A000002 Auth"
        entries = parse_entries(text)
        assert len(entries) == 2
        assert entries[0].keywords == ["nonn"]
        assert entries[1].keywords == ["sign"]
