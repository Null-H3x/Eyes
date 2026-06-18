"""Binary-provenance decoder: how the eye messages are stored in noita.exe.

Per the decompilation guide (kaliuresis), SpawnSecretEyes holds each message as a
list of hard-coded 64-bit integer chunks. Decode = base-7 digits MSB-first, drop
the 0 padding digit, subtract 1 -> base-5 symbols 0..4 with 5 = newline. Base 7
is used so 0 can be a dedicated padding symbol (distinguishing a real leading
symbol-0 from an unfilled 64-bit chunk).

This module holds the decoder + KATs (gateable without the 63 MB decompile). The
full binary->corpus byte-compare lives in eyewitness/binary_provenance.py.
"""
from __future__ import annotations

from typing import List, Tuple


def decode_chunk(v: int) -> str:
    """64-bit chunk -> base-5 symbol string (MSB-first; 0=padding dropped; 5=newline)."""
    if v == 0:
        return ""
    digs = []
    while v > 0:
        digs.append(v % 7)
        v //= 7
    return "".join(str(d - 1) for d in digs[::-1] if d != 0)


def encode_symbols(symbols: str) -> int:
    """Inverse: pack a base-5(+newline=5) symbol string into one integer the way
    the binary stores it (each symbol s -> base-7 digit s+1, MSB-first)."""
    v = 0
    for ch in symbols:
        v = v * 7 + (int(ch) + 1)
    return v


def selftest() -> List[Tuple[str, bool]]:
    out: List[Tuple[str, bool]] = []

    # KAT: the guide's worked example for the start of East 1.
    chunk = (0xacf68674 << 32) | 0x5634505c
    out.append(("guide KAT: 0xacf686745634505c -> East 1 start",
                decode_chunk(chunk) == "2010132233040411302321"))

    # base-7 representation check (drop padding 0, sub 1).
    out.append(("decode_chunk drops only padding 0 and subtracts 1",
                decode_chunk(encode_symbols("01234")) == "01234"))

    # newline symbol (5) survives a round-trip (base-7 digit 6).
    out.append(("newline symbol 5 round-trips",
                decode_chunk(encode_symbols("0125340")) == "0125340"))

    # encode/decode round-trip over many random symbol strings.
    import random
    rng = random.Random(0)
    ok = True
    for _ in range(500):
        s = "".join(str(rng.randint(0, 5)) for _ in range(rng.randint(1, 22)))
        s = s.lstrip("0") or "0"          # leading 0s are padding-ambiguous by design
        if decode_chunk(encode_symbols(s)) != s:
            ok = False
            break
    out.append(("encode/decode round-trip (no leading-0 ambiguity)", ok))

    # empty / zero chunk decodes to empty (pure padding).
    out.append(("zero chunk -> empty (pure padding)", decode_chunk(0) == ""))

    return out


if __name__ == "__main__":
    import sys
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} provenance checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
