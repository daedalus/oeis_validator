from __future__ import annotations

import re
from collections import Counter
from collections.abc import Callable, Iterator

from oeis_validator.models import Issue, OEISEntry

WarningFunc = Callable[[str, str], None]

SERVER_KEYWORDS: set[str] = {
    "changed",
    "hear",
}

VALID_KEYWORDS: set[str] = {
    "base",
    "bref",
    "cofr",
    "cons",
    "core",
    "dead",
    "dumb",
    "dupe",
    "easy",
    "eigen",
    "fini",
    "frac",
    "full",
    "hard",
    "less",
    "more",
    "mult",
    "new",
    "nice",
    "nonn",
    "obsc",
    "sign",
    "tabf",
    "tabl",
    "uned",
    "unkn",
    "walk",
    "word",
}

KNOWN_TAGS: set[str] = {
    "I",
    "S",
    "T",
    "U",
    "N",
    "D",
    "H",
    "F",
    "Y",
    "A",
    "O",
    "E",
    "e",
    "p",
    "t",
    "o",
    "K",
    "C",
}

COMMENT_SIG_RE = re.compile(r"-\s+_[^_]+_,\s+\w+ \d{2} \d{4}")
LANG_PREFIX_RE = re.compile(r"^\([A-Za-z][A-Za-z0-9+#\- ]*\)")
ANCHOR_RE = re.compile(
    r"<a\s+href\s*=\s*[\"']?([^\"'>\s]+)[\"']?[^>]*>(.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
BFILE_RE = re.compile(r"[ab]\d{6}\.txt", re.IGNORECASE)
INDEX_URL_RE = re.compile(r"/(index/|wiki/Index)", re.IGNORECASE)

WA_PATTERNS = [
    re.compile(r"\bsum the\b", re.IGNORECASE),
    re.compile(r"\bplot\s+\w+\s+from\b", re.IGNORECASE),
    re.compile(r"\bintegrate\s+\w+\s+(from|over)\b", re.IGNORECASE),
    re.compile(r"\bfactor\s+\d+\b", re.IGNORECASE),
    re.compile(r"\bsolve\s+\w+\s*=", re.IGNORECASE),
]

YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")

STYLE_PATTERNS = [
    (
        re.compile(r"\bcounts the number of\b", re.IGNORECASE),
        "Use 'is the number of' or 'gives the number of', not 'counts the number of'.",
        "W028",
    ),
    (
        re.compile(r"\bbe integer\b(?!\s*\))"),
        "Use 'be an integer' (missing article).",
        "W029",
    ),
    (
        re.compile(r"\bgreater or equal\b", re.IGNORECASE),
        "Use 'greater than or equal to'.",
        "W030",
    ),
    (
        re.compile(r"\bless or equal\b", re.IGNORECASE),
        "Use 'less than or equal to'.",
        "W031",
    ),
    (
        re.compile(r"\bcouples of\b", re.IGNORECASE),
        "Use 'pairs of', not 'couples of'.",
        "W032",
    ),
    (
        re.compile(r"\brespectfully\b", re.IGNORECASE),
        "Use 'respectively', not 'respectfully'.",
        "W033",
    ),
    (
        re.compile(r"\btriplets of\b", re.IGNORECASE),
        "Use 'triples', not 'triplets'.",
        "W034",
    ),
    (
        re.compile(r"\bamount of\b", re.IGNORECASE),
        "Use 'number of' for countable items, not 'amount of'.",
        "W035",
    ),
    (
        re.compile(r"\bfulfills\b", re.IGNORECASE),
        "Use 'satisfies', not 'fulfills'.",
        "W036",
    ),
    (
        re.compile(r"\ballows\s+to\b", re.IGNORECASE),
        "Use 'allows us to' or 'allows one to', not 'allows to'.",
        "W037",
    ),
    (
        re.compile(r"\bExcept\s+(?!(?:for|when|that|if)\b)", re.IGNORECASE),
        "Use 'except for' (missing preposition).",
        "W038",
    ),
    (
        re.compile(r"\bunique\b", re.IGNORECASE),
        "Use 'distinct' for non-identical items, not 'unique'.",
        "W039",
    ),
    (
        re.compile(
            r"\bit's\s+(?:author|name|value|definition|sequence|offset|"
            r"keyword|field|line|term|coefficient|function|property|meaning|"
            r"length|size|sum|product|limit|graph|root|source|origin|status|"
            r"type|form|range|domain|sign)",
            re.IGNORECASE,
        ),
        "Use 'its' (possessive, no apostrophe), not 'it's' (contraction).",
        "W040",
    ),
    (
        re.compile(r"\bp\(n\)(?!\w)"),
        "Use 'prime(n)' or 'partition(n)' instead of p(n) for clarity.",
        "W041",
    ),
]


def _check_style(text: str) -> Iterator[tuple[str, str]]:
    """Check text against known OEIS style guide patterns.

    Args:
        text: The text to scan.

    Yields:
        (message, code) tuples for each style-violation found in the text.
    """
    for pat, msg, code in STYLE_PATTERNS:
        m = pat.search(text)
        if m:
            yield msg, code


def validate(entry: OEISEntry) -> list[Issue]:
    """Run all validation rules against a parsed OEIS entry.

    Checks every field tag that is present in the entry for format compliance,
    internal consistency, and style-sheet adherence.  Severity is:

    - ``ERROR`` — must fix before submission
    - ``WARNING`` — likely mistake
    - ``INFO`` — advisory or convention reminder

    Args:
        entry: A parsed ``OEISEntry`` object.

    Returns:
        A list of ``Issue`` objects, one per detected problem.
        Returns an empty list when the entry is clean.
    """
    issues: list[Issue] = []

    def err(f: str, msg: str, code: str = "") -> None:
        issues.append(Issue("ERROR", f, msg, code))

    def warn(f: str, msg: str, code: str = "") -> None:
        issues.append(Issue("WARNING", f, msg, code))

    def info(f: str, msg: str, code: str = "") -> None:
        issues.append(Issue("INFO", f, msg, code))

    kw = set(entry.keywords)

    # ---- %I ----------------------------------------------------------------
    if "I" not in entry.fields:
        err("%I", "Identification line (%I) is required.", "E001")
    if entry.a_number is None:
        err("%I", "Could not parse a valid A-number (Annnnnn).", "E002")
    elif not re.fullmatch(r"A\d{6}", entry.a_number):
        err("%I", f"A-number '{entry.a_number}' must be exactly A + 6 digits.", "E003")

    if "I" in entry.fields:
        for mn in re.findall(r"\b[MN]\d+\b", entry.fields["I"][0]):
            if len(mn[1:]) > 4:
                warn("%I", f"Legacy {mn[0]}-number '{mn}' has more than 4 digits.", "W001")

    # ---- %S/%T/%U ----------------------------------------------------------
    if "S" not in entry.fields:
        err("%S", "First sequence line (%S) is required.", "E004")
    else:
        raw_s = entry.fields["S"][0]
        if "\t" in raw_s:
            err("%S", "Tabs are not allowed in sequence data.", "E005")
        for _tag, _lines in (
            ("S", entry.fields.get("S", [])),
            ("T", entry.fields.get("T", [])),
            ("U", entry.fields.get("U", [])),
        ):
            for _line in _lines:
                if re.search(r",[ \t]+", _line):
                    warn(
                        f"%{_tag}",
                        "Terms should be separated by commas with no spaces.",
                        "W002",
                    )

        bad = [t for t in entry.sequence_terms if not re.fullmatch(r"-?\d+", t)]
        for t in bad:
            err("%S/%T/%U", f"Non-integer term: '{t}'.", "E006")

        if len(entry.sequence_terms) < 4:
            err(
                "%S/%T/%U",
                f"At least 4 terms required; found {len(entry.sequence_terms)}.",
                "E007",
            )

        data_chars = len(",".join(entry.sequence_terms))
        if data_chars < 260 and len(entry.sequence_terms) >= 4:
            info(
                "%S/%T/%U",
                f"Only {data_chars} chars of data. "
                "OEIS recommends ~260 chars (~3 screen lines).",
                "I001",
            )

        for _tag in ("S", "T", "U"):
            if len(entry.fields.get(_tag, [])) > 1:
                warn(
                    f"%{_tag}",
                    f"Multiple %{_tag} lines found — "
                    "each data tag must appear at most once.",
                    "W003",
                )

        si = entry.sequence_ints
        if len(si) >= 6:
            if all(si[i] == 0 for i in range(1, len(si), 2)):
                info(
                    "%S/%T/%U",
                    "Every 2nd, 4th, 6th, ... term is zero — "
                    "OEIS convention omits them.",
                    "I002",
                )
            elif all(si[i] == 0 for i in range(0, len(si), 2)):
                info(
                    "%S/%T/%U",
                    "Every 1st, 3rd, 5th, ... term is zero — "
                    "OEIS convention omits them.",
                    "I003",
                )

    # ---- %N ----------------------------------------------------------------
    if "N" not in entry.fields:
        err("%N", "Name line (%N) is required.", "E008")
    else:
        if len(entry.fields["N"]) > 1:
            err("%N", "Only one %N line is allowed.", "E009")
        name = entry.name or ""
        if not name:
            err("%N", "Name must not be empty.", "E010")
        else:
            if name[-1] not in ".!?":
                warn(
                    "%N",
                    "Name should end with a period (or other appropriate punctuation).",
                    "W004",
                )
            if re.search(r"\b(I|my|our)\b", name):
                warn("%N", "Avoid first-person language in the name.", "W005")
            if re.search(r"\ba_\d\b|a\[n\]", name):
                warn("%N", "Use a(n) notation in the name, not a_n or a[n].", "W006")
            if re.match(r"^The number of\b", name, re.IGNORECASE):
                info(
                    "%N",
                    "Consider omitting 'The number of' prefix "
                    "when obvious from context.",
                    "I004",
                )
            for msg, code in _check_style(name):
                warn("%N", msg, code)

    # ---- %O ----------------------------------------------------------------
    if "O" not in entry.fields:
        err("%O", "Offset line (%O) is required.", "E011")
    else:
        raw_o = entry.fields["O"][-1]
        if "," not in raw_o:
            warn(
                "%O",
                "Offset should be 'a,b': index of first term, "
                "then pos of first |term|>=2.",
                "W007",
            )
        if entry.offset_a is None:
            err("%O", "Could not parse offset 'a' as an integer.", "E012")

        if entry.offset_b is not None and entry.sequence_ints:
            expected_b = 1
            for idx, val in enumerate(entry.sequence_ints, 1):
                if abs(val) >= 2:
                    expected_b = idx
                    break
            if expected_b != entry.offset_b:
                warn(
                    "%O",
                    f"Offset b={entry.offset_b} looks wrong; "
                    f"first |term|>=2 is at 1-based position {expected_b}.",
                    "W008",
                )

        if "cofr" in kw and entry.offset_a is not None and entry.offset_a != 0:
            warn("%O", "Continued fractions ('cofr') should normally use offset 0.", "W009")
        if "cons" in kw and entry.offset_a is not None and entry.offset_a not in (0, 1):
            info("%O", "Decimal expansions ('cons') typically use offset 0 or 1.", "I005")

    # ---- %K ----------------------------------------------------------------
    if "K" not in entry.fields:
        err("%K", "Keywords line (%K) is required.", "E013")
    else:
        for k in entry.keywords:
            if k in SERVER_KEYWORDS:
                info("%K", f"Keyword '{k}' is server-managed — do not submit manually.", "I026")
            elif k not in VALID_KEYWORDS:
                warn("%K", f"Unrecognized keyword: '{k}'.", "W010")

        has_nonn = "nonn" in kw
        has_sign = "sign" in kw
        if not has_nonn and not has_sign:
            err("%K", "At least one of 'nonn' or 'sign' is required.", "E014")
        if has_nonn and has_sign:
            err("%K", "'nonn' and 'sign' are mutually exclusive.", "E015")

        if entry.sequence_ints:
            has_neg = any(v < 0 for v in entry.sequence_ints)
            if has_neg and not has_sign:
                err(
                    "%K/%S",
                    "Sequence has negative terms but keyword 'sign' is missing.",
                    "E016",
                )
            if not has_neg and has_sign:
                info(
                    "%K/%S",
                    "Keyword 'sign' set but no negative terms visible in data "
                    "(acceptable if negatives appear later).",
                    "I006",
                )

        if "more" in kw and "full" in kw:
            err("%K", "'more' and 'full' are contradictory keywords.", "E017")

        if "frac" in kw:
            y_text = " ".join(entry.fields.get("Y", []))
            if not re.search(r"A\d{6}", y_text):
                warn(
                    "%K/%Y", "Keyword 'frac': companion sequence must be linked in %Y.",
                    "W011",
                )

        for kw_name, label in (
            ("tabl", "triangle"),
            ("tabf", "irregular array"),
            ("cons", "decimal expansion"),
            ("cofr", "continued fraction"),
        ):
            if kw_name in kw and "e" not in entry.fields:
                info(
                    "%K/%e",
                    f"Keyword '{kw_name}' ({label}) present but no %e example "
                    "field. Convention is to illustrate the structure in %e.",
                    "I007",
                )

        if "dead" in kw or "dupe" in kw:
            info("%K", "Sequence marked as 'dead'/'dupe' — verify this is intentional.", "I008")
        if "base" in kw and "C" not in entry.fields:
            info(
                "%K",
                "Keyword 'base': consider adding a %C comment explaining the base.",
                "I009",
            )
        if "mult" in kw:
            info(
                "%K",
                "Keyword 'mult': ensure a(mn)=a(m)*a(n) for gcd(m,n)=1 is documented.",
                "I010",
            )
        if "fini" in kw and "full" not in kw:
            info(
                "%K",
                "Keyword 'fini' (finite) without 'full': "
                "add 'full' if all terms are given.",
                "I011",
            )
        if "bref" in kw:
            info(
                "%K",
                "Keyword 'bref': sequence is intentionally short — "
                "ensure this is necessary.",
                "I012",
            )

    # ---- %A ----------------------------------------------------------------
    if "A" not in entry.fields:
        err("%A", "Author line (%A) is required.", "E018")
    else:
        author = entry.author or ""
        if not author.strip():
            err("%A", "Author field must not be empty.", "E019")
        elif not re.search(r"[A-Za-z]{2,}", author):
            warn("%A", "Author field does not appear to contain a name.", "W012")
        elif re.search(r"[\w.+\-]+(AT|@)[\w.\-]+", author):
            warn(
                "%A",
                "Author field appears to contain an email address — remove it.",
                "W013",
            )

    # ---- %F ----------------------------------------------------------------
    for formula in entry.fields.get("F", []):
        if re.search(r"a\[n\]", formula):
            warn("%F", "Use a(n) notation, not a[n].", "W014")
        if re.search(r"\bx\b", formula) and not re.search(
            r"\b(G\.f|E\.g\.f|g\.f|e\.g\.f)[\.:]\s*", formula
        ):
            info("%F", "Formula uses 'x' without a G.f./E.g.f. label.", "I013")
        if re.search(r"\b(G\.f|g\.f)[\.:]\s*", formula):
            if re.search(r"\b[Bfgh]\(x\)", formula) and not re.search(
                r"\bA\(x\)", formula
            ):
                info("%F", "G.f. convention: use A(x) for the generating function.", "I014")
        if (
            "cons" in kw
            and "Equals" not in formula
            and re.search(r"=\s*[\d.]+", formula)
        ):
            info(
                "%F",
                "For 'cons' sequences use 'Equals <formula>' to describe the constant.",
                "I015",
            )

    # ---- %H ----------------------------------------------------------------
    h_lines = entry.fields.get("H", [])
    for i, link in enumerate(h_lines):
        if not link:
            continue
        if "http" in link.lower() or "www." in link.lower():
            if not re.search(r"<a\s+href\s*=", link, re.IGNORECASE):
                warn(
                    "%H", f"URL must be wrapped in <a href=...>Title</a>: {link[:100]}",
                    "W015",
                )
        anchors = ANCHOR_RE.findall(link)
        if anchors:
            url, title = anchors[0]
            if not title.strip():
                warn("%H", f"Anchor has empty title text: {link[:100]}", "W016")
            if url.startswith("http://"):
                info("%H", f"Non-HTTPS URL — consider https://: {url[:80]}", "I016")
        if BFILE_RE.search(link) and i > 0:
            warn("%H", "b-file link should be the first entry in the %H section.", "W017")
        if INDEX_URL_RE.search(link) and i < len(h_lines) - 1:
            rest = h_lines[i + 1 :]
            if any(not INDEX_URL_RE.search(r) for r in rest):
                info(
                    "%H", "Index entries should be the last entries in the %H section.",
                    "I017",
                )

    # ---- %D ----------------------------------------------------------------
    for ref in entry.fields.get("D", []):
        if re.search(r"https?://", ref):
            warn("%D", "URL found in %D — URLs belong in %H (Links).", "W018")
        if re.search(r"\barXiv:\d{4}\.\d+\b", ref, re.IGNORECASE):
            info("%D", "arXiv reference detected — consider also adding a %H link.", "I018")

    # ---- %E ----------------------------------------------------------------
    for ext in entry.fields.get("E", []):
        if re.search(r"https?://", ext):
            warn("%E", "URL found in %E — URLs belong in %H (Links).", "W019")
        if not re.search(r"(?:19|20)\d{2}", ext):
            info("%E", "Extension may be missing a date — use 'Name, Date' format.", "I019")

    # ---- %Y ----------------------------------------------------------------
    all_xref: list[str] = []
    for xref in entry.fields.get("Y", []):
        found = re.findall(r"A\d+", xref)
        for a in found:
            if not re.fullmatch(r"A\d{6}", a):
                warn("%Y", f"'{a}' is not a valid 6-digit A-number.", "W020")
            else:
                all_xref.append(a)
        if re.search(r"A\d{6},A\d{6}", xref):
            warn("%Y", "A-numbers in %Y should be separated by a comma and a space.", "W021")

    for a, cnt in Counter(all_xref).items():
        if cnt > 1:
            warn("%Y", f"{a} appears {cnt} times in %Y — remove duplicates.", "W022")

    # ---- %C ----------------------------------------------------------------
    for comment in entry.fields.get("C", []):
        if comment.count("\n") > 1 and "(Start)" not in comment:
            info("%C", "Multi-line comment may need '(Start)' and '(End)' markers.", "I020")
        if len(comment) > 30:
            if re.search(r"-\s+[A-Z][a-z]", comment) and not COMMENT_SIG_RE.search(
                comment
            ):
                info(
                    "%C",
                    "Comment signature may not match format '- _Name_, Mon DD YYYY'.",
                    "I021",
                )
        for msg, code in _check_style(comment):
            info("%C", msg, code)

    # ---- %e ----------------------------------------------------------------
    if "e" in entry.fields and entry.name:
        stem = (entry.name or "")[:30].lower().strip(".").strip()
        for ex in entry.fields["e"]:
            if stem and stem in ex.lower():
                info(
                    "%e",
                    "Example may restate the definition — "
                    "show 1-3 concrete worked cases.",
                    "I022",
                )

    # ---- %p  Maple ---------------------------------------------------------
    for prog in entry.fields.get("p", []):
        if not re.search(r"#", prog) or not YEAR_RE.search(prog):
            info(
                "%p",
                "Maple program appears unsigned — add '# AuthorName, Date' comment.",
                "I023",
            )

    # ---- %t  Mathematica ---------------------------------------------------
    for prog in entry.fields.get("t", []):
        for pat in WA_PATTERNS:
            if pat.search(prog):
                warn(
                    "%t",
                    "Wolfram Alpha natural-language query detected — "
                    "use formal Mathematica/Wolfram Language syntax.",
                    "W023",
                )
                break
        if not re.search(r"\(\*", prog) or not YEAR_RE.search(prog):
            info(
                "%t",
                "Mathematica program appears unsigned — "
                "add '(* AuthorName, Date *)' comment.",
                "I024",
            )

    # ---- %o  Other programs ------------------------------------------------
    o_lines = entry.fields.get("o", [])
    in_block = False
    for prog in o_lines:
        has_lang = bool(LANG_PREFIX_RE.match(prog))
        if has_lang:
            in_block = True
            has_comment = bool(re.search(r"(#|//|/\*|--|\\\\ |;;|%)", prog))
            if not has_comment or not YEAR_RE.search(prog):
                info("%o", "Program in %o appears to lack a comment/signature.", "I025")
        elif not in_block:
            in_block = True
            warn(
                "%o",
                f"Program in %o must start with a language label, "
                f"e.g. '(PARI)' or '(Python)'. Got: '{prog[:40]}'.",
                "W024",
            )
            has_comment = bool(re.search(r"(#|//|/\*|--|\\\\ |;;|%)", prog))
            if not has_comment or not YEAR_RE.search(prog):
                info("%o", "Program in %o appears to lack a comment/signature.", "I025")

    # ---- global ------------------------------------------------------------
    if any("\t" in raw for raw in entry.raw_lines):
        warn("global", "Tab character(s) found — OEIS format uses spaces, not tabs.", "W025")

    content_tags = {"N", "S", "T", "U", "K", "O"}
    for raw in entry.raw_lines:
        m = re.match(r"^%([A-Za-z])\s+(A\d{6})\s*(.*)", raw.rstrip())
        if not m:
            continue
        tag = m.group(1)
        if tag not in content_tags:
            continue
        content = m.group(3)
        if any(ord(c) > 127 for c in content):
            warn(
                "global",
                f"Non-ASCII character in %{tag} — "
                f"use ASCII only: {content.strip()[:80]}",
                "W026",
            )

    for tag in entry.fields:
        if tag not in KNOWN_TAGS:
            warn(f"%{tag}", f"Unknown field tag '%{tag}'.", "W027")

    return issues
