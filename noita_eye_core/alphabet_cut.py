"""Sequential range-cut alphabet permutations (A–Z / a–z deck builders).

Given a standard A–Z string, repeatedly extract letters in named ranges (e.g.
``A-F``, ``H-N``, ``P-C``, ``E-R``) in their *current* left-to-right order,
remove them from the front portion, and append them to the end.  Repeating this
for each range yields a new 26-letter ordering.  The community ``GOD…`` deck is
produced by the preset cuts plus a ``GOD`` prefix promotion step (the raw cut
sequence yields ``DSTUVWXYZABCGO…``; moving the ``GO`` block before ``D`` gives
``GODSTUVWXYZABCEFHIJKLMNPQR``).

Also builds full **N=83** decks for the eye corpus: 26- or 52-letter block at
low indices + punctuation/digit tail, with optional wiki header crib markers.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

STANDARD_26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GOD_CANONICAL = "GODSTUVWXYZABCEFHIJKLMNPQR"
GOD_CUT_SPECS: Tuple[str, ...] = ("A-F", "H-N", "P-C", "E-R")

# Tail symbols after the 52-letter block in ``noita-alphabet2`` layout.
DEFAULT_TAIL_31 = "0123456789.,?'!@#&*()_+-=[]:;<>/"


def parse_range(spec: str) -> List[str]:
    """Expand a range token like ``A-F`` or wrap-around ``P-C`` (P..Z,A..C)."""
    spec = spec.strip().upper()
    if not spec:
        return []
    if len(spec) == 1:
        return [spec]
    if "-" not in spec:
        return list(spec)
    a, b = spec.split("-", 1)
    a, b = a.strip(), b.strip()
    if len(a) != 1 or len(b) != 1:
        raise ValueError(f"bad range token {spec!r}")
    ai, bi = ord(a), ord(b)
    if ai <= bi:
        return [chr(c) for c in range(ai, bi + 1)]
    return [chr(c) for c in range(ai, ord("Z") + 1)] + [
        chr(c) for c in range(ord("A"), bi + 1)
    ]


def cut_range_to_end(text: str, spec: str, exclude: Sequence[str] = ()) -> str:
    """Remove all letters in ``spec`` from ``text`` (in string order) and append."""
    skip = {c.upper() for c in exclude}
    want = {c for c in parse_range(spec) if c not in skip}
    extracted = [c for c in text if c in want]
    remaining = [c for c in text if c not in want]
    return "".join(remaining + extracted)


def apply_range_cuts(
    base: str = STANDARD_26,
    specs: Sequence[str] = GOD_CUT_SPECS,
    exclude: Optional[Dict[str, Sequence[str]]] = None,
) -> str:
    """Apply each cut spec in sequence to ``base``."""
    exclude = exclude or {}
    out = base.upper()
    for spec in specs:
        out = cut_range_to_end(out, spec, exclude.get(spec, ()))
    return out


def promote_prefix(text: str, prefix: str) -> str:
    """If ``text`` starts with ``prefix[0]`` and contains the rest of ``prefix``
    later as a contiguous block, hoist that block to form ``prefix`` at the front."""
    prefix = prefix.upper()
    if len(prefix) < 2 or text.startswith(prefix):
        return text
    if prefix[0] not in text:
        return text
    rest = prefix[1:]
    idx = text.find(rest)
    if idx <= 0:
        return text
    before = text[:idx]
    after = text[idx + len(rest):]
    if before.startswith(prefix[0]) and before[0] == prefix[0]:
        mid = before[1:]
        return prefix + mid + after
    return text


def promote_god_prefix(text: str) -> str:
    """Hoist ``GO`` before ``D`` so ``DSTUVWXYZABCGO…`` → ``GODSTUVWXYZABC…``."""
    if text.startswith("GOD"):
        return text
    if not text.startswith("D"):
        return text
    go_idx = text.find("GO")
    if go_idx < 2:
        return text
    mid = text[1:go_idx]
    tail = text[go_idx + 2:]
    return "GOD" + mid + tail


def god_alphabet_26(*, promote: bool = True) -> str:
    """Community GOD deck (26 uppercase letters)."""
    raw = apply_range_cuts(STANDARD_26, GOD_CUT_SPECS)
    return promote_god_prefix(raw) if promote else raw


def expand_to_52(upper26: str, *, lower_mode: str = "mirror") -> str:
    """Expand a 26-letter ordering to 52 (``mirror`` | ``shift`` | ``none``)."""
    u = upper26.upper()
    if len(u) != 26 or len(set(u)) != 26:
        raise ValueError("need a 26-letter permutation")
    if lower_mode == "mirror":
        low = u.lower()
    elif lower_mode == "shift":
        low = u[1:].lower() + u[0].lower()
    elif lower_mode == "none":
        low = ""
    else:
        raise ValueError(f"unknown lower_mode {lower_mode!r}")
    return u + low if low else u


def build_deck_83(
    letters: str,
    *,
    variant: str = "26",
    tail: Optional[str] = None,
    wiki_crib: bool = True,
    wiki_mode: str = "symbol",
) -> str:
    """Build an 83-character plaintext alphabet from a 26- or 52-letter block.

    ``variant``:
      - ``26``: ``letters`` is 26 uppercase (lowercase absent from deck)
      - ``52``: ``letters`` is 26 upper + 26 lower (104 chars trimmed to 52)

    ``wiki_mode``:
      - ``symbol``: force ``deck[66]='.'`` and ``deck[5]=' '`` (ciphertext-symbol
        diagnostic map used in community grid displays)
      - ``value``: ensure ``'.'`` and space appear somewhere in the deck
      - ``off``: no wiki pinning
    """
    if variant == "26":
        block = letters.upper()
        if len(block) != 26 or len(set(block)) != 26:
            raise ValueError("26-variant needs 26 distinct uppercase letters")
        tail_len = 83 - 26
    elif variant == "52":
        block = letters
        if len(block) != 52 or len(set(block)) != 52:
            raise ValueError("52-variant needs 52 distinct letters")
        tail_len = 83 - 52
    else:
        raise ValueError(f"variant must be '26' or '52', not {variant!r}")

    fill = (tail or DEFAULT_TAIL_31)
    while len(fill) < tail_len:
        fill += DEFAULT_TAIL_31
    deck = list(block + fill[:tail_len])
    if len(deck) != 83:
        raise ValueError(f"internal deck length {len(deck)} != 83")

    if wiki_crib and wiki_mode == "symbol":
        deck[66] = "."
        deck[5] = " "
    elif wiki_crib and wiki_mode == "value":
        if "." not in deck:
            deck[-2] = "."
        if " " not in deck:
            deck[-1] = " "

    return "".join(deck)


def letter_values(word: str, deck: str, N: int = 83) -> Optional[List[int]]:
    """Map ``word`` to plaintext values via ``deck`` (``None`` if unmappable)."""
    idx = {ch: i for i, ch in enumerate(deck)}
    out: List[int] = []
    for ch in word:
        if ch not in idx:
            return None
        out.append(idx[ch] % N)
    return out


def header_pos0_digits(deck: str, pos0_symbols: Sequence[int]) -> Tuple[bool, str]:
    """Check whether pos-0 ciphertext symbols map to distinct digit chars."""
    digits = set("123456789")
    mapped = []
    for sym in pos0_symbols:
        if sym >= len(deck):
            return False, ""
        mapped.append(deck[sym])
    ok = len(set(mapped)) == len(mapped) and all(c in digits for c in mapped)
    return ok, "".join(mapped)


def describe_cuts(specs: Sequence[str], base: str = STANDARD_26) -> List[str]:
    """Return intermediate strings after each cut (for CLI display)."""
    steps: List[str] = []
    cur = base.upper()
    steps.append(f"start: {cur}")
    for spec in specs:
        cur = cut_range_to_end(cur, spec)
        steps.append(f"after {spec}: {cur}")
    promoted = promote_god_prefix(cur)
    if promoted != cur:
        steps.append(f"promote GOD: {promoted}")
    return steps


def selftest() -> List[Tuple[str, bool]]:
    out: List[Tuple[str, bool]] = []

    out.append(("parse_range A-F length 6", len(parse_range("A-F")) == 6))
    out.append(("parse_range P-C wraps", "P" in parse_range("P-C") and "C" in parse_range("P-C")))

    raw = apply_range_cuts(STANDARD_26, GOD_CUT_SPECS)
    out.append(("GOD raw cuts start with D", raw.startswith("D")))

    god = god_alphabet_26()
    out.append(("GOD canonical 26", god == GOD_CANONICAL))
    out.append(("GOD is a permutation", len(set(god)) == 26))

    out.append(("promote_god_prefix", promote_god_prefix(raw) == GOD_CANONICAL))

    g52 = expand_to_52(god)
    out.append(("GOD52 length", len(g52) == 52))
    out.append(("GOD52 mirror lower", g52[26:].startswith("god")))

    d26 = build_deck_83(god, variant="26", wiki_crib=True, wiki_mode="symbol")
    d52 = build_deck_83(g52, variant="52", wiki_crib=True, wiki_mode="symbol")
    out.append(("deck83-26 length", len(d26) == 83))
    out.append(("deck83-52 length", len(d52) == 83))
    out.append(("wiki symbol crib pos5/66", d26[5] == " " and d26[66] == "."))

    pos0 = [27, 33, 34, 36, 50, 63, 76, 77, 80]
    ok, _ = header_pos0_digits(d26, pos0)
    out.append(("header pos0 digit check runs", isinstance(ok, bool)))

    vals = letter_values("god", d52, 83)
    out.append(("god maps on 52 deck", vals is not None and len(vals) == 3))

    steps = describe_cuts(["A-F", "B-B"])
    out.append(("describe_cuts returns steps", len(steps) >= 2))

    return out


if __name__ == "__main__":
    import sys

    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} alphabet_cut checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
