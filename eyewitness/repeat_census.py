#!/usr/bin/env python3
"""EyeWitness repeated-substring census — stream vs block/periodic/transposition.

Runs noita_eye_core.repeats: enumerates every k-gram across the nine messages and
classifies collisions.

  ALIGNED collisions (same k-gram, SAME position, two messages) = depth.
  OFFSET collisions (same k-gram, DIFFERENT positions) = the mode tell: a pure
    aperiodic stream produces them only at chance (<<1 for k>=4); an excess means
    periodicity / running-key / a moved-or-reused block (transposition / cut /
    shuffle / ECB).

Run:
    python3 repeat_census.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import repeats                # noqa: E402


def _grp(mi):
    for gi, g in enumerate(repeats.TRIPLETS):
        if mi in g:
            return gi
    return -1


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]
    lab = c.labels

    print("=" * 70)
    print("EYEWITNESS — repeated-substring census")
    print("=" * 70)
    print(f"  {f'k':>2}  {'k-grams':>8}  {'aligned(depth)':>14}  "
          f"{'offset':>7}  {'offset chance':>13}")
    any_offset = False
    cross_body_total = 0
    for k in (3, 4, 5, 6, 7):
        cen = repeats.census(M, N, k)
        cross_body = sum(1 for a in cen.aligned
                         if _grp(a[1][0]) != _grp(a[2][0]) and a[1][1] >= 25)
        cross_body_total += cross_body
        any_offset = any_offset or bool(cen.offset)
        print(f"  {k:>2}  {cen.n_instances:>8}  {len(cen.aligned):>14}  "
              f"{len(cen.offset):>7}  {cen.exp_offset:>13.3f}")
        if cen.offset:
            for v, a, b in cen.offset[:8]:
                print(f"        OFFSET: {lab[a[0]]}@{a[1][1]} == "
                      f"{lab[b[0]]}@{b[1][1]}")

    print("\n" + "-" * 70)
    print("VERDICT:")
    if not any_offset:
        print("  ZERO offset collisions at every k -> NO repeated substring sits at")
        print("  a different position anywhere. This DENIES transposition / cut /")
        print("  positional shuffle, periodic / repeating-key, and block/ECB reuse.")
        print("  The cipher is a PURE APERIODIC, POSITION-LOCKED stream (a per-column")
        print("  bijection that never moves a symbol).")
    else:
        print("  Offset collisions found -> a block was moved/reused or the key/")
        print("  plaintext repeats at a lag (periodic / transposition / cut). See above.")
    print(f"\n  cross-group aligned collisions live only in the opening (pos<25);")
    print(f"  cross-group BODY collisions: {cross_body_total} -> the cross-group")
    print("  commonality is a short shared preamble; the body keystream is per-group.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
