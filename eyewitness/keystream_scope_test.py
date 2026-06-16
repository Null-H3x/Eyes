#!/usr/bin/env python3
"""EyeWitness keystream-scope test — one global keystream, or one per triplet?

Decides whether a single position keystream spans all nine messages (GLOBAL) or
each triplet carries its own (PER-TRIPLET), by comparing within-triplet vs
cross-triplet difference-IoC.  Runs `noita_eye_core.keystream_scope`.

The verdict is taken on the message **body** (after the shared opening), because
the triplets' shared preambles and the universal header inflate cross-triplet
difference-IoC near the start and would otherwise fake a "global" result.

Run:
    python3 keystream_scope_test.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod      # noqa: E402
import keystream_scope as ksc    # noqa: E402

BODY_START = 25   # past the longest triplet opening + the universal header


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    messages = [list(ct) for ct in c.ciphertexts]

    print("=" * 70)
    print("EYEWITNESS — keystream scope (global vs per-triplet)")
    print("=" * 70)
    for start, label in ((0, "FULL overlap (confounded by shared openings)"),
                         (BODY_START, f"BODY only, positions >= {BODY_START} "
                                      "(PRIMARY)")):
        r = ksc.scope_report(messages, N, body_start=start, n_null=1000, seed=0)
        print(f"\n[{label}]")
        print(f"  within-triplet diff-IoC = {r.within_mean:.4f}  "
              f"z={r.within_sig.z:.1f}   (n={r.n_within} pairs)")
        print(f"  cross-triplet  diff-IoC = {r.cross_mean:.4f}  "
              f"z={r.cross_sig.z:.1f}   (n={r.n_cross} pairs)")
        print(f"  uniform baseline (1/N)  = {r.uniform_baseline:.4f}")
        print(f"  verdict: {r.verdict}")

    print("\n" + "-" * 70)
    print("CONCLUSION (trust the BODY verdict):")
    rb = ksc.scope_report(messages, N, body_start=BODY_START, n_null=1000, seed=0)
    if rb.verdict.startswith("PER-TRIPLET"):
        print("  PER-TRIPLET keystreams. The cross-triplet 'depth' at full")
        print("  overlap is a shared-preamble artifact; once the openings are")
        print("  removed, cross-triplet differences sit exactly at the uniform")
        print("  baseline. Each triplet has its OWN keystream.")
        print("  => EyeCrack must hunt THREE keystreams (one per triplet), and")
        print("     effective depth per column is 3 messages, not 9.")
    elif rb.verdict.startswith("GLOBAL"):
        print("  GLOBAL keystream — one keystream spans all nine even after the")
        print("  openings are stripped. EyeCrack hunts a single keystream.")
    else:
        print(f"  {rb.verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
