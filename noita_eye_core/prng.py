"""Noita's world-generation PRNG (``NollaPRNG``), ported faithfully.

Why add it: EyeStat's PRNG zoo ships generic LCG/xorshift/PCG/MT families.  If
the eye keystream was produced in-engine, only Noita's *exact* generator
reproduces it -- a generic Park-Miller with a different seeding will silently
miss.  Noita's core ``Next()`` is the Lewis-Goodman-Miller / Park-Miller
"minimal standard" generator (a = 16807, m = 2^31-1); the distinctive part is
``SetRandomSeed(x, y)`` -- a position->seed scrambler built on IEEE-754 bit
twiddling -- which is what couples a *world position* to a stream.

Source of the algorithm: the reverse-engineered reference
``pudy248/noitaWandAtlas/src/noita_random.h`` (credited to kaliuresis/noa),
matching the Noita Wiki "Technical: Noita PRNG" description.  This is a
byte-faithful port: 32-bit signed wraparound and C truncating integer division
are emulated explicitly.

KATs
----
* ``Next()`` core == Park & Miller minimal standard: from seed 1, the 10000th
  iterate is 1043618065 (the canonical published value, also cited in the
  EyeStat audit).  Independently verifiable, not invented here.
* ``Next()`` stream matches EyeStat's ``ParkMillerV0Rng`` state-for-state when
  reachable (a concrete convergence check against the existing tool).
* ``SetRandomSeed`` carries a regression vector that locks this faithful port
  (labelled as such -- no external game capture was available to certify it).
"""
from __future__ import annotations

import struct
from typing import List, Tuple

MASK32 = 0xFFFFFFFF
MASK64 = 0xFFFFFFFFFFFFFFFF
INT_MAX = 0x7FFFFFFF  # 2**31 - 1 = MINSTD modulus


def _i32(v: int) -> int:
    """Reduce to a 32-bit two's-complement signed int (C ``int`` semantics)."""
    v &= MASK32
    return v - 0x100000000 if (v & 0x80000000) else v


def _ctrunc_div(a: int, b: int) -> int:
    """C integer division: truncate toward zero (Python ``//`` floors)."""
    q = abs(a) // abs(b)
    return -q if (a < 0) != (b < 0) else q


def _double_bits(x: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", x))[0]


class NollaPRNG:
    """Faithful port of Noita's ``NollaPRNG``."""

    def __init__(self, world_seed: int):
        self.world_seed = world_seed & MASK32
        self.Seed = _i32(world_seed)

    # -- core MINSTD step -------------------------------------------------
    def next_raw(self) -> int:
        """Advance the state and return the raw integer Seed (in [1, 2^31-1))."""
        s = self.Seed
        v4 = _i32(_i32(s * 0x41A7) + _i32(_ctrunc_div(s, 0x1F31D) * (-INT_MAX)))
        if v4 < 0:
            v4 += INT_MAX
        self.Seed = v4
        return v4

    def next(self) -> float:
        """``float`` in [0, 1] (Noita ``Next``)."""
        return self.next_raw() / INT_MAX

    def random(self, a: int, b: int) -> int:
        """Integer in [a, b] inclusive (Noita ``Random(a, b)``)."""
        self.next_raw()
        return a + int((b - a + 1) * self.Seed * 4.656612875e-10)

    # -- position -> seed scrambler --------------------------------------
    def _helper(self, r: float) -> int:
        e = _double_bits(r) & 0x7FFFFFFFFFFFFFFF
        c = -1 if r < 0 else 1
        f = (e & 0xFFFFFFFFFFFFF) | 0x0010000000000000
        g = (0x433 - (e >> 0x34)) & MASK64
        shift = g & 0x3F  # x86 64-bit shift count masking
        h = (f >> shift) & MASK64
        cond = 1 if (0x433 < (((e >> 0x20) & 0xFFFFFFFF) >> 0x14)) else 0
        j = MASK32 if cond else 0
        a = ((j << 0x20) | j) & MASK64
        b = (((~a & MASK64) & h) | (((f << 0xD) & MASK64) & a)) & MASK64
        b *= c
        return b & 0xFFFFFFFF

    @staticmethod
    def _helper2(a: int, b: int, ws: int) -> int:
        a &= MASK32
        b &= MASK32
        ws &= MASK32
        uVar2 = (((a - b - ws) & MASK32) ^ (ws >> 0xD)) & MASK32
        uVar1 = (((b - uVar2 - ws) & MASK32) ^ ((uVar2 << 8) & MASK32)) & MASK32
        uVar3 = (((ws - uVar2 - uVar1) & MASK32) ^ (uVar1 >> 0xD)) & MASK32
        uVar2 = (((uVar2 - uVar1 - uVar3) & MASK32) ^ (uVar3 >> 0xC)) & MASK32
        uVar1 = (((uVar1 - uVar2 - uVar3) & MASK32) ^ ((uVar2 << 0x10) & MASK32)) & MASK32
        uVar3 = (((uVar3 - uVar2 - uVar1) & MASK32) ^ (uVar1 >> 5)) & MASK32
        uVar2 = (((uVar2 - uVar1 - uVar3) & MASK32) ^ (uVar3 >> 3)) & MASK32
        uVar1 = (((uVar1 - uVar2 - uVar3) & MASK32) ^ ((uVar2 << 0xA) & MASK32)) & MASK32
        return (((uVar3 - uVar2 - uVar1) & MASK32) ^ (uVar1 >> 0xF)) & MASK32

    def set_random_seed(self, x: float, y: float) -> None:
        ws = self.world_seed & MASK32
        a = (ws ^ 0x93262E6F) & MASK32
        b = a & 0xFFF
        c = (a >> 0xC) & 0xFFF

        x_ = float(x) + b
        y_ = float(y) + c

        r = x_ * 134217727.0
        e = self._helper(r)

        if 102400.0 <= abs(y_) or abs(x_) <= 1.0:
            r = y_ * 134217727.0
        else:
            y__ = y_ * 3483.328
            y__ += float(e)
            r = y_ * y__

        f = self._helper(r)
        g = self._helper2(e & MASK32, f & MASK32, ws)

        s = g / 4294967295.0
        s *= 2147483639.0
        s += 1.0
        self.Seed = int(s)  # C (int) cast truncates toward zero; s > 0 here

        self.next_raw()
        h = ws & 3
        while h > 0:
            self.next_raw()
            h -= 1

    # -- convenience for the cipher convergence --------------------------
    def keystream_mod(self, N: int, count: int) -> List[int]:
        """A length-``count`` keystream of symbols in [0, N) via Random(0,N-1).

        This is how a Noita-derived position keystream would feed the mod-N
        stream cipher in :mod:`cipher_ops`.
        """
        return [self.random(0, N - 1) for _ in range(count)]

    def procedural_stream_mod(self, coords, N: int) -> List[int]:
        """One symbol per (x, y) coordinate via ProceduralRandom -- models a
        position-keyed keystream (each absolute position seeds the RNG)."""
        out: List[int] = []
        for (x, y) in coords:
            self.set_random_seed(x, y)
            out.append(self.random(0, N - 1))
        return out


def minstd_iterate(seed: int, n: int) -> int:
    """Reference MINSTD iteration via Schrage's method (independent of the
    NollaPRNG int-overflow form) for KAT cross-checking."""
    A, M, Q, R = 16807, 2147483647, 127773, 2836
    s = seed
    for _ in range(n):
        hi, lo = divmod(s, Q)
        s = A * lo - R * hi
        if s <= 0:
            s += M
    return s


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------

def selftest() -> List[tuple[str, bool]]:
    import sys
    from pathlib import Path

    out: List[tuple[str, bool]] = []

    # Canonical Park-Miller minimal-standard KAT: seed=1, 10000th iterate.
    out.append(("Schrage MINSTD 10000th iterate == 1043618065",
                minstd_iterate(1, 10000) == 1043618065))

    # NollaPRNG.next_raw() reproduces the same MINSTD recurrence.
    p = NollaPRNG(0)
    p.Seed = 1
    for _ in range(10000):
        p.next_raw()
    out.append(("NollaPRNG.next_raw 10000th iterate == 1043618065",
                p.Seed == 1043618065))

    # next_raw stays in the valid MINSTD range and matches Schrage step-by-step.
    p2 = NollaPRNG(0)
    p2.Seed = 12345
    ref = 12345
    ok_stream = True
    for _ in range(2000):
        ref = minstd_iterate(ref, 1)
        got = p2.next_raw()
        if got != ref or not (1 <= got < 2147483647):
            ok_stream = False
            break
    out.append(("next_raw matches Schrage MINSTD for 2000 steps", ok_stream))

    # next() in [0,1]; random(a,b) within bounds and covers the range.
    p3 = NollaPRNG(123456)
    p3.set_random_seed(10.0, 20.0)
    floats_ok = all(0.0 <= p3.next() <= 1.0 for _ in range(1000))
    out.append(("next() stays in [0,1]", floats_ok))
    vals = [p3.random(0, 82) for _ in range(5000)]
    out.append(("random(0,82) within bounds",
                all(0 <= v <= 82 for v in vals)))
    out.append(("random(0,82) covers most of the range",
                len(set(vals)) >= 80))

    # Determinism: same world seed + same coordinate => identical stream.
    qa = NollaPRNG(98765)
    qa.set_random_seed(3.0, 7.0)
    sa = [qa.random(0, 82) for _ in range(20)]
    qb = NollaPRNG(98765)
    qb.set_random_seed(3.0, 7.0)
    sb = [qb.random(0, 82) for _ in range(20)]
    out.append(("deterministic for fixed (world_seed, x, y)", sa == sb))

    # Different coordinates diverge (scrambler actually mixes position).
    qc = NollaPRNG(98765)
    qc.set_random_seed(3.0, 8.0)
    sc = [qc.random(0, 82) for _ in range(20)]
    out.append(("different position -> different stream", sa != sc))

    # Regression vector locking this faithful SetRandomSeed port.
    rp = NollaPRNG(1)
    rp.set_random_seed(0.0, 0.0)
    seed_after = rp.Seed
    first5 = [rp.random(0, 82) for _ in range(5)]
    out.append(("SetRandomSeed regression vector (locks port)",
                seed_after == _REG_SEED_AFTER and first5 == _REG_FIRST5))

    # Cross-check against EyeStat's ParkMillerV0Rng if importable.
    eyestat = Path(__file__).resolve().parent.parent / "eyestat"
    if (eyestat / "eyestat_prngs.py").exists():
        sys.path.insert(0, str(eyestat))
        try:
            import eyestat_prngs as ep  # type: ignore
            rng = ep.ParkMillerV0Rng(777)
            noita = NollaPRNG(0)
            noita.Seed = 777
            match = all(noita.next_raw() == rng.next_u32() for _ in range(500))
            out.append(("Next() core == EyeStat ParkMillerV0 (convergence)",
                        match))
        except Exception:
            pass
        finally:
            sys.path.pop(0)

    # --- paranoia: random(a,b) bounds under stress (float rounding risk) ----
    bounds_ok = True
    range_seen = set()
    for ws in (1, 2, 7, 12345, 0xFFFFFFFF, 987654321):
        q = NollaPRNG(ws)
        q.set_random_seed(float(ws % 97), float((ws * 3) % 89))
        for _ in range(20000):
            v = q.random(0, 82)
            if not (0 <= v <= 82):
                bounds_ok = False
                break
            range_seen.add(v)
        if not bounds_ok:
            break
    out.append(("random(0,82) never escapes bounds over 120k draws",
                bounds_ok))
    out.append(("random(0,82) reaches both endpoints",
                0 in range_seen and 82 in range_seen))

    # next_raw stays in the valid MINSTD range [1, 2^31-2] from a healthy seed.
    q2 = NollaPRNG(424242)
    q2.set_random_seed(5.0, 9.0)
    rng_ok = all(1 <= q2.next_raw() <= INT_MAX - 1 for _ in range(50000))
    out.append(("next_raw stays in [1, 2^31-2]", rng_ok))

    # random(a,b) with a==b is constant a (degenerate range).
    q3 = NollaPRNG(11)
    q3.set_random_seed(1.0, 2.0)
    out.append(("random(a,a) == a", all(q3.random(7, 7) == 7 for _ in range(100))))

    return out


# Regression constants for the faithful SetRandomSeed port (world_seed=1,
# SetRandomSeed(0,0)); filled in from a first run and then locked.
_REG_SEED_AFTER = 275022572
_REG_FIRST5: List[int] = [35, 67, 10, 77, 75]


if __name__ == "__main__":
    import sys
    if "--emit-regression" in sys.argv:
        rp = NollaPRNG(1)
        rp.set_random_seed(0.0, 0.0)
        sa = rp.Seed
        f5 = [rp.random(0, 82) for _ in range(5)]
        print(f"_REG_SEED_AFTER = {sa}")
        print(f"_REG_FIRST5 = {f5}")
        sys.exit(0)
    results = selftest()
    for label, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    n_ok = sum(1 for _, ok in results if ok)
    print(f"\n{n_ok}/{len(results)} prng checks passed")
    sys.exit(0 if n_ok == len(results) else 1)
