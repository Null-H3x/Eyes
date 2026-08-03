#!/usr/bin/env python3
"""
eyeclass2 -- auditing the second of the model's two load-bearing pieces.
Read-only.

WHY. FR49's sensitivity map showed the model rests on exactly two pieces of
evidence: the FR32/33 passage (161 relations) and class #2 (159). The passage
was audited in FR48 and re-priced at 3.6e-6. Class #2 had never been examined
individually the way FR15 examined the cross-triplet bridges, and it is a long
class (L = 30) with only three instances, which makes its skeleton weight the
thing to establish.

RESULT. It audits clean and strong. Five skeleton equal-pairs give a chance of
83^-5 per window, about 2e-7 across the 775 windows the corpus offers; the
pattern matches exactly its own three instances and nothing else; and 2000
unigram-preserving shuffled corpora produce zero matches. No instance weakens
the class.

ONE OBSERVATION WORTH RECORDING. East 5 @ 69 is STANDALONE -- it sits inside
no larger certified passage, which is the property FR27 used against E1@68.
The two cases are not comparable, and the reason is the skeleton weight: #M
carries three equal-pairs (chance ~1 in 600 corpus-wide) while #2 carries five
(chance ~2e-7). A standalone instance of a class this heavy is not
surprising; a standalone instance of a class as light as #M is.
"""

import json, os, random, sys
from collections import Counter
from itertools import combinations

ERR = "XD-MBYG04K-URS3LF"
N = 83

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeaudit2", "eyecirc", "eyerepair2", "eyeaudit", "eyeinject",
          "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyeinject as EI                     # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "target": "#2", "shuffles": 2000, "seed": 20260901}

def klass(atlas, cid):
    return next(c for c in atlas["classes"] if c["id"] == cid)

def skeleton(cl):
    L, pat = cl["length"], cl["pattern"]
    return L, [(i, j) for i in range(L) for j in range(i + 1, L)
               if pat[i] != '.' and pat[i] == pat[j]]

def matches(seq, L, sk):
    return sum(1 for p in range(len(seq) - L + 1)
               if all(seq[p + i] == seq[p + j] for i, j in sk))

def shared_skeleton(cts, Lx, inst, L):
    out = None
    for m, p in inst:
        w = cts[Lx[m]][p:p + L]
        e = {(i, j) for i in range(L) for j in range(i + 1, L) if w[i] == w[j]}
        out = e if out is None else (out & e)
    return out or set()

def parents(atlas, msg, start, L, cid):
    out = []
    for c in atlas["classes"]:
        if c["id"] == cid: continue
        for it in c["instances"]:
            if it["message"] == msg and it["start"] <= start \
               and start + L <= it["start"] + c["length"]:
                out.append(f"{c['id']}@{it['start']}")
    return out

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: matcher, null calibration, weakening detector")
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas_p = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    S = EI.setup(corpus, atlas_p)
    Lx, cts, labels = S["Lx"], S["cts"], S["labels"]
    atlas = json.load(open(atlas_p))
    cl = klass(atlas, PREREG["target"])
    L, sk = skeleton(cl)

    check("class #2 has a five-pair skeleton over length 30",
          L == 30 and len(sk) == 5, f"(L={L}, k={len(sk)})")

    inst = [(it["message"], it["start"]) for it in cl["instances"]]
    check("every instance satisfies the skeleton",
          all(all(cts[Lx[m]][p + i] == cts[Lx[m]][p + j] for i, j in sk)
              for m, p in inst))

    tot = sum(matches(cts[Lx[m]], L, sk) for m in labels)
    check("the pattern matches exactly its own instances corpus-wide",
          tot == len(inst), f"({tot} matches, {len(inst)} instances)")

    # a genuinely weaker skeleton must match more often -- calibration.
    # (sk[:2] is NOT weaker in practice: those two pairs are still restrictive
    # over a 30-long window, which is itself worth knowing.)
    weak = [sk[0]]
    totw = sum(matches(cts[Lx[m]], L, weak) for m in labels)
    wins = sum(max(0, len(cts[Lx[m]]) - L + 1) for m in labels)
    check("a one-pair skeleton matches at the CHANCE rate (calibration)",
          abs(totw - wins / N) < 3 * (wins / N) ** 0.5,
          f"({totw} observed, {wins/N:.1f} expected by chance)")

    rng = random.Random(PREREG["seed"])
    nulls = 0
    for _ in range(50):
        for m in labels:
            s = list(cts[Lx[m]]); rng.shuffle(s)
            nulls += matches(s, L, sk)
    check("shuffles produce essentially nothing", nulls == 0, f"({nulls})")

    kall = len(shared_skeleton(cts, Lx, inst, L))
    check("no instance weakens the class",
          all(len(shared_skeleton(cts, Lx, [y for y in inst if y != x], L)) == kall
              for x in inst), f"(k={kall})")

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
    atlas = json.load(open(atlas_path))
    cl = klass(atlas, PREREG["target"])
    L, sk = skeleton(cl)
    inst = [(it["message"], it["start"]) for it in cl["instances"]]
    TRI = {"T1": ["East 1", "West 1", "East 2"],
           "T2": ["West 2", "East 3", "West 3"],
           "T3": ["East 4", "West 4", "East 5"]}
    tri = {m: t for t, ms in TRI.items() for m in ms}
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")

    print(f"\nQ1 class {PREREG['target']} — the object")
    print(f"  length {L}, pattern {cl['pattern']}")
    print(f"  skeleton equal-pairs k = {len(sk)} at {sk}")
    print(f"  instances {inst}, triplets {[tri[m] for m, _ in inst]}")

    print("\nQ2 pattern weight")
    wins = sum(max(0, len(cts[Lx[m]]) - L + 1) for m in labels)
    print(f"  chance per window 83^-{len(sk)} = {83.0**-len(sk):.2e}")
    print(f"  windows corpus-wide {wins}; expected chance matches "
          f"{wins*83.0**-len(sk):.2e}")
    hits = {m: matches(cts[Lx[m]], L, sk) for m in labels}
    print(f"  actual matches per message: "
          f"{ {m: n for m, n in hits.items() if n} }")
    print("  -> exactly its own three instances, nothing spurious anywhere")

    print("\nQ3 shuffle null")
    rng = random.Random(PREREG["seed"])
    tot = 0
    for _ in range(PREREG["shuffles"]):
        for m in labels:
            s = list(cts[Lx[m]]); rng.shuffle(s)
            tot += matches(s, L, sk)
    print(f"  matches across {PREREG['shuffles']} shuffled corpora: {tot}")

    print("\nQ4 embeddedness, instance by instance")
    for m, p in inst:
        par = parents(atlas, m, p, L, cl["id"])
        print(f"  {m:8s}@{p:3d}: "
              f"{'inside ' + ', '.join(par) if par else 'STANDALONE'}")
    print("  East 5 @ 69 is standalone -- the property FR27 used against E1@68")

    print("\nQ5 why that is not the same situation")
    mcl = klass(atlas, "#M"); mL, msk = skeleton(mcl)
    mwins = sum(max(0, len(cts[Lx[m]]) - mL + 1) for m in labels)
    print(f"  class #M : k = {len(msk)}, expected chance matches "
          f"{mwins*83.0**-len(msk):.4f}")
    print(f"  class #2 : k = {len(sk)}, expected chance matches "
          f"{wins*83.0**-len(sk):.2e}")
    print("  a standalone instance of a class this heavy is unremarkable; a")
    print("  standalone instance of a class as light as #M is the anomaly FR27")
    print("  identified. The comparison turns on skeleton weight, not on")
    print("  standalone-ness by itself.")

    print("\nQ6 verdict")
    print("  class #2 is strongly supported and internally uniform. Both of the")
    print("  model's load-bearing pieces are now audited: the passage at 3.6e-6")
    print(f"  (FR48) and class #2 at {wins*83.0**-len(sk):.0e} (here).")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
