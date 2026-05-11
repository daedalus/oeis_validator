from __future__ import annotations

import pytest

from oeis_validator.models import OEISEntry
from oeis_validator.parser import parse_entry
from oeis_validator.rules import validate

GOOD_ENTRY = """\
%I A000001
%S A000001 1,1,2,5,14,42,132,429,1430,4862
%N A000001 Test sequence: a(n) = n.
%O A000001 1,3
%K A000001 nonn
%A A000001 Test Author
"""


def entry_from_text(text: str) -> OEISEntry:
    return parse_entry(text)


def test_clean_entry() -> None:
    issues = validate(entry_from_text(GOOD_ENTRY))
    errors = [i for i in issues if i.level == "ERROR"]
    assert len(errors) == 0


@pytest.mark.parametrize(
    "text, expected_error_field",
    [
        ("%S A000001 1,2,3,4\n%O A000001 1,3\n%K A000001 nonn\n%A A000001 Test", "%I"),
        ("%I A000001\n%O A000001 1,3\n%K A000001 nonn\n%A A000001 Test", "%S"),
        ("%I A000001\n%S A000001 1,2,3,4\n%K A000001 nonn\n%A A000001 Test", "%N"),
        (
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%K A000001 nonn\n%A A000001 Test",
            "%O",
        ),
        (
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,3\n%A A000001 Test",
            "%K",
        ),
        (
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,3\n%K A000001 nonn",
            "%A",
        ),
    ],
)
def test_each_required_field_missing(text: str, expected_error_field: str) -> None:
    issues = validate(entry_from_text(text))
    errors = [
        i for i in issues if i.level == "ERROR" and i.field == expected_error_field
    ]
    assert len(errors) >= 1, f"Expected error in field {expected_error_field}"


class TestDataField:
    def test_fewer_than_4_terms(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3\n%N A000001 Test\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("4 terms" in i.message for i in errs)

    def test_tabs_in_data(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1\t2,3,4,5\n%N A000001 Test\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("Tabs" in i.message for i in errs)

    def test_non_integer_term(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,foo,3,4,5\n%N A000001 Test\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("Non-integer" in i.message for i in errs)

    def test_multiple_S_lines(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%S A000001 5,6,7,8\n%N A000001 Test\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("Multiple %S" in i.message for i in warns)


class TestNameField:
    def test_no_punctuation(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 No punctuation\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("punctuation" in i.message for i in warns)

    def test_multiple_N_lines(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 First\n%N A000001 Second\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("Only one %N" in i.message for i in errs)

    def test_first_person(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 I found this sequence\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("first-person" in i.message for i in warns)

    def test_a_n_notation(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 a_0 = n\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("a(n)" in i.message for i in warns)

    def test_a_bracket_n_notation(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 a[n] = n\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("a(n)" in i.message for i in warns)


class TestKeywordField:
    def test_unrecognized_keyword(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn,fakeword\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("Unrecognized" in i.message for i in warns)

    def test_nonnn_and_sign_both(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn,sign\n%A A000001 Auth"
        )
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("mutually exclusive" in i.message for i in errs)

    def test_neither_nonn_nor_sign(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 core\n%A A000001 Auth"
        )
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("nonn' or 'sign" in i.message for i in errs)

    def test_negative_without_sign(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 -1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("negative" in i.message for i in errs)

    def test_more_and_full_contradictory(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn,more,full\n%A A000001 Auth"
        )
        errs = [i for i in validate(e) if i.level == "ERROR"]
        assert any("contradictory" in i.message for i in errs)


class TestOffsetField:
    def test_offset_b_mismatch(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,-1,3,4,5\n%N A000001 Test.\n%O A000001 1,99\n%K A000001 sign\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("offset b" in i.message or "looks wrong" in i.message for i in warns)

    def test_offset_no_comma(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("Offset should" in i.message or "a,b" in i.message for i in warns)


class TestAuthorField:
    def test_email_only(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4,5\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 user@example.com"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("email" in i.message for i in warns)


class TestFormulaField:
    def test_a_n_notation_in_formula(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n%F A000001 a[n] = n"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("a[n]" in i.message for i in warns)


class TestLinkField:
    def test_url_without_anchor(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn"
            "\n%A A000001 Auth\n%H A000001 http://example.com"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("URL must" in i.message for i in warns)

    def test_empty_anchor(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn"
            '\n%A A000001 Auth\n%H A000001 <a href="http://example.com"></a>'
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("empty title" in i.message for i in warns)


class TestProgramField:
    def test_o_missing_language_label(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn"
            "\n%A A000001 Auth\n%o A000001 print('hello')"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("language label" in i.message for i in warns)

    def test_t_wolfram_alpha_pattern(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn"
            "\n%A A000001 Auth\n%t A000001 sum the series"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("Wolfram Alpha" in i.message for i in warns)


class TestNonASCII:
    def test_non_ascii_in_name(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Séquencé\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("Non-ASCII" in i.message for i in warns)

    def test_non_ascii_in_seq_data(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth\n"
            "%U A000001 caf\u00e9,5"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        non_ascii = [w for w in warns if "Non-ASCII" in w.message]
        assert len(non_ascii) > 0

    def test_non_ascii_in_keywords(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn,na\u00efve\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        non_ascii = [w for w in warns if "Non-ASCII" in w.message]
        assert len(non_ascii) > 0

    def test_non_ascii_in_offset(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,\u00a02\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        non_ascii = [w for w in warns if "Non-ASCII" in w.message]
        assert len(non_ascii) > 0

    def test_non_ascii_in_author_ok(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 "
            "Ren\u00e9 Descartes"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        non_ascii = [w for w in warns if "Non-ASCII" in w.message]
        assert len(non_ascii) == 0


class TestGlobal:
    def test_unknown_tag(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn"
            "\n%A A000001 Auth\n%Z A000001 test"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("Unknown field" in i.message for i in warns)

    def test_tabs_anywhere(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001\tAuth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("Tab character" in i.message for i in warns)


class TestStyle:
    def test_counts_the_number_of(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Counts the number of primes.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("counts" in i.message for i in warns)

    def test_greater_or_equal(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Values greater or equal to 2.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("greater than or equal" in i.message for i in warns)

    def test_allows_to(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 This allows to compute.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("allows us to" in i.message for i in warns)

    def test_except_missing_for(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Except a(2)=3, all terms are even.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("except for" in i.message for i in warns)

    def test_except_for_ok(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Except for a(2)=3, all terms are even.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert not any("except for" in i.message for i in warns)

    def test_unique_should_be_distinct(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 There are three unique values.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("distinct" in i.message for i in warns)

    def test_its_vs_it_s(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 The sequence and it's author.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("its" in i.message for i in warns)

    def test_p_of_n_ambiguity(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 This is p(n) for n>0.\n%O A000001 1,2\n%K A000001 nonn\n%A A000001 Auth"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("prime(n)" in i.message for i in warns)


class TestCrossReference:
    def test_invalid_a_number(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn"
            "\n%A A000001 Auth\n%Y A000001 A123, A1234567"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        a123_warns = [w for w in warns if "A123" in w.message]
        a4567_warns = [w for w in warns if "A1234567" in w.message]
        assert len(a123_warns) >= 1
        assert len(a4567_warns) >= 1

    def test_duplicate_a_numbers(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn"
            "\n%A A000001 Auth\n%Y A000001 A000001, A000002, A000001"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("duplicate" in i.message for i in warns)


class TestReferenceField:
    def test_url_in_D(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn"
            "\n%A A000001 Auth\n%D A000001 See https://example.com"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("URL" in i.message for i in warns)


class TestExtensionField:
    def test_url_in_E(self) -> None:
        e = entry_from_text(
            "%I A000001\n%S A000001 1,2,3,4\n%N A000001 Test.\n%O A000001 1,2\n%K A000001 nonn"
            "\n%A A000001 Auth\n%E A000001 See https://example.com"
        )
        warns = [i for i in validate(e) if i.level == "WARNING"]
        assert any("URL" in i.message for i in warns)
