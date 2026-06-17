#!/usr/bin/env python3
"""EyeCrack salakieli crib battery — run the salakieli register through every
crib pathway and report honestly which can and cannot confirm a placement.

Two pathways, with different powers:

  A. Two-time-pad crib-drag (mapping-free, generator-free).  Works only where
     >=2 members of a depth-group carry DISTINCT known plaintext at the same
     position.  The eye depth-groups are near-duplicate pairs (similar text, not
     two different phrases), so this pathway is expected to stay null — and it
     does — but we run it for completeness and record the decoy false-positive
     rate so the null is quantified.

  B. Crib -> seed -> decrypt-all (globality), per generator.  A long phrase's
     repeat pattern (8-24 constraints) filters seeds to ~1/N^k; a survivor that
     decrypts ALL nine to structure proves a global keystream.  This is the
     pathway where the strong salakieli phrases pay off — but it needs a
     generator family, and the seed must lie in the scanned range.  Run the
     heavy sweep on the GPU (eyestat/globality_gpu.py); this prints the exact
     commands for the strongest cribs.

    python3 salakieli_crib.py                  # cribdrag pass + GPU commands
    python3 salakieli_crib.py --globality-demo # also run a small CPU globality pass
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parent / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import cribdrag               # noqa: E402
import salakieli              # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="salakieli crib battery")
    ap.add_argument("--min-len", type=int, default=4)
    ap.add_argument("--min-redundant", type=int, default=4)
    ap.add_argument("--top-cribs", type=int, default=8)
    ap.add_argument("--globality-demo", action="store_true",
                    help="run a small CPU globality pass on the top crib")
    ap.add_argument("--demo-count", type=int, default=300000)
    args = ap.parse_args()

    c = corpus_mod.load()
    reg = salakieli.ranked(min_len=args.min_len)

    print("=" * 70)
    print("EYECRACK — salakieli crib battery")
    print("=" * 70)
    print(f"register: {len(reg)} cribs from {len(salakieli.RAW_PHRASES)} phrases "
          f"(spaceless; sub-phrases + words). Strongest:")
    for w, k, kind in reg[:args.top_cribs]:
        print(f"  {k:>2} constraints  {kind:10} {w}")

    # ---- Pathway A: two-time-pad crib-drag (generator-free) ----
    print("\n[A] two-time-pad crib-drag (mapping-free)")
    words = salakieli.all_cribs(min_len=args.min_len)
    res = cribdrag.search_corpus(c, words=words, min_len=args.min_len,
                                 require_distinct=2,
                                 min_redundant=args.min_redundant, top=15)
    if res:
        msgs = [list(ct) for ct in c.ciphertexts]
        lengths = sorted({len(w) for w in words if len(w) >= args.min_len})
        fp = {fam: cribdrag.decoy_rate(msgs, fam, c.N, lengths, n_decoys=600,
                                       seed=9) for fam in cribdrag.TRIPLETS}
        print(f"  {len(res)} placement(s) cleared evidence >= {args.min_redundant}:")
        for p in res[:15]:
            fam = "+".join(c.labels[i][:2] for i in p.family)
            print(f"    {fam:14} pos {p.start:>3} L{p.length:>2} "
                  f"evidence {p.redundant} {p.words}")
        print("  decoy false-positive rate (RANDOM-letter words, same lengths):")
        for fam, r in fp.items():
            print(f"    {'+'.join(c.labels[i][:2] for i in fam)}: {r:.1%}")
        print("  READ CAREFULLY: these clear the random-letter null, but that is")
        print("  the wrong null for a themed English wordlist — real words share")
        print("  repeat skeletons (seek/seea/eyes interchange at the same spot), so")
        print("  the true false-positive rate is higher than random letters show.")
        print("  Combined with short length (L4-6) and low evidence (4), treat these")
        print("  as SOFT LEADS (note the clustering at one position in the first")
        print("  triplet), not confirmations. The decisive test is pathway B.")
    else:
        print("  no consistent placement (expected: depth-groups are near-")
        print("  duplicate pairs, not two distinct phrases — this pathway can't")
        print("  confirm a single phrase mapping-free).")

    # ---- Pathway B: crib -> globality (needs a generator) ----
    print("\n[B] crib -> seed -> decrypt-all (globality) — the high-power path")
    print("  Run the heavy sweep on the GPU. Strongest cribs first:")
    for w, k, kind in reg[:args.top_cribs]:
        print(f"    # '{w}' ({k} constraints, ~1/83^{k} survive)")
        print(f"    python3 ../eyestat/globality_gpu.py --crib-word {w} "
              f"--crib-msg \"East 1\" --crib-pos 3 --crib-pos-end 40 "
              f"--generators all --seed-end 100000000 --require-gpu \\")
        print(f"        --html ../salakieli_{w[:16]}.html")
    print("  (sweep --crib-msg over all nine messages; a row green across all "
          "nine = global keystream found.)")

    if args.globality_demo:
        import globality as gl
        top = reg[0][0]
        msgs = [list(x) for x in c.ciphertexts]
        print(f"\n[demo] CPU globality on '{top}' over {args.demo_count:,} seeds "
              f"(nolla, pos 3-12) — small range, expect null:")
        any_hit = False
        for pos in range(3, 13):
            if pos + len(top) > len(msgs[0]):
                break
            r = gl.crib_globality_test(msgs, top, pos, 0, "nolla", "add", 0,
                                       args.demo_count, N=c.N, body_start=0,
                                       decoy_seeds=60)
            hits = [x for x in r if x.verdict in ("global", "local")]
            if hits:
                any_hit = True
                print(f"  pos {pos}: {hits[0].verdict} seed {hits[0].seed}")
        if not any_hit:
            print("  no global/local hit in this tiny range (as expected; the real "
                  "search is the GPU sweep above).")

    print("\n" + "-" * 70)
    print("SUMMARY: the salakieli register is the strongest crib set we have "
          "(8-24 constraints). Pathway A can't confirm it mapping-free given the "
          "near-duplicate depth structure; pathway B (globality) is the test — "
          "run the GPU sweep. A single surviving seed that decrypts all nine "
          "would both confirm the crib AND prove a global keystream.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
