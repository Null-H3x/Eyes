#!/usr/bin/env python3
"""EyeWitness — model-independent shared-structure map.

Maps where the corpus repeats the SAME plaintext (isomorph-based, no cipher model):
the pairwise opening-extent matrix, the triplet shared openings (null-calibrated),
and a census of maximal repeated passages. Writes report/shared_structure_report.md.

Run:
    python3 shared_structure.py
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CORE = ROOT / "noita_eye_core"
sys.path.insert(0, str(CORE))

import corpus as corpus_mod   # noqa: E402
import shared_structure as ss  # noqa: E402


def main() -> int:
    c = corpus_mod.load()
    M = [list(x) for x in c.ciphertexts]
    lab = c.labels
    short = [l.replace("East", "E").replace("West", "W").replace(" ", "") for l in lab]

    L = []
    L.append("# Model-Independent Shared-Structure Map")
    L.append("")
    L.append("*Reproduce: `python3 eyewitness/shared_structure.py`. No cipher-model "
             "assumption — only 'same glyph = same glyph' (isomorph skeletons).*")
    L.append("")
    mat = ss.opening_extent_matrix(M)
    L.append("## Opening-extent matrix (isomorph extent from body pos 3)")
    L.append("")
    L.append("How many glyphs each message pair shares as the SAME plaintext from "
             "the opening (after the (66,5) header).")
    L.append("")
    L.append("```")
    L.append("        " + " ".join(f"{s:>3}" for s in short))
    for i in range(len(M)):
        L.append(f"{short[i]:>4}   " + " ".join(f"{mat[i][j]:>3}" for j in range(len(M))))
    L.append("```")
    L.append("")
    trip = [("Triplet 1", (0, 1, 2)), ("Triplet 2", (3, 4, 5)), ("Triplet 3", (6, 7, 8))]
    res = ss.triplet_openings(M, trip, n_null=400)
    L.append("## Triplet shared openings (3-way, null-calibrated)")
    L.append("")
    L.append("| triplet | members | shared-opening glyphs | significant? |")
    L.append("|---|---|---|---|")
    for r in res:
        mem = "/".join(short[m] for m in r.members)
        L.append(f"| {r.name} | {mem} | {r.extent} | "
                 f"{'YES' if r.significant else 'no (~null '+format(r.null_mean,'.1f')+')'} |")
    L.append("")
    L.append("## Repeated-passage census (maximal, anywhere in the corpus)")
    L.append("")
    passages = ss.repeated_passages(M, min_len=12)
    passages = [p for p in passages if p["length"] >= 12][:12]
    L.append("| length | count | messages | first occurrences |")
    L.append("|---|---|---|---|")
    for p in passages:
        occ = ", ".join(f"{short[m]}@{q}" for m, q in p["occurrences"][:6])
        msgs = "/".join(short[m] for m in p["messages"])
        L.append(f"| {p['length']} | {p['count']} | {msgs} | {occ} |")
    L.append("")
    L.append("## Read (what is solid, model-free)")
    L.append("- **Triplet 1 (E1/W1/E2)** shares a long opening (~22 glyphs); "
             "**Triplet 3 (E4/W4/E5)** shares ~18. Both far above the null — the "
             "messages genuinely come in triplets with shared openings (confirms "
             "the original triplet theory, model-free).")
    L.append("- **Triplet 2 (W2/E3/W3)** does NOT share a long opening (~null); "
             "W2/W3 share ~13 but E3 is weakly linked to everything — E3 is "
             "structurally distinct (and the longest message).")
    L.append("- **No universal opening** beyond the (66,5) header (9-way ~ chance).")
    L.append("- These shared passages are model-free same-plaintext anchors: they "
             "constrain the plaintext content directly, and are the highest-value "
             "targets for any future ordering/anchor (independent of the cipher model).")

    out = ROOT / "report" / "shared_structure_report.md"
    out.write_text("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n[wrote] {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
