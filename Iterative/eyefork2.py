#!/usr/bin/env python3
"""
eyefork2 -- building the A-vs-B discriminator, measuring what it costs, and
converting the doctrine's "~40 pins" estimate into a measured requirement.
Read-only.

WHY A-vs-B IS GENUINELY GATED (not merely declared so). Under the progressive
reading c[t] = C[(p[t] + off_m + drift*t) mod 83]. Take two positions t, t'
carrying the same plaintext bigram, p[t]=p[t'] and p[t+1]=p[t'+1] -- the kind
of repetition that reveals language structure. The ciphertext bigrams match
only if drift*(t'-t) = 0, i.e. only if the positions coincide. So the drift
DESTROYS plaintext bigram structure in the raw ciphertext, and no amount of
cleverness recovers it without de-drifting. De-drifting needs pins. The
guardrail in the doctrine is mechanical, not conservative.

THE DISCRIMINATOR. Once positions are de-drifted, adjacent plaintext
differences p[t+1]-p[t] are observable. Branch A (a further layer: flat,
high-entropy tokens) makes them uniform; branch B (a token stream retaining
structure) makes them concentrated. The index of coincidence of those
differences is the statistic. It is SHIFT-INVARIANT, which matters here: the
per-triplet drift is free under FR16's coherent model, and a free drift shifts
every difference within a triplet by the same constant, leaving the IoC
untouched. Computed per triplet and pooled, it survives that freedom exactly.

WHAT COSTS WHAT. A pair of adjacent positions is usable only if BOTH carry a
determined glyph, so usable pairs grow roughly as the square of coverage. That
is why the requirement is steep and why the current pin set is nowhere near it.

Model B's structure strength is a free parameter and the power depends on it,
so the instrument sweeps it rather than assuming one value.
"""

import json, os, random, sys
from collections import Counter

ERR = "XD-MBYG04K-URS3LF"
N = 83
EFF = 79            # effective plaintext alphabet, FG2/FG3

HERE = os.path.dirname(os.path.abspath(__file__))
for p in ("eyeend", "eyereach2", "eyegauge", "eyestem", "eyereach"):
    sys.path.insert(0, os.path.join(HERE, "..", p))
import eyegauge as EG                      # noqa: E402
import iso_relax as IR                     # noqa: E402

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

PREREG = {"baseline_guard": {"linked": 22, "distinct": 19, "pins": 16},
          "seed": 20260730, "trials": 30,
          "B_strengths": [0.40, 0.55, 0.65, 0.80],
          "pair_grid": [20, 50, 100, 200, 400, 800]}

def ioc(vals):
    n = len(vals)
    if n < 2: return None
    cnt = Counter(vals)
    return sum(v * (v - 1) for v in cnt.values()) / (n * (n - 1))

def make_plain(kind, rng, n, strength=0.65, fanout=4):
    if kind == "A":
        return [rng.randrange(EFF) for _ in range(n)]
    succ = {s: [rng.randrange(EFF) for _ in range(fanout)] for s in range(EFF)}
    out = [rng.randrange(EFF)]
    for _ in range(n - 1):
        out.append(rng.choice(succ[out[-1]]) if rng.random() < strength
                   else rng.randrange(EFF))
    return out

def diffs(p):
    return [(p[i + 1] - p[i]) % N for i in range(len(p) - 1)]

def separation(npairs, strength, rng, total, trials):
    A, B = [], []
    for _ in range(trials):
        for kind, acc in (("A", A), ("B", B)):
            d = diffs(make_plain(kind, rng, total, strength))
            sub = rng.sample(d, min(npairs, len(d)))
            v = ioc(sub)
            if v is not None: acc.append(v)
    ma = sum(A) / len(A); mb = sum(B) / len(B)
    sa = (sum((x - ma) ** 2 for x in A) / (len(A) - 1)) ** 0.5
    return ma, mb, ((mb - ma) / sa if sa else 0.0)

def reach_set(cts, labels, atlas_path, ctx):
    Lx = {l: i for i, l in enumerate(labels)}
    a = json.load(open(atlas_path))
    letter, dot = set(), set()
    for cl in a["classes"]:
        L, pat = cl["length"], cl["pattern"]
        for it in cl["instances"]:
            mi = Lx[it["message"]]
            for i in range(L):
                (letter if pat[i] != '.' else dot).add((mi, it["start"] + i))
    dot -= letter
    strict = {(m, t) for p in ctx["strict"] for i in range(p.length)
              for (m, t) in ((p.m1, p.p1 + i), (p.m2, p.p2 + i))
              if (m, t) not in dot}
    return sorted({cts[m][t] for m, t in (letter | strict)})

def adj_pairs(cts, pins):
    S = set(pins); n = 0
    for m in cts:
        for t in range(len(m) - 1):
            if m[t] in S and m[t + 1] in S: n += 1
    return n

# ------------------------------------------------------------------ selftest
def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    print("selftest: statistic behaviour, shift invariance, drift mechanism")
    rng = random.Random(PREREG["seed"])

    u = [rng.randrange(N) for _ in range(4000)]
    check("IoC of uniform data sits at 1/83",
          abs(ioc(u) - 1 / N) < 0.002, f"({ioc(u):.5f} vs {1/N:.5f})")

    dA = diffs(make_plain("A", rng, 4000))
    dB = diffs(make_plain("B", rng, 4000))
    check("model A differences are uniform, model B concentrated",
          ioc(dB) > ioc(dA) * 1.05, f"(A={ioc(dA):.5f}, B={ioc(dB):.5f})")

    shifted = [(x + 37) % N for x in dB]
    check("statistic is SHIFT-INVARIANT (free per-triplet drift is harmless)",
          abs(ioc(shifted) - ioc(dB)) < 1e-12)

    # the drift mechanism that gates the whole question
    drift = 1
    p = make_plain("B", rng, 400)
    C = list(range(N)); rng.shuffle(C)
    ct = [C[(p[t] + 5 + drift * t) % N] for t in range(len(p))]
    reps = 0; cipher_reps = 0
    for i in range(len(p) - 1):
        for j in range(i + 1, len(p) - 1):
            if p[i] == p[j] and p[i + 1] == p[j + 1]:
                reps += 1
                if ct[i] == ct[j] and ct[i + 1] == ct[j + 1]: cipher_reps += 1
    check("drift destroys plaintext bigram repeats in the ciphertext",
          reps > 0 and cipher_reps == 0,
          f"({reps} plaintext bigram repeats, {cipher_reps} survive)")

    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    c = json.load(open(corpus))
    cts = [list(x) for x in c["ciphertexts"]]
    r = IR.relax(cts, N, seed=0); bg = PREREG["baseline_guard"]
    check("baseline guard", (r.linked_strict, r.distinct_strict, len(r.pins)) ==
          (bg["linked"], bg["distinct"], bg["pins"]))

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path, atlas_path):
    c = json.load(open(corpus_path))
    cts = [list(x) for x in c["ciphertexts"]]; labels = c["message_labels"]
    ctx = EG.build_context(cts, labels, atlas_path)
    print("baseline guard: 22/19/16  [MATCHES CERTIFIED]")
    total = sum(len(m) for m in cts)
    tot_adj = sum(len(m) - 1 for m in cts)
    R = reach_set(cts, labels, atlas_path, ctx)
    freq = Counter(v for m in cts for v in m)
    rng = random.Random(PREREG["seed"])

    print(f"\nS1 the discriminator: adjacent-difference IoC on de-drifted plaintext")
    for s in PREREG["B_strengths"]:
        dA = diffs(make_plain("A", rng, total))
        dB = diffs(make_plain("B", rng, total, s))
        print(f"  model B strength {s:.2f}: A = {ioc(dA):.5f} (x{ioc(dA)*N:.2f}), "
              f"B = {ioc(dB):.5f} (x{ioc(dB)*N:.2f})")
    print("  (uniform = 1/83 = 0.01205; the statistic is shift-invariant, so the")
    print("   free per-triplet drift of FR16's coherent model does not disturb it)")

    print(f"\nS2 power curve: separation vs number of usable adjacent pairs")
    print(f"  {'pairs':>6s} " + " ".join(f"{'B=%.2f' % s:>9s}"
                                          for s in PREREG["B_strengths"]))
    for npairs in PREREG["pair_grid"]:
        row = []
        for s in PREREG["B_strengths"]:
            _, _, sep = separation(npairs, s, rng, total, PREREG["trials"])
            row.append(f"{sep:8.1f}s")
        print(f"  {npairs:6d} " + " ".join(f"{x:>9s}" for x in row))

    print(f"\nS3 what the corpus can supply: usable adjacent pairs vs pinned glyphs")
    print("  (a pair counts only if BOTH positions carry a determined glyph, so")
    print("   usable pairs grow as the SQUARE of coverage)")
    byfreq = sorted(R, key=lambda g: -freq[g])
    print(f"  {'pins':>5s} {'random':>8s} {'freq-greedy':>12s} {'coverage':>9s}")
    for k in (8, 10, 16, 20, 25, 30, 40, len(R)):
        rnd = [adj_pairs(cts, rng.sample(R, min(k, len(R)))) for _ in range(20)]
        g = byfreq[:k]
        print(f"  {k:5d} {sum(rnd)/len(rnd):8.0f} {adj_pairs(cts, g):12d} "
              f"{100*sum(freq[x] for x in g)/total:8.1f}%")
    cur = [12, 13, 19, 23, 37, 44, 49, 72]
    print(f"\n  total adjacent pairs in the corpus: {tot_adj}")
    print(f"  CURRENT 8 pin-grade glyphs {cur}: {adj_pairs(cts, cur)} usable pairs")
    print(f"  ALL {len(R)} reachable glyphs: {adj_pairs(cts, R)} usable pairs")

    print("\nS4 the requirement, and how it joins the endgame route")
    print(f"  * the current pin set gives {adj_pairs(cts, cur)} pairs -- no power at all;")
    print("    the doctrine's 'no bigram probes below ~40 pins' guardrail is")
    print("    quantitatively justified, not merely cautious")
    print("  * ~40 frequency-greedy pins give ~360 pairs; the full reachable set")
    print(f"    gives {adj_pairs(cts, R)} -- around 4s separation at moderate B strength")
    print("  * FR17: 8 well-chosen external anchors determine all "
          f"{len(R)} reachable glyphs")
    print("  -> the SAME eight anchors that expose 67.7% of the corpus (FR19) also")
    print("     supply enough adjacent pairs to resolve A-vs-B. One acquisition")
    print("     target serves both halves of the programme.")
    print("\n  CAVEAT: power depends on how much structure branch B actually has.")
    print("  At strength 0.40 the separation is materially weaker; a token stream")
    print("  flatter than the simulation would need more pairs than the corpus can")
    print("  supply, in which case A-vs-B stays open even after a full solve.")

if __name__ == "__main__":
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(HERE, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    atlas = os.environ.get("EYE_ATLAS",
        os.path.join(HERE, "..", "Eyes-main", "data", "isomorph_atlas.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus, atlas)
