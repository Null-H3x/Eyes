"""Universal ciphertext import parsing for eye-puzzle datasets.

Accepts arbitrary mixes of:
  * variable-length decimal values (10, 66, 5)
  * single glyph letters/symbols from the 83-rune alphabet
  * optional spacing and punctuation between tokens

One non-empty line = one message (optional ``Label:`` prefix).  Corpus JSON is
detected when the payload starts with ``{``.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from dashboard.cipher_validate import GLYPHS  # noqa: E402

PARSE_CEILING = 256

_GLYPH_INDEX = {ch: i for i, ch in enumerate(GLYPHS)}
_WRAPPER_CHARS = set("[](){}<>\"'`")
# Separators that are never ciphertext symbols in typical pasted data
_PLAIN_SEP = set(" \t\n\r,;|")
# Characters in GLYPHS that may separate numbers when sandwiched between digits
_AMBIG_SEP = set(".:+-=~^/")


@dataclass
class ParseLineResult:
    values: List[int]
    strategy: str
    notes: List[str] = field(default_factory=list)


@dataclass
class ParseImportResult:
    messages: List[List[int]]
    labels: List[str]
    deck_size: int
    detected_format: str
    per_message: List[dict]
    notes: List[str] = field(default_factory=list)


def _validate_value(v: int, *, N: int, strict: bool, context: str) -> int:
    if strict and not (0 <= v < N):
        raise ValueError(f"{context}: value {v} outside [0, {N})")
    return v if strict else v % N


def _try_json_array(text: str, *, N: int, strict: bool) -> Optional[List[int]]:
    text = text.strip()
    if not (text.startswith("[") and text.endswith("]")):
        return None
    try:
        arr = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(arr, list):
        return None
    vals = []
    for item in arr:
        if isinstance(item, int):
            vals.append(_validate_value(int(item), N=N, strict=strict,
                                       context="json array"))
        elif isinstance(item, str) and len(item) == 1 and item in _GLYPH_INDEX:
            vals.append(_GLYPH_INDEX[item])
        else:
            raise ValueError(f"json array item not int/glyph: {item!r}")
    return vals


def _split_glued_digits(text: str, *, N: int, strict: bool) -> List[int]:
    """Greedy longest-prefix parse of a digit-only string into values < N."""
    s = text.strip()
    if not s or not s.isdigit():
        raise ValueError("digit split requires all-digit string")
    out: List[int] = []
    i = 0
    while i < len(s):
        chosen: Optional[Tuple[int, int]] = None
        for j in range(len(s), i, -1):
            v = int(s[i:j])
            if 0 <= v < N:
                chosen = (v, j)
                break
        if chosen is None:
            v = int(s[i])
            out.append(_validate_value(v, N=N, strict=strict,
                                       context="digit split"))
            i += 1
        else:
            out.append(_validate_value(chosen[0], N=N, strict=strict,
                                       context="digit split"))
            i = chosen[1]
    return out


def _is_separator_at(text: str, i: int) -> bool:
    ch = text[i]
    if ch.isspace() or ch in _PLAIN_SEP:
        return True
    if i == 0:
        return False
    prev_digit = text[i - 1].isdigit()
    if not prev_digit:
        return False
    if ch in _AMBIG_SEP:
        return True
    if ch == "-" and i + 1 < len(text) and text[i + 1].isdigit():
        return True
    if ch == "-" and i + 1 < len(text) and not text[i + 1].isdigit():
        return True
    return False


def _stream_scan(text: str, *, N: int, strict: bool) -> List[int]:
    """Scan mixed digits + glyphs with flexible punctuation."""
    vals: List[int] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if _is_separator_at(text, i):
            i += 1
            continue
        if ch in _WRAPPER_CHARS:
            i += 1
            continue

        if ch.isdigit() or (ch == "-" and i + 1 < n and text[i + 1].isdigit()):
            k = i + 1 if ch == "-" else i
            if text[i] == "-":
                k = i + 1
            else:
                k = i
            while k < n and text[k].isdigit():
                k += 1
            num = int(text[i:k])
            vals.append(_validate_value(num, N=N, strict=strict,
                                        context="stream scan"))
            i = k
            continue

        if ch in _GLYPH_INDEX:
            vals.append(_GLYPH_INDEX[ch])
            i += 1
            continue

        raise ValueError(
            f"cannot parse character {ch!r} at position {i} in {text!r}")
    return vals


def _separated_tokens(text: str, *, N: int, strict: bool) -> List[int]:
    """Split on whitespace/punctuation runs, then parse each token."""
    parts = re.split(r"[\s,;|]+", text.strip())
    vals: List[int] = []
    for p in parts:
        if not p:
            continue
        if p.isdigit() or (p.startswith("-") and p[1:].isdigit()):
            v = int(p)
            vals.append(_validate_value(v, N=N, strict=strict,
                                        context=f"token {p!r}"))
        elif len(p) == 1 and p in _GLYPH_INDEX:
            vals.append(_GLYPH_INDEX[p])
        else:
            # Token is glued mix — rescan this token only.
            vals.extend(_stream_scan(p, N=N, strict=strict))
    return vals


def _has_obvious_separators(text: str) -> bool:
    if re.search(r"[\s,;|]", text):
        return True
    for i, ch in enumerate(text):
        if ch in _AMBIG_SEP and i > 0 and text[i - 1].isdigit():
            return True
        if ch == "-" and i > 0 and text[i - 1].isdigit():
            return True
    return False


def _has_letters_or_glyph_punct(text: str) -> bool:
    for ch in text:
        if ch in _GLYPH_INDEX and not ch.isdigit():
            if ch.isalpha() or ch in _AMBIG_SEP or ch in "!@#$%&*<>?.,:;~^|/":
                return True
    return False


def parse_ciphertext_line(
    text: str,
    *,
    N: int = 83,
    strict: bool = True,
) -> ParseLineResult:
    """Parse one message body into ciphertext integers."""
    text = text.strip()
    if not text:
        return ParseLineResult([], "empty", [])

    notes: List[str] = []

    arr = _try_json_array(text, N=N, strict=strict)
    if arr is not None:
        return ParseLineResult(arr, "json_array", notes)

    body = text
    for ch in _WRAPPER_CHARS:
        body = body.strip(ch)

    if body.isdigit():
        whole = int(body)
        if 0 <= whole < N:
            return ParseLineResult([whole], "single_integer", notes)
        vals = _split_glued_digits(body, N=N, strict=strict)
        notes.append(f"split glued digits {body!r} → {len(vals)} symbols")
        return ParseLineResult(vals, "glued_digits", notes)

    if _has_letters_or_glyph_punct(body) or not _has_obvious_separators(body):
        vals = _stream_scan(body, N=N, strict=strict)
        return ParseLineResult(vals, "stream_scan", notes)

    vals = _separated_tokens(body, N=N, strict=strict)
    return ParseLineResult(vals, "separated_tokens", notes)


def _split_label(line: str) -> Tuple[Optional[str], str]:
    line = line.strip()
    if not line:
        return None, ""
    if ":" in line:
        head, rest = line.split(":", 1)
        head = head.strip()
        rest = rest.strip()
        if head and not head.isdigit() and rest:
            # Avoid splitting "10:20:30" style — require label to be non-numeric
            # and rest must contain non-digit or multiple tokens.
            if not re.fullmatch(r"[\d\s,;|.+-]+", head):
                return head, rest
    return None, line


def detect_import_format(content: str) -> str:
    content = content.strip()
    if not content:
        return "empty"
    if content.startswith("{"):
        return "corpus_json"
    return "auto"


def parse_import_content(
    content: str,
    *,
    fmt: str = "auto",
    deck_size: Optional[int] = 83,
    labels: Optional[Sequence[str]] = None,
    strict: bool = True,
) -> ParseImportResult:
    """Parse arbitrary import text into ciphertext messages.

    Pass ``deck_size=None`` to parse with a safe ceiling (256) for unknown N;
    the caller should run ``deck_infer.infer_deck_size`` on the result.
    """
    content = content.strip()
    if not content:
        raise ValueError("empty import")
    unknown_n = deck_size is None
    parse_n = PARSE_CEILING if unknown_n else deck_size
    if parse_n is None or parse_n < 2 or parse_n > PARSE_CEILING:
        raise ValueError(f"deck_size must be in [2, {PARSE_CEILING}] or unknown")

    if fmt == "auto":
        fmt = detect_import_format(content)

    if fmt == "corpus_json":
        raw = json.loads(content)
        N = int(raw.get("deck_size", deck_size or 83))
        if N < 2 or N > PARSE_CEILING:
            raise ValueError(f"deck_size must be in [2, {PARSE_CEILING}]")
        if "ciphertexts" not in raw:
            raise ValueError("corpus JSON missing ciphertexts")
        messages = [list(int(v) for v in ct) for ct in raw["ciphertexts"]]
        lbls = [str(x) for x in raw.get("message_labels", [])]
        if not lbls:
            lbls = [f"Message {i + 1}" for i in range(len(messages))]
        per = [{"strategy": "corpus_json", "count": len(ct), "label": lbls[i]}
               for i, ct in enumerate(messages)]
        return ParseImportResult(
            messages=messages,
            labels=lbls,
            deck_size=N,
            detected_format="corpus_json",
            per_message=per,
            notes=[f"Loaded {len(messages)} message(s) from corpus JSON (N={N})"],
        )

    messages: List[List[int]] = []
    lbls: List[str] = []
    per: List[dict] = []
    msg_num = 0

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        label, body = _split_label(line)
        if not body:
            continue
        parsed = parse_ciphertext_line(body, N=parse_n, strict=strict)
        if not parsed.values:
            continue
        if label:
            lbls.append(label)
        else:
            lbls.append(
                labels[msg_num] if labels and msg_num < len(labels)
                else f"Message {msg_num + 1}")
        messages.append(parsed.values)
        per.append({
            "label": lbls[-1],
            "strategy": parsed.strategy,
            "count": len(parsed.values),
            "notes": parsed.notes,
            "preview": "".join(
                GLYPHS[v] if 0 <= v < len(GLYPHS) else "?"
                for v in parsed.values[:60]),
        })
        msg_num += 1

    if not messages:
        raise ValueError("no messages parsed from import")

    if len(lbls) < len(messages):
        lbls.extend(f"Message {i + 1}" for i in range(len(lbls), len(messages)))

    resolved_n = parse_n
    notes = [f"Parsed {len(messages)} message(s) with universal import parser"]
    if unknown_n:
        notes.append(f"Parsed with unknown N (ceiling={PARSE_CEILING}); infer deck size next")

    return ParseImportResult(
        messages=messages,
        labels=lbls[:len(messages)],
        deck_size=resolved_n,
        detected_format=fmt,
        per_message=per,
        notes=notes,
    )


def selftest() -> List[Tuple[str, bool]]:
    N = 83
    out: List[Tuple[str, bool]] = []

    cases = [
        ("10 20 30", [10, 20, 30]),
        ("10,20;30|40", [10, 20, 30, 40]),
        ("10.20.30", [10, 20, 30]),
        ("10-66-5", [10, 66, 5]),
        ("10665", [10, 66, 5]),
        ("505", [50, 5]),
        ("50", [50]),
        ("o%5", [GLYPHS.index("o"), GLYPHS.index("%"), 5]),
        ("o % 5", [GLYPHS.index("o"), GLYPHS.index("%"), 5]),
        ("o,%,5", [GLYPHS.index("o"), GLYPHS.index("%"), 5]),
        ("10o66", [10, GLYPHS.index("o"), 66]),
        ("10.o%5;66", [10, GLYPHS.index("o"), GLYPHS.index("%"), 5, 66]),
        ("ABC", [GLYPHS.index("A"), GLYPHS.index("B"), GLYPHS.index("C")]),
        ("[1, 2, 3]", [1, 2, 3]),
        ("50o66", [50, GLYPHS.index("o"), 66]),
    ]
    for text, expected in cases:
        got = parse_ciphertext_line(text, N=N).values
        out.append((f"line {text!r}", got == expected))

    multi = parse_import_content(
        "# comment\nEast: 10 20 30\no%5\n10665", deck_size=N)
    out.append(("multi-line import count", len(multi.messages) == 3))
    out.append(("label preserved", multi.labels[0] == "East"))
    out.append(("glued line parsed", multi.messages[2] == [10, 66, 5]))

    try:
        parse_import_content("999 1000", deck_size=N, strict=True)
        out.append(("strict rejects OOR", False))
    except ValueError:
        out.append(("strict rejects OOR", True))

    unk = parse_import_content("10 20 30", deck_size=None)
    out.append(("unknown N uses ceiling", unk.deck_size == PARSE_CEILING))

    return out


if __name__ == "__main__":
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n = sum(1 for _, ok in results if ok)
    print(f"\n{n}/{len(results)} import_parse checks passed")
    sys.exit(0 if n == len(results) else 1)
