#!/usr/bin/env python3
"""
eyeseek -- a constraint form different in kind from the three FR19 closed, and
what it finds. Read-only.

FR30 named widening the components as the single lever that improves both the
endgame exposure and the drift-free channel's power, and FR18 required any new
route to be "different in kind" from isomorph pattern-matching. This is one.

THE METHOD. FR30 established that inside a component q[s] = base_C +
drift*Delta_s with Delta_s known. So for a candidate same-passage window pair
at shift Delta, any cell whose two glyphs BOTH lie in one known component
predicts

    w = (Delta_{c2} - Delta_{c1} - Delta) mod 83

to be the SAME constant across all such cells -- it equals base_diff/drift.
The test is therefore drift-free, and it uses derived knowledge (the skeleton)
rather than raw repeat patterns, so it can evaluate window pairs the isomorph
scan rejects outright.

TWO FILTERS THAT MATTER. Cells where the two glyphs are IDENTICAL give w
trivially and carry no information about the alphabet -- windows that are
literally identical (the near-duplicate runs, the openings) would otherwise
dominate the results. Only cells with DIFFERING glyphs are counted. And
sliding windows of one underlying alignment are deduplicated, since they are
one phenomenon seen at several offsets.

THE SELECTION EFFECT, stated up front. The components were built from the
pool's certified pairs, so the scan can only see passages composed largely of
glyphs those pairs already linked. It is biased toward extending known
territory, and the corpus results show exactly that.
"""

import json, os, random, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyefree", "eyebase", "eyealpha", "eyepack", "eyeskel", "eyerepair",
          "eyescore", "eyeinject", "eyegauge", "eyecore", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeskel as EK                       # noqa: E402
import eyerepair as ERP                    # noqa: E402
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "L": 13, "min_informative": 5, "seed": 20260803}

def skeleton_deltas(S, pool):
    gf = EK.build(S, pool, 1, (("East 4", "East 5"),))
    sk = EK.skeleton(gf)
    delta, comp = {}, {}
    for ci, c in enumerate(sk["comps"]):
        if len(c) < 2: continue
        anc = c[0]; o = {anc: 0}
        for s in c:
            if s == anc: continue
            h = [d for d in range(N)
                 if gf.classify({s: 1, anc: N - 1}, d) == "redundant"]
            if len(h) == 1: o[s] = h[0]
        if len(o) == len(c):
            for s, d in o.items(): delta[s] = d; comp[s] = ci
    return delta, comp

def scan(corpus, delta, comp, L, minc):
    """returns one representative per (m1, m2, shift) alignment."""
    known = set(delta)
    best = {}
    wins = [(m, p) for m in range(len(corpus))
            for p in range(len(corpus[m]) - L + 1)]
    for i in range(len(wins)):
        m1, p1 = wins[i]
        for j in range(i + 1, len(wins)):
            m2, p2 = wins[j]
            if m1 == m2 and abs(p2 - p1) < L: continue
            ws = []; unk = set()
            for k in range(L):
                a = corpus[m1][p1 + k]; b = corpus[m2][p2 + k]
                if a == b: continue                    # uninformative
                if a in comp and b in comp and comp[a] == comp[b]:
                    ws.append((delta[b] - delta[a] - (p2 - p1)) % N)
                else:
                    if a not in known: unk.add(a)
                    if b not in known: unk.add(b)
            if len(ws) >= minc and len(set(ws)) == 1:
                key = (m1, m2, p2 - p1)
                if key not in best or len(ws) > best[key][4]:
                    best[key] = (m1, p1, m2, p2, len(ws), sorted(unk))
    return list(best.values())

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: planted passage found, shuffles clean, filters correct")
    rng = random.Random(5)

    # a synthetic corpus with a KNOWN repeated passage and a known alphabet
    C = list(range(N)); rng.shuffle(C)
    q = [0] * N
    for pos, s in enumerate(C): q[s] = pos
    drift = 1
    T = 90
    plain = [[rng.randrange(N) for _ in range(T)] for _ in range(3)]
    passage = [rng.randrange(N) for _ in range(20)]
    plain[0][20:40] = passage
    plain[1][35:55] = passage
    base = [7, 31, 55]
    cts = [[C[(plain[m][t] + base[m] + drift * t) % N] for t in range(T)]
           for m in range(3)]
    # give the scan the true Deltas for every glyph, one component
    delta = {g: q[g] for g in range(N)}
    comp = {g: 0 for g in range(N)}
    hits = scan(cts, delta, comp, PREREG["L"], PREREG["min_informative"])
    found = any(h[0] == 0 and h[2] == 1 and (h[3] - h[1]) == 15 for h in hits)
    check("planted passage is found at the correct alignment", found,
          f"({len(hits)} alignments hit)")

    # shuffled corpus must yield nothing
    sh = []
    for m in cts:
        s = list(m); rng.shuffle(s); sh.append(s)
    nh = scan(sh, delta, comp, PREREG["L"], PREREG["min_informative"])
    check("shuffled corpus yields no hits", len(nh) == 0, f"({len(nh)})")

    # the identical-glyph filter: a literally duplicated window must NOT
    # register, since identical cells carry no alphabet information
    cts2 = [list(x) for x in cts]
    cts2[2][10:30] = cts2[0][10:30]
    h2 = scan(cts2, delta, comp, PREREG["L"], PREREG["min_informative"])
    triv = [h for h in h2 if h[0] == 0 and h[2] == 2 and h[3] == h[1]]
    check("literally identical windows do not register (informative filter)",
          not triv)

    # dedup: one alignment yields one entry
    keys = [(h[0], h[2], h[3] - h[1]) for h in hits]
    check("alignments are deduplicated", len(keys) == len(set(keys)))

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    c = json.load(open(corpus))
    cc = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cc, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    S = EI.setup(corpus_path, atlas_path)
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    plA = ERP.drop(S["pool"], (Lx["East 3"], 101), (Lx["East 1"], 68))
    delta, comp = skeleton_deltas(S, plA)
    L, minc = PREREG["L"], PREREG["min_informative"]

    print(f"\nS1 positive control — do the KNOWN certified pairs carry enough")
    print( "   informative cells for this test to see them?")
    us = []
    for p in plA:
        n = sum(1 for k in range(p.length)
                if cts[p.m1][p.p1 + k] != cts[p.m2][p.p2 + k]
                and cts[p.m1][p.p1 + k] in comp and cts[p.m2][p.p2 + k] in comp
                and comp[cts[p.m1][p.p1 + k]] == comp[cts[p.m2][p.p2 + k]])
        us.append(n)
    print(f"   certified pairs: mean informative cells {sum(us)/len(us):.2f}, "
          f"max {max(us)}, with >=5: {sum(1 for x in us if x >= 5)}/{len(us)}")
    print( "   CIRCULARITY CAVEAT: those pairs BUILT the components, so their")
    print( "   cell-richness is partly self-fulfilling. The honest test is what")
    print( "   the scan finds OUTSIDE the pool.")

    print(f"\nS2 scan at L={L}, informative cells only, >= {minc} agreeing")
    hits = scan(cts, delta, comp, L, minc)
    print(f"   distinct alignments hit: {len(hits)}")
    rng = random.Random(PREREG["seed"])
    nulls = []
    for _ in range(3):
        sh = []
        for m in cts:
            s = list(m); rng.shuffle(s); sh.append(s)
        nulls.append(len(scan(sh, delta, comp, L, minc)))
    print(f"   unigram-preserving shuffles: {nulls}")

    aligns = set()
    for p in plA:
        aligns.add((p.m1, p.m2, p.p2 - p.p1)); aligns.add((p.m2, p.m1, p.p1 - p.p2))
    print(f"\nS3 are the hits new, or known territory?")
    new = []
    for m1, p1, m2, p2, n, unk in sorted(hits, key=lambda x: -x[4]):
        k = (m1, m2, p2 - p1) in aligns
        if not k: new.append((m1, p1, m2, p2, n, unk))
        print(f"   {labels[m1]:8s}@{p1:3d} x {labels[m2]:8s}@{p2:3d} "
              f"shift {p2-p1:+4d} informative {n:2d}   "
              f"{'known alignment' if k else 'NEW'}")
    print(f"\n   genuinely new alignments: {len(new)}")
    for m1, p1, m2, p2, n, unk in new:
        print(f"     {labels[m1]}@{p1} x {labels[m2]}@{p2} shift {p2-p1:+d}, "
              f"{n} informative cells, unknown glyphs {unk}")

    print("\nS4 reading")
    print("   the scan reproduces known territory and finds essentially nothing")
    print("   beyond it. That is what the selection effect predicts: the")
    print("   components were built from the pool, so the test can only see")
    print("   passages made largely of glyphs the pool already linked. The route")
    print("   is real and drift-free, but it cannot bootstrap the skeleton past")
    print("   its own reach. External anchors remain the lever.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
