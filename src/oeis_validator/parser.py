from __future__ import annotations

import re

from oeis_validator.models import OEISEntry

LINE_RE = re.compile(r"^%([A-Za-z])\s+(A\d{6})\s*(.*)", re.DOTALL)


def _make_entry(lines: list[str]) -> OEISEntry:
    """Parse a block of raw lines into an ``OEISEntry``.

    Iterates over the lines, matches each against ``LINE_RE``, and populates
    all structured fields on the entry object.

    Args:
        lines: Raw text lines belonging to one entry block.

    Returns:
        A fully populated ``OEISEntry``. Fields that could not be parsed
        remain as ``None`` or empty defaults.
    """
    entry = OEISEntry(raw_lines=lines)
    for raw in lines:
        raw = raw.rstrip()
        if not raw:
            continue
        m = LINE_RE.match(raw)
        if not m:
            continue
        tag = m.group(1)
        anum = m.group(2)
        content = m.group(3).strip()
        entry.fields.setdefault(tag, []).append(content)
        if entry.a_number is None:
            entry.a_number = anum

    seq_raw = "".join(
        entry.fields.get("S", [])
        + entry.fields.get("T", [])
        + entry.fields.get("U", [])
    )
    entry.sequence_terms = [t.strip() for t in seq_raw.split(",") if t.strip()]
    for t in entry.sequence_terms:
        try:
            entry.sequence_ints.append(int(t))
        except ValueError:
            pass

    if "N" in entry.fields:
        entry.name = " ".join(entry.fields["N"])

    if "O" in entry.fields:
        parts = entry.fields["O"][-1].split(",")
        try:
            entry.offset_a = int(parts[0].strip())
        except (ValueError, IndexError):
            pass
        try:
            entry.offset_b = int(parts[1].strip())
        except (ValueError, IndexError):
            pass

    if "K" in entry.fields:
        kw_raw = ",".join(entry.fields["K"])
        entry.keywords = [k.strip().lower() for k in kw_raw.split(",") if k.strip()]

    if "A" in entry.fields:
        entry.author = entry.fields["A"][0]

    return entry


def parse_entries(text: str) -> list[OEISEntry]:
    """Split internal-format text into per-A-number blocks and parse each.

    Handles multi-entry files by detecting changes in the A-number between
    consecutive tagged lines.

    Args:
        text: UTF-8 encoded OEIS internal format text.

    Returns:
        A list of ``OEISEntry`` objects, one per block. If no valid tags
        are found, returns a single entry parsed from the entire text.
    """
    lines = text.splitlines()
    blocks: list[list[str]] = []
    current: list[str] = []
    current_anum: str | None = None

    for raw in lines:
        m = LINE_RE.match(raw.rstrip())
        if m:
            anum = m.group(2)
            if current_anum is not None and anum != current_anum:
                blocks.append(current)
                current = []
            current_anum = anum
        current.append(raw)

    if current:
        blocks.append(current)

    if not blocks:
        return [_make_entry(lines)]
    return [_make_entry(b) for b in blocks]


def parse_entry(text: str) -> OEISEntry:
    """Parse a single OEIS internal-format entry.

    Delegates to :func:`parse_entries` and returns the first (or only) entry.

    Args:
        text: UTF-8 encoded OEIS internal format text.

    Returns:
        The first ``OEISEntry`` parsed from the text.
    """
    return parse_entries(text)[0]
