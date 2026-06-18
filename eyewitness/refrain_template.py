#!/usr/bin/env python3
"""EyeWitness — refrain repeat-template.

Extracts, ordering-free, the structure the 22-glyph refrain forces on its
plaintext: which positions must be the SAME letter, which must DIFFER, which are
free, and how many free plaintext degrees of freedom remain. This is what makes
guided crib generation possible (blind guessing passes the structural filter at
~0/300, any language — only a phrase matching this template can pass).

Run:
    python3 refrain_template.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import refrain as rf          # noqa: E402
import template as tp         # noqa: E402


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    M = [list(x) for x in c.ciphertexts]
    region = rf.DEFAULT_INSTANCES
    L = rf.DEFAULT_LEN

    print("=" * 70)
    print("EYEWITNESS — refrain repeat-template (ordering-free)")
    print("=" * 70)
    print(f"Refrain region {[(c.labels[m], p) for m, p in region]}, L={L} glyphs.")
    t = tp.extract(M, region, L, N)
    if not t.consistent:
        print(f"  INCONSISTENT at {t.contradiction} (refrain shorter than {L}?)")
        return 1
    print(f"\nFree plaintext degrees of freedom: {t.dof} of {L}")
    print("  (the relative plaintext is pinned to a {}-parameter family)".format(t.dof))
    print(f"\nForced-SAME letter groups (must share a letter): "
          f"{t.same_groups if t.same_groups else 'none'}")
    print(f"Free positions (unconstrained): {t.free_positions}")
    print(f"\nRepeat skeleton (same group letter; '.'=free; '?'=in difference web):")
    print(f"   pos: " + " ".join(f"{i%10}" for i in range(L)))
    print(f"   pat: " + "  ".join(tp.skeleton_string(t)))
    print(f"\nForced-DIFFERENT pairs: {len(t.diff_pairs)} "
          f"(any candidate must have different letters at each)")
    print("\n" + "-" * 70)
    print("READ:")
    print(f"  A valid 22-glyph refrain must put the SAME letter at each group "
          f"{t.same_groups}")
    print(f"  and DIFFERENT letters across all {len(t.diff_pairs)} forced-different "
          f"pairs. Position(s) {t.free_positions} are free.")
    print(f"  With only {t.dof} free plaintext d.o.f., the refrain's relative")
    print("  structure is nearly fixed — reading it still needs the alphabet")
    print("  ORDERING (value->char), but a correct ordering nearly determines it.")
    print("  CAUTION: this assumes the per-message-progressive model; a tiny dof")
    print("  could also reflect over-constraint from coincidental cross-instance")
    print("  matches if the model is imperfect. Verify before over-trusting.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
