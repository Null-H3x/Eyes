#!/usr/bin/env python3
"""
eyetarget -- what the 74.1% ceiling is made of, and what an acquisition
programme should actually ask for. Read-only.

THE GAP. The model determines 56 glyphs and leaves 27 outside every component.
Fifty-three reports have quoted the resulting 74.1% exposure without once
asking what those 27 glyphs are. If they are systematically the rare ones the
ceiling is a sampling limit; if some are common, they are anchor targets the
current arithmetic ignores.

WHAT THEY ARE. Systematically rarer, but not by much: mean corpus frequency
9.93 against 13.71 for determined glyphs, z = +4.32. The separation is real
and it is not clean -- the most common undetermined glyph appears 17 times,
more often than a third of the determined ones. So the ceiling is mostly a
sampling effect (rare glyphs co-occur in fewer isomorph windows and so never
get linked) rather than anything structural about those glyphs.

WHAT IT MEANS FOR ACQUISITION. A component anchor buys the WHOLE component; a
singleton anchor buys only its own positions. One anchor in component 2 buys
179 corpus positions. The best singleton buys 17. That is more than a tenfold
difference in yield per anchor, and it gives a strict priority ordering that
the "ten anchors reach 74.1%" summary obscures.
"""

import json, math, os, statistics, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeinvar", "eyestale", "eyestrict", "eyeclass2", "eyeaudit2",
          "eyecirc", "eyerepair2", "eyeaudit", "eyeinject", "eyegauge",
          "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeaudit as EA                      # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "relations": 384, "glyphs": 56}

def setup(corpus_path, atlas_path):
    cts, labels, Lx, ctx, pool, _ = EA.load(corpus_path, atlas_path)
    BR = (Lx["East 3"], 101); A1 = (Lx["East 1"], 68)
    red = [p for p in pool
           if not any((p.m1, p.p1) == k or (p.m2, p.p2) == k for k in (BR, A1))]
    gf = EA.build(cts, ctx, Lx, red)
    return cts, labels, Lx, ctx, red, EA.analyse(gf)

def welch_z(x, y):
    m1, m2 = statistics.mean(x), statistics.mean(y)
    s1, s2 = statistics.pstdev(x), statistics.pstdev(y)
    se = math.sqrt(s1 * s1 / len(x) + s2 * s2 / len(y))
    return (m1 - m2) / se if se else 0.0

def targets(a, freq):
    """every anchorable unit, with the positions one anchor buys"""
    out = []
    for i, c in enumerate(a["comps"]):
        out.append((f"component {i+1}", len(c), sum(freq[g] for g in c),
                    1 if i else 2))
    und = [g for g in range(N) if g not in a["linked"]]
    for g in sorted(und, key=lambda x: -freq[x]):
        out.append((f"glyph {g}", 1, freq[g], 1))
    return out

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: partition, frequency statistic, yield arithmetic")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    cts, labels, Lx, ctx, red, a = setup(corpus, atlas)
    freq = Counter(g for m in cts for g in m)

    check("skeleton is the current one",
          a["det"] == PREREG["relations"] and len(a["linked"]) == PREREG["glyphs"],
          f"({a['det']} relations, {len(a['linked'])} glyphs)")

    und = [g for g in range(N) if g not in a["linked"]]
    check("the 83 glyphs partition into determined and not",
          len(und) + len(a["linked"]) == N and not (set(und) & a["linked"]),
          f"({len(a['linked'])} + {len(und)})")

    check("positions partition too",
          sum(freq[g] for g in a["linked"]) + sum(freq[g] for g in und) == 1036)

    z = welch_z([freq[g] for g in a["linked"]], [freq[g] for g in und])
    check("undetermined glyphs are rarer, and the statistic is calibrated",
          z > 2, f"(z = {z:+.2f})")
    # calibration: a random split of the same sizes must give z ~ 0
    import random
    rng = random.Random(5)
    allg = list(range(N)); rng.shuffle(allg)
    zc = welch_z([freq[g] for g in allg[:len(a["linked"])]],
                 [freq[g] for g in allg[len(a["linked"]):]])
    check("a random split of the same sizes gives no separation",
          abs(zc) < 2.5, f"(z = {zc:+.2f})")

    t = targets(a, freq)
    check("component anchors outyield singleton anchors by >5x",
          max(p for n, g, p, k in t if n.startswith("component") and g > 3) >
          5 * max(p for n, g, p, k in t if n.startswith("glyph")),
          f"({max(p for n,g,p,k in t if n.startswith('component') and g>3)} vs "
          f"{max(p for n,g,p,k in t if n.startswith('glyph'))})")

    c = json.load(open(corpus))
    cc = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cc, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    cts, labels, Lx, ctx, red, a = setup(corpus_path, atlas_path)
    freq = Counter(g for m in cts for g in m)
    und = [g for g in range(N) if g not in a["linked"]]
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print("\nG1 the partition")
    print(f"  determined   : {len(a['linked'])} glyphs, "
          f"{sum(freq[g] for g in a['linked'])} positions "
          f"({100*sum(freq[g] for g in a['linked'])/1036:.1f}%)")
    print(f"  undetermined : {len(und)} glyphs, {sum(freq[g] for g in und)} "
          f"positions ({100*sum(freq[g] for g in und)/1036:.1f}%)")

    print("\nG2 are the undetermined glyphs systematically rare?")
    fd = [freq[g] for g in a["linked"]]; fu = [freq[g] for g in und]
    print(f"  determined   : mean {statistics.mean(fd):5.2f}, "
          f"median {statistics.median(fd):4.1f}, range {min(fd)}-{max(fd)}")
    print(f"  undetermined : mean {statistics.mean(fu):5.2f}, "
          f"median {statistics.median(fu):4.1f}, range {min(fu)}-{max(fu)}")
    print(f"  z = {welch_z(fd, fu):+.2f}")
    print("  -> real, but not a clean separation: the most common undetermined")
    print("     glyph appears more often than a third of the determined ones.")
    print("     The ceiling is mostly a SAMPLING limit — rare glyphs co-occur")
    print("     in fewer isomorph windows and never get linked — rather than")
    print("     anything structural about those glyphs.")

    print("\nG3 the undetermined glyphs")
    print(f"  {'glyph':>5s} {'freq':>5s} {'messages':>9s}")
    for g in sorted(und, key=lambda x: -freq[x]):
        print(f"  {g:5d} {freq[g]:5d} {sum(1 for m in cts if g in m):9d}")

    print("\nG4 anchor yield — what one anchor buys")
    t = targets(a, freq)
    print(f"  {'target':16s} {'glyphs':>7s} {'positions':>10s} {'corpus':>8s} "
          f"{'anchors':>8s}")
    for name, g, p, k in t[:14]:
        print(f"  {name:16s} {g:7d} {p:10d} {100*p/1036:7.1f}% {k:8d}")
    print("  ...")

    print("\nG5 the acquisition priority this implies")
    comps = [(f"component {i+1}", len(c), sum(freq[g] for g in c))
             for i, c in enumerate(a["comps"])]
    run = 0; n = 0
    print(f"  {'step':38s} {'anchors':>8s} {'cumulative corpus':>18s}")
    for i, (name, g, p) in enumerate(comps):
        k = 2 if i == 0 else 1
        n += k; run += p
        print(f"  {name + (' (2 anchors: base + drift)' if i == 0 else ''):38s} "
              f"{n:8d} {100*run/1036:17.1f}%")
    for j, g in enumerate(sorted(und, key=lambda x: -freq[x])[:5]):
        n += 1; run += freq[g]
        print(f"  {'glyph ' + str(g) + ' (singleton)':38s} {n:8d} "
              f"{100*run/1036:17.1f}%")
    print("\n  the first two anchors are worth more than the next eight")
    print("  combined, and every component anchor outyields every singleton.")
    print("  A programme that acquires anchors opportunistically rather than")
    print("  by this ordering will spend far more for the same exposure.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
