#!/usr/bin/env python3
"""
eyeh1 -- retiring a hypothesis the project has carried since cycle five, and
dissolving the test FR43 nominated. Read-only.

TWO HORIZON ITEMS, TWO DIFFERENT FATES.

FR43 item 1 -- "attack the consecutive-label assumption" -- is NOT TESTABLE as
posed, and this cycle shows why rather than attempting it. The indicator is
ind_m = C[(label_m + base_m + K_g[0]) mod 83] with base_m free per message and
K_g[0] free per triplet, so for any target glyph and any label there is a base
making them agree. Fixing a consecutive label assignment and solving for the
bases succeeds; fixing an arbitrary assignment and solving succeeds equally.
The label structure leaves no trace in the ciphertext.

FR43 item 2 -- "re-examine H1's provenance" -- is live and decisive. H1 (FR5)
asserts that the same boundary token closes both opening frames, at T3 slot 20
(glyph 47) and T1 slot 24 (glyph 1), giving q[1] - q[47] = 4. Both glyphs sit
at the LAST position of an opening block. FR29 concluded the T3 opening must be
read as literal stamped material rather than encrypted shared plaintext, and
FR33's widening forced the same reading onto T1. Under that reading those
positions carry no plaintext token, so H1's claim about their q values has no
referent.

A second, independent argument points the same way. If the openings are
literal stamped material and a shared boundary marker closes both, that marker
would be the SAME GLYPH in both. It is not -- 1 against 47. A single token
encrypting to two different glyphs is possible only under the ENCRYPTED
reading, which is exactly the reading FR29 and FR33 rejected. H1 belongs to
the discarded branch.
"""

import json, os, random, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeind", "eyenull", "eyeinject", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = {"T1": ["East 1", "West 1", "East 2"],
            "T2": ["West 2", "East 3", "West 3"],
            "T3": ["East 4", "West 4", "East 5"]}
PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "H1_sites": [(47, 20, "T3"), (1, 24, "T1")],
          "openings": {"T1": (1, 24), "T3": (1, 20)}}

def site_check(S):
    Lx, cts = S["Lx"], S["cts"]
    out = []
    for g, slot, tr in PREREG["H1_sites"]:
        hits = [m for m in TRIPLETS[tr]
                if slot < len(cts[Lx[m]]) and cts[Lx[m]][slot] == g]
        lo, hi = PREREG["openings"][tr]
        out.append((g, slot, tr, hits, lo <= slot <= hi))
    return out

def label_solvability(S, labs, seed=1):
    """can an arbitrary label assignment be reconciled with the observed
    indicator glyphs by choosing bases? (it always can)"""
    rng = random.Random(seed)
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    C = list(range(N)); rng.shuffle(C)
    q = [0] * N
    for i, s in enumerate(C): q[s] = i
    inds = [cts[Lx[m]][0] for m in labels]
    bases = [(q[inds[i]] - labs[i]) % N for i in range(len(labs))]
    return all(C[(labs[i] + bases[i]) % N] == inds[i] for i in range(len(labs)))

def prefix_tree(S):
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    out = []
    for hi in range(2, 25):
        seqs = {tuple(cts[Lx[m]][1:hi]) for m in labels
                if hi <= len(cts[Lx[m]])}
        out.append((hi - 1, len(seqs)))
    return out

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: site verification, label solvability, tree monotonicity")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas)

    sites = site_check(S)
    check("H1's glyphs occur at the stated slots in every triplet member",
          all(len(h) == 3 for _, _, _, h, _ in sites),
          f"({[(g, len(h)) for g, _, _, h, _ in sites]})")
    check("and both slots lie inside an opening block",
          all(inside for *_, inside in sites))

    check("consecutive labels are solvable for bases",
          label_solvability(S, list(range(9))))
    rng = random.Random(3)
    check("arbitrary labels are equally solvable (no trace in ciphertext)",
          label_solvability(S, [rng.randrange(N) for _ in range(9)]))

    tree = prefix_tree(S)
    check("prefix tree is non-decreasing in window length",
          all(tree[i][1] <= tree[i + 1][1] for i in range(len(tree) - 1)),
          f"({[c for _, c in tree[:8]]}...)")
    check("positions 1-2 are universal across all nine messages",
          tree[0][1] == 1 and tree[1][1] == 1)

    c = json.load(open(corpus))
    cts = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nH1 where H1's glyphs live")
    for g, slot, tr, hits, inside in site_check(S):
        lo, hi = PREREG["openings"][tr]
        print(f"  glyph {g:2d} at slot {slot} of {tr}: present in "
              f"{len(hits)}/3 messages {hits}")
        print(f"     {tr} opening spans {lo}..{hi}; slot {slot} is "
              f"{'INSIDE, at the terminal position' if inside else 'outside'}")

    print("\nH2 what the adopted model says about those positions")
    print("  FR29: the T3 opening must be read as literal stamped material or")
    print("        the constraint system contradicts at every drift")
    print("  FR33: the passage widening forced the same reading onto T1")
    print("  -> opening positions carry stamped glyphs, not ciphertext of")
    print("     plaintext tokens. H1 asserts a relation between the PLAINTEXT")
    print("     TOKENS at two such positions, so under the adopted model it has")
    print("     no referent.")

    print("\nH3 a second, independent argument")
    t1 = cts[Lx["East 1"]][24]; t3 = cts[Lx["East 4"]][20]
    print(f"  T1's terminal opening glyph: {t1}")
    print(f"  T3's terminal opening glyph: {t3}")
    print(f"  identical: {t1 == t3}")
    print("  under a LITERAL reading a shared boundary marker would be the same")
    print("  glyph; it is not. A single token encrypting to two different glyphs")
    print("  is possible only under the ENCRYPTED reading -- the one FR29 and")
    print("  FR33 rejected. H1 belongs to the discarded branch.")

    print("\nH4 the opening prefix tree (why the stamped reading is natural)")
    print(f"  {'window 1..k':>12s} {'distinct sequences across the 9 messages':>42s}")
    for k, cnt in prefix_tree(S):
        if k in (2, 3, 5, 6, 9, 10, 15, 20, 24):
            print(f"  {k:12d} {cnt:42d}")
    print("  the openings form a nested tree: a universal two-glyph head, then")
    print("  successive branchings. That is the shape of a structured header,")
    print("  and it is what the depth-tree work recorded independently.")

    print("\nH5 FR43's item 1 dissolves")
    print("  ind_m = C[(label_m + base_m + K_g[0]) mod 83], with base_m free per")
    print("  message and K_g[0] free per triplet.")
    rng = random.Random(11)
    for tag, labs in (("consecutive 0..8", list(range(9))),
                      ("arbitrary", [rng.randrange(N) for _ in range(9)])):
        print(f"    labels {tag:18s}: solvable for bases = "
              f"{label_solvability(S, labs)}")
    print("  both work, so the label structure leaves no trace in the")
    print("  ciphertext and cannot be attacked from inside the corpus.")

    print("\nH6 verdict")
    print("  H1 IS RETIRED, on coherence rather than on measurement: it presumes")
    print("  the openings are encrypted plaintext, which the model rejected two")
    print("  cycles before FR43 raised it against H4. FR43's conflict therefore")
    print("  resolves by removing one side, not by testing the other.")
    print("  CONDITION: H1 revives if the stamped-header reading is abandoned.")
    print("  H4 survives as the only drift hypothesis, still resting on an")
    print("  untestable premise, and still implying drift in {1..8, 75..82}.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
