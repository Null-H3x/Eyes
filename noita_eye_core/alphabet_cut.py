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


def describe_cuts_detailed(
    specs: Sequence[str],
    base: str = STANDARD_26,
    *,
    promote_god: bool = False,
    promote: Optional[str] = None,
) -> List[dict]:
    """Structured cut steps for API / HTML."""
    rows: List[dict] = []
    cur = base.upper()
    rows.append({"step": "start", "label": "start", "alphabet_26": cur})
    for spec in specs:
        cur = cut_range_to_end(cur, spec)
        rows.append({"step": spec, "label": f"after {spec}", "alphabet_26": cur})
    if promote_god:
        nxt = promote_god_prefix(cur)
        if nxt != cur:
            cur = nxt
            rows.append({"step": "promote_god", "label": "promote GOD", "alphabet_26": cur})
    elif promote:
        nxt = promote_prefix(cur, promote)
        if nxt != cur:
            cur = nxt
            rows.append({"step": f"promote_{promote}", "label": f"promote {promote.upper()}",
                         "alphabet_26": cur})
    return rows


def missing_chars(phrase: str, deck: str) -> List[str]:
    """Characters in ``phrase`` absent from ``deck``."""
    have = set(deck)
    return [ch for ch in phrase if ch not in have]


def analyze_phrase(
    phrase: str,
    upper26: str,
    *,
    lower_mode: str = "mirror",
    wiki_crib: bool = True,
    wiki_mode: str = "symbol",
) -> dict:
    """Check whether ``phrase`` maps on 26- / 52- / 83-deck embeddings."""
    u = upper26.upper()
    deck26 = build_deck_83(u, variant="26", wiki_crib=wiki_crib, wiki_mode=wiki_mode)
    g52 = expand_to_52(u, lower_mode=lower_mode)
    deck52 = build_deck_83(g52, variant="52", wiki_crib=wiki_crib, wiki_mode=wiki_mode)

    def _pack(label: str, deck: str, variant: str) -> dict:
        miss = missing_chars(phrase, deck)
        vals = letter_values(phrase, deck, 83)
        return {
            "variant": variant,
            "viable": vals is not None,
            "missing": miss,
            "values": vals,
            "deck_len": len(deck),
        }

    v26 = _pack("26", deck26, "26")
    v52 = _pack("52", deck52, "52")

    recommended = None
    if v52["viable"]:
        recommended = "52"
    elif v26["viable"]:
        recommended = "26"
    elif phrase and phrase == phrase.upper() and all(c.isalpha() for c in phrase):
        recommended = "26"
    else:
        recommended = "52" if any(c.islower() for c in phrase if c.isalpha()) else "26"

    return {
        "phrase": phrase,
        "recommended_variant": recommended,
        "v26": v26,
        "v52": v52,
        "needs_lowercase": any(c.islower() for c in phrase if c.isalpha()),
        "needs_uppercase_only": not any(c.islower() for c in phrase if c.isalpha()),
    }


def build_recipe(
    specs: Sequence[str],
    *,
    base: str = STANDARD_26,
    promote_god: bool = False,
    promote: Optional[str] = None,
    variant: str = "both",
    lower_mode: str = "mirror",
    wiki_crib: bool = True,
    wiki_mode: str = "symbol",
    phrase: str = "",
) -> dict:
    """Full cut-recipe payload for API / HTML."""
    specs = [s.strip() for s in specs if s.strip()]
    rows = describe_cuts_detailed(
        specs, base, promote_god=promote_god, promote=promote)
    upper26 = rows[-1]["alphabet_26"] if rows else base.upper()
    if len(upper26) != 26 or len(set(upper26)) != 26:
        return {
            "ok": False,
            "error": f"cut result is not a 26-letter permutation ({len(set(upper26))} distinct)",
            "steps": rows,
            "specs": list(specs),
        }

    out: dict = {
        "ok": True,
        "specs": list(specs),
        "steps": rows,
        "upper26": upper26,
        "promote_god": promote_god,
        "promote": promote,
        "lower_mode": lower_mode,
        "wiki_crib": wiki_crib,
        "wiki_mode": wiki_mode,
        "variants": {},
    }
    if variant in ("26", "both"):
        d26 = build_deck_83(upper26, variant="26", wiki_crib=wiki_crib, wiki_mode=wiki_mode)
        out["variants"]["26"] = {
            "deck": d26,
            "deck_preview": d26[:52],
            "letter_block": upper26,
        }
    if variant in ("52", "both"):
        g52 = expand_to_52(upper26, lower_mode=lower_mode)
        d52 = build_deck_83(g52, variant="52", wiki_crib=wiki_crib, wiki_mode=wiki_mode)
        out["variants"]["52"] = {
            "deck": d52,
            "deck_preview": d52[:52],
            "letter_block": g52,
        }
    if phrase.strip():
        out["phrase"] = analyze_phrase(
            phrase.strip(), upper26,
            lower_mode=lower_mode,
            wiki_crib=wiki_crib,
            wiki_mode=wiki_mode,
        )
    return out


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

    rec = build_recipe(list(GOD_CUT_SPECS), promote_god=True, phrase="Eyes")
    out.append(("build_recipe GOD + Eyes phrase", rec.get("ok") is True))
    out.append(("Eyes viable on 52 not 26",
                rec["phrase"]["v52"]["viable"] and not rec["phrase"]["v26"]["viable"]))

    return out


if __name__ == "__main__":
    import sys

    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} alphabet_cut checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
