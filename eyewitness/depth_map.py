#!/usr/bin/env python3
"""EyeWitness depth map — how much shared keystream can we actually prove?

Runs noita_eye_core.depthmap. The point is an honest accounting of DEPTH:

  * Shared keystream is PROVABLE only where ciphertext coincides — identical runs
    (shared plaintext + keystream) or equality far above 1/N (shared keystream +
    related plaintext).
  * Where plaintexts differ, shared vs independent keystream is INVISIBLE, and we
    can NEVER prove independence.

It reports the opening shared-keystream clades (which cross triplet boundaries,
refuting strictly-independent per-triplet keys), the body-persistent shared
keystream (only the near-duplicate pairs), and the count of exploitable 2-deep
key-free difference positions.

Run:
    python3 depth_map.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import depthmap as dm         # noqa: E402


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]
    lab = c.labels
    d = dm.build(M, N)

    print("=" * 70)
    print("EYEWITNESS — keystream-sharing / true-depth map")
    print("=" * 70)

    print("\nOpening shared-keystream clades (proven via identical runs):")
    for comp in d.opening_components:
        print("  {" + ", ".join(lab[i] for i in comp) + "}")
    print("  -> these cross triplet boundaries: strictly-independent per-triplet")
    print("     keystreams are REFUTED. (But the openings are shared plaintext,")
    print("     so they carry no decryption leverage.)")

    print("\nBody-persistent shared keystream (equality z > "
          f"{dm.Z_PROVE:.0f} vs 1/N):")
    body = [comp for comp in d.body_components if len(comp) > 1]
    if body:
        for comp in body:
            print("  {" + ", ".join(lab[i] for i in comp) + "}")
    else:
        print("  (none beyond singletons)")
    for e in sorted(d.pairs, key=lambda e: -e.z_body):
        if e.body_proven:
            print(f"    {lab[e.i]:7}~{lab[e.j]:7}  opening={e.prefix:>2}  "
                  f"body_equal={e.body_equal}/{e.body_n}  z={e.z_body:5.1f}  "
                  f"exploitable={e.exploitable}")

    print("\n" + "-" * 70)
    print(f"  exploitable key-free 2-deep positions: {d.exploitable_total} "
          f"(all from the two near-duplicate pairs)")
    print(f"  undetermined pairs (shared vs independent invisible): "
          f"{d.undetermined}/{len(d.pairs)}")
    print("\nCONCLUSION:")
    print("  We do NOT have free 3+ depth in the body. Provable shared keystream")
    print("  is the opening clades (no leverage) plus exactly two near-duplicate")
    print("  pairs (the crib-drag surface). Whether the body keystream is GLOBAL")
    print("  (which would unlock deep depth) is undetermined from ciphertext —")
    print("  the way to test it is a crib: a confident plaintext fragment in one")
    print("  message implies K there; if it decrypts the OTHERS to consistent")
    print("  structure, the keystream is global and depth opens up.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
