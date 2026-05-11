from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Issue:
    """A single validation finding attached to a specific field.

    Args:
        level: Severity — one of ``"ERROR"``, ``"WARNING"``, or ``"INFO"``.
        field: The tag or section the issue belongs to (e.g. ``"%N"``, ``"global"``).
        message: Human-readable description of the issue.

    Returns:
        Formatted string like ``[ERROR] %N: Name is required.``
    """

    level: str
    field: str
    message: str
    code: str = ""

    def __str__(self) -> str:
        code_part = f" [{self.code}]" if self.code else ""
        return f"[{self.level}]{code_part} {self.field}: {self.message}"


@dataclass
class OEISEntry:
    """Parsed representation of a single OEIS internal-format entry.

    Stores all raw lines plus structured fields extracted during parsing.

    Args:
        raw_lines: Every line belonging to this entry, including blank lines.
        fields: Mapping of tag character (e.g. ``"N"``, ``"S"``) to list of content strings.
        a_number: The A-number (e.g. ``"A000010"``), or ``None`` if not found.
        sequence_terms: Raw string terms split on commas from ``%S``/``%T``/``%U``.
        sequence_ints: Terms successfully parsed as ``int`` (non-integer terms are skipped).
        name: Concatenated ``%N`` content, or ``None``.
        offset_a: First component of ``%O`` (index of first term), or ``None``.
        offset_b: Second component of ``%O`` (position of first term with |value|>=2), or ``None``.
        keywords: Lowercased keyword list from ``%K``, or empty list.
        author: ``%A`` content, or ``None``.
    """

    raw_lines: list[str]
    fields: dict[str, list[str]] = field(default_factory=dict)
    a_number: str | None = None
    sequence_terms: list[str] = field(default_factory=list)
    sequence_ints: list[int] = field(default_factory=list)
    name: str | None = None
    offset_a: int | None = None
    offset_b: int | None = None
    keywords: list[str] = field(default_factory=list)
    author: str | None = None
