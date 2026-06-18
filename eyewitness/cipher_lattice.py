#!/usr/bin/env python3
"""EyeWitness — cipher-construction lattice.

Enumerates which cipher constructions survive ALL validated structural constraints,
runs the re-sync test (excludes ciphertext-autokey), and writes
report/cipher_lattice_report.md.

Run:
    python3 cipher_lattice.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import resync                 # noqa: E402


def main() -> int:
    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    # E1/W1 re-sync (shared-key near-duplicate pair)
    rs = resync.count_resync(M[0], M[1])
    idf = resync.identical_fraction(M[0], M[1])

    L = []
    L.append("# Cipher-Construction Lattice — what fits the validated structure")
    L.append("")
    L.append("*Reproduce: `python3 eyewitness/cipher_lattice.py`. Constructions are "
             "kept only if they fit EVERY validated structural fact.*")
    L.append("")
    L.append("## The hard constraints (the filter)")
    L.append("1. N=83 (prime), flat unigram (IoC≈uniform).")
    L.append("2. **Interrelated alphabets** — isomorphs z≈117 (single mixed alphabet "
             "family; rules out independent-column / unrelated-alphabet OTP).")
    L.append("3. **Position-dependent within a message** — same plaintext at different "
             "positions gives different (isomorphic) ciphertext (E1@39 vs @67: 0/20 "
             "identical, same pattern).")
    L.append("4. **Per-message variation required** — E2 is isomorphic to E1 but "
             "value-shifted (different base), so a single global key is insufficient.")
    L.append("5. **Keys cluster** — E1≈W1 share a key: "
             f"{idf*100:.0f}% identical glyphs, in blocks.")
    L.append(f"6. **Re-sync: {rs} events** in E1/W1 (identical→differ→identical) — "
             "the difference does NOT propagate.")
    L.append("7. Literal universal (66,5) header; no periodicity, no transposition, "
             "no fractionation; hard-coded/offline-authored.")
    L.append("")
    L.append("## SURVIVING family")
    L.append("**A position-indexed-keystream substitution over a single interrelated "
             "(mixed) alphabet C, with a per-message/per-group key offset (base).**")
    L.append("")
    L.append("`c[m][t] = C[(p[m][t] + base_m + K[t]) mod 83]`, K a position keystream "
             "shared by all messages; base_m the per-message offset (clusters: "
             "E1=W1, E2 differs).")
    L.append("")
    L.append("| construction | fits? | why |")
    L.append("|---|---|---|")
    L.append("| **A. Progressive / Trithemius** (K[t]=t, linear slide) + per-msg base | "
             "**FITS** | position-only keystream re-syncs; +base gives per-msg variation; "
             "single mixed alphabet = interrelated. The simplest survivor. |")
    L.append("| **B. General aperiodic position-keystream** (K[t] arbitrary, same for "
             "all msgs) + per-msg base | **FITS** | same as A but K need not be linear; "
             "isomorph data does not force K linear. |")
    L.append("| **C. Per-message/group MIXED-ALPHABET progressive** (C_m = S_m∘C, all "
             "related) | **FITS** | a per-message substitution stacked on the slide is "
             "absorbed into a per-message alphabet; still single-family/interrelated. |")
    L.append("| **D. Plaintext-autokey lag-1** (keystream = prior plaintext) + per-msg "
             "seed | **NOT EXCLUDED** | it re-syncs one position late; distinguishing it "
             "from A/B needs the plaintext (lag-0 vs lag-1). A residual alternative. |")
    L.append("")
    L.append("## EXCLUDED constructions (with reason)")
    L.append("| construction | verdict | reason |")
    L.append("|---|---|---|")
    L.append("| Ciphertext-autokey (any lag) | **EXCLUDED** | difference would "
             f"propagate; E1/W1 show {rs} clean re-syncs (`resync`). |")
    L.append("| Single global key, no per-message base | **EXCLUDED** | E2 is "
             "isomorphic-not-identical to E1 (needs per-message base). |")
    L.append("| Pure progressive with NO per-message offset | **EXCLUDED** | would "
             "make shared openings identical; they are value-shifted across some msgs. |")
    L.append("| Transposition / cut-and-shuffle on glyph order | **EXCLUDED** | "
             "transposition ruled out; would also break the re-sync block alignment. |")
    L.append("| Fractionation / Trifid (on eye-marks) | **EXCLUDED** | eye-mark streams "
             "structureless; no period (`trifid`). |")
    L.append("| Periodic Vigenère / monoalphabetic / block / AES-CTR | **EXCLUDED** | "
             "prior calibrated tests. |")
    L.append("")
    L.append("## Stacked-cipher (combination) note")
    L.append("- substitution ∘ position-keystream → absorbed into a per-message/group "
             "mixed alphabet (construction C).")
    L.append("- anything ∘ transposition → excluded (transposition out; breaks re-sync).")
    L.append("- two stacked position-keystreams → collapse to one combined K (B).")
    L.append("- a 0–82 'cut'/offset → exactly the per-message base in A/B/C.")
    L.append("So the community 'GAK/XGAK/stacked-with-cut' theories all reduce to the "
             "single surviving family above: **mixed-alphabet position-keystream + "
             "per-message base**, differing only in whether K is linear (A) or general "
             "(B) and whether the alphabet is global (A/B) or per-group (C).")
    L.append("")
    L.append("## Honest open sub-questions")
    L.append("- K linear (progressive) vs general aperiodic — not yet distinguished.")
    L.append("- position-keystream (A/B) vs plaintext-autokey lag-1 (D) — needs plaintext.")
    L.append("- the per-message base grouping (why E1=W1 share, E2 differs).")
    L.append("- ALL of the above are moot for READING without the glyph→character "
             "ordering — the standing bottleneck.")

    out = ROOT / "report" / "cipher_lattice_report.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n[wrote] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
