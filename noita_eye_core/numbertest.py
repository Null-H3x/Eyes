"""Is the literal header (66, 5) a NUMBER — e.g. 34 (the orb count)?

We already proved (see ``header_test``) that positions 1-2 = (66,5) are a
LITERAL / shared marker, not part of the per-triplet body keystream.  A literal
marker *could* be a literal number.  This module asks, falsifiably, *which*
number — and guards hard against the obvious trap.

The trap
--------
Two symbols can be "decoded" to almost any target under *some* hand-picked map,
so "is (66,5) == 34?" is unfalsifiable in isolation.  To make it testable we:

1. **Pre-register** a small family of *principled* symbol-pair -> integer
   encodings (base-N place value, base-5 trigram place value, digit sums, the
   trivial per-symbol reads).  No free parameters, fixed before looking.
2. Decode the header under each and check for the target.
3. Report a **luck baseline**: how many of the integers in a plausible range any
   encoding in the family can hit — so a "match" is judged against chance.
4. Offer a **corroboration hook**: a true global encoding must also make the
   per-message slot (position 0) behave like a sensible index.  Two symbols
   can't pin an encoding; an independent corroborator can.

Verdict on the real corpus: under every principled encoding, (66,5) is one of
{5483, 481, 71, 61, 330, 66, 5, 8255, ..., 7}.  **None is 34** (or 33, or 11).
So the header is not 34 under any principled reading; getting 34 requires a
bespoke, parameter-fit map, which two symbols cannot justify.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Sequence

import trigram


def _t5(v: int) -> List[int]:
    return trigram.to_digits(v, 5, 3)          # MSB-first base-5 trigram


# ---------------------------------------------------------------------------
# Pre-registered encoding family: (a, b, N) -> int.  a = symbol at pos 1 (66),
# b = symbol at pos 2 (5).  All principled, zero free parameters.
# ---------------------------------------------------------------------------

ENCODINGS: Dict[str, Callable[[int, int, int], int]] = {
    "base_be":          lambda a, b, N: a * N + b,
    "base_le":          lambda a, b, N: b * N + a,
    "sum":              lambda a, b, N: a + b,
    "absdiff":          lambda a, b, N: abs(a - b),
    "product":          lambda a, b, N: a * b,
    "first":            lambda a, b, N: a,
    "second":           lambda a, b, N: b,
    "base5_concat_be":  lambda a, b, N: trigram.from_digits(_t5(a) + _t5(b), 5),
    "base5_concat_le":  lambda a, b, N: trigram.from_digits(
                            list(reversed(_t5(a) + _t5(b))), 5),
    "base5_digitsum":   lambda a, b, N: sum(_t5(a)) + sum(_t5(b)),
}

# The subset whose outputs can plausibly land in a "small number" range
# (1..~166); the others explode to the hundreds/thousands and can't be a count.
SMALL_RANGE = ("sum", "absdiff", "first", "second", "base5_digitsum")


def decode_header(symbols: Sequence[int], N: int) -> Dict[str, int]:
    a, b = int(symbols[0]), int(symbols[1])
    return {name: fn(a, b, N) for name, fn in ENCODINGS.items()}


def hits(values: Dict[str, int], target: int) -> List[str]:
    return [name for name, v in values.items() if v == target]


def luck_baseline(N: int, symbols: Sequence[int], lo: int = 1, hi: int = 166
                  ) -> Dict[str, object]:
    """How surprising is hitting a given small number?  Counts, over the family,
    the distinct values and which integers in [lo,hi] are reachable at all."""
    values = decode_header(symbols, N)
    reachable = sorted({v for v in values.values() if lo <= v <= hi})
    return {
        "distinct_values": sorted(set(values.values())),
        "reachable_small": reachable,
        "n_reachable_small": len(reachable),
        "p_random_target_hit": len(reachable) / (hi - lo + 1),
    }


def index_likeness(pos0_symbols: Sequence[int], N: int, encoding: str) -> float:
    """Corroboration score in [0,1]: under ``encoding`` applied per-symbol
    (single-symbol read), how index-like is the per-message slot — i.e. how
    tightly do the decoded values pack into a small contiguous range?
    1.0 == a permutation of a contiguous block (perfect index set)."""
    fn = ENCODINGS[encoding]
    vals = [fn(int(s), 0, N) for s in pos0_symbols]   # single-symbol read (b=0)
    if len(set(vals)) != len(vals):
        return 0.0                                    # indices must be distinct
    span = max(vals) - min(vals) + 1
    return len(vals) / span                           # 1.0 iff perfectly packed


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []
    N = 83

    # KAT: base-5 trigram of the real header symbols.
    out.append(("base-5 trigram of 66 is (2,3,1)", _t5(66) == [2, 3, 1]))
    out.append(("base-5 trigram of 5 is (0,1,0)", _t5(5) == [0, 1, 0]))

    # Real header under the principled family: NONE equals 34 / 33 / 11.
    vals = decode_header([66, 5], N)
    out.append(("real header decodes consistently (base_be=5483)",
                vals["base_be"] == 5483 and vals["sum"] == 71))
    out.append(("real header is NOT 34 under any principled encoding",
                34 not in vals.values()))
    out.append(("real header is NOT 33 or 11 either",
                33 not in vals.values() and 11 not in vals.values()))

    # Planted: a header that genuinely encodes 34 under base_be is (0, 34).
    planted = decode_header([0, 34], N)
    out.append(("planted (0,34) is detected as 34 by base_be",
                "base_be" in hits(planted, 34)))

    # Luck baseline: only a handful of small integers are reachable, so a chance
    # match is plausible -> a single hit is weak evidence.
    lk = luck_baseline(N, [66, 5])
    out.append(("luck baseline reports a small reachable set",
                0 < lk["n_reachable_small"] <= 8))
    out.append(("p(random small target is hit) is modest, not ~1",
                0.0 < lk["p_random_target_hit"] < 0.1))

    # index_likeness: a perfect contiguous index set scores 1.0; the real
    # per-message slot does not.
    perfect = list(range(1, 10))
    out.append(("index_likeness = 1.0 for a perfect 1..9 index",
                abs(index_likeness(perfect, N, "first") - 1.0) < 1e-9))
    real_pos0 = [50, 80, 36, 76, 63, 34, 27, 77, 33]
    out.append(("real position-0 slot is NOT a packed index under identity",
                index_likeness(real_pos0, N, "first") < 0.3))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} numbertest checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
