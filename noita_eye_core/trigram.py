"""Base-5 trigram substructure decomposition and per-digit statistics.

The corpus comment records that the runes were *sourced from base-5 trigrams*
(``noita-eyes.neocities.org``).  All three tools currently treat each rune as an
opaque integer ``0..82``.  Decomposing a rune into its base-5 digits opens up
per-digit analysis and fractionation/Trifid ciphers that operate on the real
coordinates -- a family none of the tools currently run on the true digits.

Honesty about the math
----------------------
``deck_size = 83`` is **prime**, so the 83-symbol alphabet has *no* non-trivial
internal radix factorisation: you cannot split a uniform ``0..82`` symbol into
independent sub-symbols.  What *is* exact is interpreting each integer in a
chosen radix: every value ``0..82`` fits in three base-5 digits (``5^3 = 125 >
83``), so ``to_digits(v, 5, 3)`` is a well-defined, reversible re-coordinatisation
of the rune.  Whether those digits are *meaningful* depends on the
source-encoding hypothesis being correct -- this module gives you the exact tool
and the per-digit diagnostics to test that hypothesis, and is careful not to
assert it.
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

from stats import ioc


def to_digits(value: int, base: int, ndigits: int) -> List[int]:
    """Most-significant-first digit decomposition.

    ``value == sum(d[i] * base**(ndigits-1-i))``.  Raises if ``value`` does not
    fit in ``ndigits`` base-``base`` digits.
    """
    if base < 2:
        raise ValueError("base must be >= 2")
    if value < 0 or value >= base ** ndigits:
        raise ValueError(f"value {value} does not fit in {ndigits} "
                         f"base-{base} digits (max {base**ndigits - 1})")
    digits = [0] * ndigits
    v = value
    for i in range(ndigits - 1, -1, -1):
        digits[i] = v % base
        v //= base
    return digits


def from_digits(digits: Sequence[int], base: int) -> int:
    v = 0
    for d in digits:
        if not (0 <= d < base):
            raise ValueError(f"digit {d} out of range for base {base}")
        v = v * base + d
    return v


def decompose_sequence(seq: Sequence[int], base: int = 5,
                       ndigits: int = 3) -> List[List[int]]:
    """Return ``ndigits`` parallel digit-streams (MSB-first) for ``seq``."""
    streams: List[List[int]] = [[] for _ in range(ndigits)]
    for v in seq:
        d = to_digits(v, base, ndigits)
        for i in range(ndigits):
            streams[i].append(d[i])
    return streams


def recompose_sequence(streams: Sequence[Sequence[int]], base: int = 5) -> List[int]:
    ndigits = len(streams)
    length = len(streams[0])
    out: List[int] = []
    for t in range(length):
        out.append(from_digits([streams[i][t] for i in range(ndigits)], base))
    return out


def per_digit_ioc(seq: Sequence[int], base: int = 5,
                  ndigits: int = 3) -> List[float]:
    """IoC of each base-``base`` digit stream (MSB-first)."""
    streams = decompose_sequence(seq, base, ndigits)
    return [ioc(s) for s in streams]


def alphabet_fits(values: Sequence[int], base: int, ndigits: int) -> bool:
    cap = base ** ndigits
    return all(0 <= v < cap for v in values)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    out: List[tuple[str, bool]] = []

    # Round-trip every value that fits in base-5 trigrams.
    rt_ok = all(from_digits(to_digits(v, 5, 3), 5) == v for v in range(125))
    out.append(("base-5 trigram round-trip for all 0..124", rt_ok))

    # KAT: 82 = 3*25 + 1*5 + 2 -> digits [3,1,2] (MSB first).
    out.append(("to_digits(82,5,3) == [3,1,2]",
                to_digits(82, 5, 3) == [3, 1, 2]))
    out.append(("from_digits([3,1,2],5) == 82",
                from_digits([3, 1, 2], 5) == 82))

    # Mixed example in another radix.
    out.append(("generic radix round-trip (base 7, 4 digits)",
                from_digits(to_digits(1234, 7, 4), 7) == 1234))

    # All corpus runes fit in base-5 trigrams (since max is 82 < 125).
    out.append(("0..82 all fit base-5 trigrams",
                alphabet_fits(range(83), 5, 3)))

    # Values >= 125 are rejected (no silent truncation).
    try:
        to_digits(125, 5, 3)
        rejected = False
    except ValueError:
        rejected = True
    out.append(("out-of-range value rejected", rejected))

    # Planted-structure detection: digit 2 (LSB) constant, others random ->
    # its per-digit IoC should be 1.0 while the others sit near uniform (1/5).
    import random
    rng = random.Random(11)
    seq = []
    for _ in range(3000):
        d0 = rng.randrange(5)
        d1 = rng.randrange(5)
        d2 = 4  # constant LSB
        seq.append(from_digits([d0, d1, d2], 5))
    iocs = per_digit_ioc(seq, 5, 3)
    out.append(("per-digit IoC flags the constant digit",
                abs(iocs[2] - 1.0) < 1e-9 and iocs[0] < 0.3 and iocs[1] < 0.3))

    # decompose/recompose is the identity on a real corpus-like stream.
    sample = [rng.randrange(83) for _ in range(500)]
    out.append(("decompose/recompose identity",
                recompose_sequence(decompose_sequence(sample, 5, 3), 5)
                == sample))

    # --- edge cases ---------------------------------------------------------
    out.append(("per_digit_ioc returns one value per digit",
                len(per_digit_ioc(sample, 5, 3)) == 3))
    # from_digits rejects an out-of-range digit.
    try:
        from_digits([0, 5, 1], 5)
        digit_rejected = False
    except ValueError:
        digit_rejected = True
    out.append(("from_digits rejects out-of-range digit", digit_rejected))
    # base < 2 rejected.
    try:
        to_digits(3, 1, 3)
        base_rejected = False
    except ValueError:
        base_rejected = True
    out.append(("to_digits rejects base < 2", base_rejected))
    # zero decomposes to all-zero digits.
    out.append(("0 -> all-zero digits", to_digits(0, 5, 3) == [0, 0, 0]))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} trigram checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
