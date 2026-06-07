"""Run the depth analysis on the real Noita eye corpus and print findings.

This is the human-facing entry point that ties the library together:

* confirm the messages are in depth (shared position-keystream),
* show the strongest in-depth pairs and the universal header crib,
* report per-base-5-digit IoC,
* demonstrate exact crib propagation from the universal header.

It deliberately does NOT claim a plaintext: the real corpus has a flat unigram,
so unsupervised keystream recovery is under-determined (see README).  The high-
value, mathematically exact lever here is crib-drag, shown below.
"""
from __future__ import annotations

import corpus as corpus_mod
import depth
import trigram


def main() -> int:
    c = corpus_mod.load()
    N = c.N
    print(f"Corpus: {c.num_messages} messages, alphabet N={N}, "
          f"lengths {list(c.lengths)}\n")

    # 1. Depth confirmation
    rep = depth.confirm_depth(c, n_null=500, seed=1)
    print("== Depth confirmation ==")
    print(f"  mean pairwise difference IoC : {rep.mean_pair_diff_ioc:.4f}")
    print(f"  uniform baseline (1/N)       : {rep.uniform_baseline:.4f}")
    print(f"  overall column agreement     : {rep.equal_fraction:.1%}")
    print(f"  significance                 : {rep.significance}")
    verdict = ("IN DEPTH (shared position-keystream)"
               if rep.significance.z > 5 else "no depth detected")
    print(f"  verdict                      : {verdict}\n")

    print("  strongest in-depth pairs:")
    for a, b, di, ef in sorted(rep.per_pair, key=lambda x: -x[3])[:5]:
        print(f"    {a:8} ~ {b:8}  agreement {ef:5.1%}  diff-IoC {di:.4f}")
    print()

    # 2. Universal header crib
    print("== Universal header (shared ciphertext => shared plaintext) ==")
    uni = corpus_mod.universal_positions(c)
    print(f"  positions identical across all 9 messages: {uni}\n")

    # 3. Per-base-5-digit IoC of each message (source-encoding hypothesis)
    print("== Per-base-5-digit IoC (trigram source hypothesis; N=83 is "
          "prime so this is a source-encoding view, not an alphabet split) ==")
    for i, ct in enumerate(c.ciphertexts):
        d = trigram.per_digit_ioc(ct, 5, 3)
        print(f"  {c.labels[i]:8}  digits(MSB->LSB) IoC = "
              f"[{d[0]:.3f}, {d[1]:.3f}, {d[2]:.3f}]")
    print()

    # 4. Exact crib-drag demo from the longest message's header.
    print("== Crib-drag demo (exact arithmetic) ==")
    print("  Hypothesis: assume message 'East 3' (longest) decrypts to symbols")
    print("  [0,1,2,3,4] at positions 0..4 (placeholder crib); propagate the")
    print("  implied shared keystream to every message.\n")
    ref = c.labels.index("East 3")
    cr = depth.crib_drag(c, ref_index=ref, start=0, plain=[0, 1, 2, 3, 4],
                         mode="add")
    print(f"  implied keystream k[0..4] = {cr.keystream}")
    for i in range(c.num_messages):
        print(f"    {c.labels[i]:8} -> {cr.revealed[i]}")
    print("\n  (Swap in a real header guess to read all 9 headers at once.)")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
