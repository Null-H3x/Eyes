#!/usr/bin/env python3
"""alphabet_sweep -- exhaustively disposition structured alphabet families.

THE IDEA
========
The devs had to BUILD the mixed alphabet C somehow.  The realistic
construction space for a human-designed puzzle is small and enumerable:
natural order, affine/multiplicative scrambles, tricks on the glyphs' own
base-5 trigram digits, deck-style deals, keyword-columnar mixes, or PRNG
output.  EyeStat burned 34+ billion seeds against the PRNG corner (null);
nobody has swept the STRUCTURED corner, because until ordering_bridge there
was no cheap scorer.  Now a candidate costs microseconds (batch gsupport on
GPU/NumPy) and a survivor costs minutes (bridge verdict with readability
gates), so the right move is to enumerate whole families and disposition
them: either a construction lights up at permutation-null z << -6 and then
must survive the bridge's read, or the family is EXCLUDED and the key
retreats into "PRNG under an untested family or a non-alphabet source" --
a publishable narrowing either way.

WHAT ABSORBS, AND WHY THE COUNTS ARE SMALL
==========================================
support((q + const) mod N) == support(q): a global rotation of positions is
absorbed by base_m in the model, and the distinct-residue count is shift-
invariant.  Consequences, so the families dedupe BY CONSTRUCTION:
  * affine q[v] = (a*v + b) : b drops       -> 82 candidates (a = 1..82)
  * power  q[v] = a * v^k   : k=1 dups affine -> 39 exponents x 82
  * pre-shift power a*(v+b)^k : k=1 collapses into affine for ALL b
Every candidate is a FULL q, so verdicts ride ordering_bridge's fast path:
no annealing, no completed-q circularity caveats.

FAMILIES
========
affine    q[v] = a*v                                   (82)
power     q[v] = a*v^k, gcd(k,82)=1, k!=1, 0^k=0       (3,198)
prepower  q[v] = a*(v+b)^k, k!=1, b=1..82              (262,236)
trigram   per-digit S5 substitutions + digit-position permutation on the
          base-5 trigram (d2,d1,d0), FILTERED to maps closed on {0..82}
          (the glyph set is 83 of 125 trigrams; most maps leak out)
deals     deal 0..82 into k piles (k=2..41), pickup natural/reversed,
          optionally deck-reversed first; BOTH orientations (320)
keyword   classic columnar transposition of 0..82 keyed by wordlist words
          (rank tuple of the word's letters orders the columns), deduped
          by rank tuple across the shipped en/fi/krl wordlists; BOTH
          orientations

ORIENTATION: unlike the algebraic families (closed under inversion: a
C-side affine/power/prepower construction is a q-side family member after
the additive constant absorbs, and the trigram set is a group restricted
to its closed subset), deals and keyword are NOT inversion-closed -- the
inverse of a k-pile deal is an interleave, the inverse of a columnar read
is a row-wise read.  "The devs built C this way" and "the devs built q
this way" are distinct hypotheses, so both are emitted (orient=C / q).

HONEST LIMITS
=============
* This dispositions CONSTRUCTIONS OF q AS A MAP ON VALUE INDICES.  If the
  devs built C over a different latent labeling of the glyphs (e.g. sorted
  by first appearance), a structured construction there looks unstructured
  here.  Family exclusion is exclusion of the construction IN THIS FRAME.
* trigram/keyword families overlap affine at their identity corners; exact
  dedup is enforced only within affine+power+prepower (disjoint by
  construction).  Cross-family duplicates cost rescoring, not correctness.
* The support filter is necessary, not sufficient: survivors must pass the
  bridge's readability-gated read before anyone gets excited.  z floors
  here follow support_min's calibration (true q lives at -15..-32; the
  survivor line -6 is conservative for millions of comparisons).

THE MIRROR IDENTITY (an unconditional redundancy)
=================================================
support(q, drift) == support(-q, -drift) IDENTICALLY, for any corpus and
any q: negating q negates the residues, a bijection, so the distinct count
cannot change -- the Beaufort equivalence surfacing in the sweep.  Two
consequences.  (1) For negation-CLOSED families (affine, power, prepower:
-a is in-family) the drift -1 column exactly duplicates drift +1 under
a -> -a; the real-corpus output shows this as every candidate appearing
twice at identical z (e.g. 17@+1 with 66@-1, since 66 = -17 mod 83).  The
redundancy is kept because for NON-closed families (trigram, deals,
keyword) the negated construction is NOT in-family, and there the drift -1
column is genuine new coverage.  (2) A true hit therefore always arrives
as a pair in closed families (the selftest plants confirm), and any
survivor's mirror is worth checking by hand in open ones.
"""

from __future__ import annotations

import argparse
import math
import sys
from itertools import permutations
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

import numpy as np

HERE = Path(__file__).resolve().parent
for p in (HERE, HERE.parent / "noita_eye_core"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import plantlab                                            # noqa: E402
import order_gpu                                           # noqa: E402
import ordering_bridge                                     # noqa: E402

N_DEFAULT = 83
Z_SURVIVOR = -6.0     # permutation-null z to advance to the bridge
NULL_R = 200          # random permutations for null calibration
CHUNK = 1024          # batch_support onehot is (B,M,L,N): ~100MB at 1024

Candidate = Tuple[str, np.ndarray]     # (label, q array)


# --------------------------------------------------------------------------
# family generators -- each yields (label, q) with q a permutation of 0..N-1
# --------------------------------------------------------------------------
def fam_affine(N: int = N_DEFAULT) -> Iterator[Candidate]:
    v = np.arange(N)
    for a in range(1, N):
        yield (f"affine a={a}", (a * v) % N)


def _prime_exponents(N: int) -> List[int]:
    return [k for k in range(2, N - 1) if math.gcd(k, N - 1) == 1]


def fam_power(N: int = N_DEFAULT) -> Iterator[Candidate]:
    v = np.arange(N)
    for k in _prime_exponents(N):
        vk = np.array([pow(int(x), k, N) for x in v])
        for a in range(1, N):
            yield (f"power a={a} k={k}", (a * vk) % N)


def fam_prepower(N: int = N_DEFAULT) -> Iterator[Candidate]:
    v = np.arange(N)
    for k in _prime_exponents(N):
        for b in range(1, N):
            vk = np.array([pow(int(x + b) % N, k, N) for x in v])
            for a in range(1, N):
                yield (f"prepower a={a} b={b} k={k}", (a * vk) % N)


def _digits(N: int = N_DEFAULT) -> np.ndarray:
    v = np.arange(N)
    return np.stack([v // 25, (v // 5) % 5, v % 5], axis=1)   # (N,3)


def fam_trigram(N: int = N_DEFAULT, limit: Optional[int] = None
                ) -> Iterator[Candidate]:
    """Digit-wise S5 substitutions + digit-position permutation, closed maps.

    Closure filter is vectorized per (pi, sigma2) slab: for each of the 6
    position orders and 120 top-digit substitutions, all 14400 (s1, s0)
    pairs are checked at once against the valid-value predicate."""
    D = _digits(N)                                            # (N,3)
    perms5 = np.array(list(permutations(range(5))))           # (120,5)
    emitted = 0
    for pi in permutations(range(3)):
        Dp = D[:, list(pi)]                                   # (N,3) permuted
        for i2 in range(120):
            s2 = perms5[i2]
            d2 = s2[Dp[:, 0]]                                 # (N,)
            # values for all (s1,s0): 25*d2 + 5*s1[d1] + s0[d0]
            d1all = perms5[:, Dp[:, 1]]                       # (120,N)
            d0all = perms5[:, Dp[:, 2]]                       # (120,N)
            vals = (25 * d2)[None, None, :] \
                + 5 * d1all[:, None, :] + d0all[None, :, :]   # (120,120,N)
            closed = (vals < N).all(axis=2)                   # (120,120)
            for i1, i0 in zip(*np.nonzero(closed)):
                q = vals[i1, i0]
                # closure onto <N of an injective 125-map == permutation,
                # but assert cheaply anyway (paranoia beats proofs).
                if len(np.unique(q)) == N:
                    yield (f"trigram pi={pi} s2={i2} s1={i1} s0={i0}",
                           q.astype(np.int64))
                    emitted += 1
                    if limit and emitted >= limit:
                        return


def fam_deals(N: int = N_DEFAULT) -> Iterator[Candidate]:
    base = np.arange(N)
    for rev in (False, True):
        deck = base[::-1].copy() if rev else base
        for k in range(2, 42):
            piles = [deck[i::k] for i in range(k)]
            for pick, order in (("nat", range(k)),
                                ("rev", range(k - 1, -1, -1))):
                C = np.concatenate([piles[i] for i in order])
                q = np.empty(N, dtype=np.int64)
                q[C] = np.arange(N)
                yield (f"deal k={k} pick={pick} rev={int(rev)} orient=C", q)
                yield (f"deal k={k} pick={pick} rev={int(rev)} orient=q",
                       C.copy())


def _rank_tuple(word: str) -> Tuple[int, ...]:
    """Column read order for classic keyed columnar transposition."""
    order = sorted(range(len(word)), key=lambda i: (word[i], i))
    return tuple(order)


def _keyed_columnar_C(ranks: Sequence[int], N: int) -> np.ndarray:
    w = len(ranks)
    cols = [list(range(c, N, w)) for c in range(w)]
    return np.array([i for r in ranks for i in cols[r]], dtype=np.int64)


def fam_keyword(N: int = N_DEFAULT, min_len: int = 3, max_len: int = 13,
                limit: Optional[int] = None) -> Iterator[Candidate]:
    est = HERE.parent / "eyestat"
    seen: set = set()
    emitted = 0
    for fn in ("eng-wordlist.txt", "extra_words_fi.txt",
               "extra_words_krl.txt"):
        p = est / fn
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8",
                                errors="ignore").splitlines():
            w = line.strip().lower()
            if not (min_len <= len(w) <= max_len) or not w.isalpha():
                continue
            rk = _rank_tuple(w)
            if rk in seen:
                continue
            seen.add(rk)
            C = _keyed_columnar_C(rk, N)
            q = np.empty(N, dtype=np.int64)
            q[C] = np.arange(N)
            yield (f"keyword '{w}' ranks={rk} orient=C", q)
            yield (f"keyword '{w}' ranks={rk} orient=q", C.copy())
            emitted += 2
            if limit and emitted >= limit:
                return


FAMILIES = {"affine": fam_affine, "power": fam_power,
            "prepower": fam_prepower, "trigram": fam_trigram,
            "deals": fam_deals, "keyword": fam_keyword}


# --------------------------------------------------------------------------
# the engine
# --------------------------------------------------------------------------
def null_calibration(cts, N: int, xp=None, R: int = NULL_R,
                     seed: int = 0) -> Dict[int, Tuple[float, float]]:
    """(mu, sd) of batch support under random permutations, per drift."""
    rng = np.random.default_rng(seed)
    Q = np.stack([rng.permutation(N) for _ in range(R)])
    out = {}
    for drift, corpus in ((1, cts), (-1, [list(c)[::-1] for c in cts])):
        s = np.asarray(order_gpu.batch_support(Q, corpus, N, xp=xp))
        out[drift] = (float(s.mean()), float(s.std()) or 1e-9)
    return out


def sweep(candidates: Iterable[Candidate], cts, N: int = N_DEFAULT, *,
          xp=None, chunk: int = CHUNK, topk: int = 50,
          null: Optional[Dict[int, Tuple[float, float]]] = None,
          seed: int = 0) -> dict:
    """Score candidates at both drifts; keep top-k and all survivors.

    Returns {"scored": n, "top": [(zbest, drift, label)...],
             "survivors": [(zbest, drift, label, q)...]}   (z ascending)"""
    null = null or null_calibration(cts, N, xp=xp, seed=seed)
    rev = [list(c)[::-1] for c in cts]
    top: List[Tuple[float, int, str]] = []
    survivors: List[Tuple[float, int, str, List[int]]] = []
    n_scored = 0
    labels: List[str] = []
    batch: List[np.ndarray] = []

    def flush():
        nonlocal n_scored
        if not batch:
            return
        Q = np.stack(batch)
        for drift, corpus in ((1, cts), (-1, rev)):
            s = np.asarray(order_gpu.batch_support(Q, corpus, N, xp=xp))
            mu, sd = null[drift]
            z = (s - mu) / sd
            for i in np.nonzero(z <= Z_SURVIVOR)[0]:
                survivors.append((float(z[i]), drift, labels[i],
                                  [int(x) for x in Q[i]]))
            for i in np.argsort(z)[:min(len(z), topk)]:
                top.append((float(z[i]), drift, labels[i]))
        n_scored += len(batch)
        top.sort()
        del top[topk:]
        labels.clear()
        batch.clear()

    for label, q in candidates:
        labels.append(label)
        batch.append(np.asarray(q))
        if len(batch) >= chunk:
            flush()
    flush()
    survivors.sort()
    return {"scored": n_scored, "top": top, "survivors": survivors,
            "null": null}


def verdict_survivors(result: dict, cts, N: int = N_DEFAULT, *, bank=None,
                      max_verdicts: int = 5, read_restarts: int = 8,
                      read_iters: int = 16000, seed: int = 0) -> List[dict]:
    """Stage 2: run the bridge's readability-gated verdict on survivors."""
    cards = []
    for zb, drift, label, q in result["survivors"][:max_verdicts]:
        hyp = ordering_bridge.normalize(N, q=q, label=label)
        card = ordering_bridge.scorecard(cts, N, hyp, bank=bank,
                                         read_restarts=read_restarts,
                                         read_iters=read_iters, seed=seed)
        card["sweep_z"] = zb
        card["sweep_drift"] = drift
        cards.append(card)
    return cards


# --------------------------------------------------------------------------
# plants for the audit
# --------------------------------------------------------------------------
def _plant_with_q(q: np.ndarray, *, seed: int = 0, drift: int = 1,
                  shared_prefix: int = 20):
    """Re-encrypt a pmp plant's ground truth under a SPECIFIED q."""
    pl = plantlab.gen("pmp", seed=seed, shared_prefix=shared_prefix)
    N = pl.N
    C = np.empty(N, dtype=np.int64)
    C[np.asarray(q)] = np.arange(N)
    cts = [[int(C[(pv + pl.bases[m] + drift * t) % N])
            for t, pv in enumerate(pl.pvals[m])]
           for m in range(len(pl.pvals))]
    pl.cts = cts
    pl.q = [int(x) for x in q]
    return pl


# --------------------------------------------------------------------------
# selftest -- the paranoia audit
# --------------------------------------------------------------------------
def selftest() -> List[Tuple[str, bool]]:
    checks: List[Tuple[str, bool]] = []
    N = N_DEFAULT
    rng = np.random.default_rng(0)

    # (1) family validity + exact counts where formulas exist.
    aff = list(fam_affine(N))
    ok = (len(aff) == 82 and
          all(sorted(q.tolist()) == list(range(N)) for _, q in aff))
    checks.append((f"affine: {len(aff)} valid permutations", ok))
    pw = list(fam_power(N))
    ok = (len(pw) == 39 * 82 and
          all(sorted(pw[i][1].tolist()) == list(range(N))
              for i in rng.choice(len(pw), 40, replace=False)))
    checks.append((f"power: {len(pw)} candidates (39 exps x 82)", ok))
    dl = list(fam_deals(N))
    ok = (len(dl) == 320 and
          all(sorted(q.tolist()) == list(range(N)) for _, q in dl))
    checks.append((f"deals: {len(dl)} valid perms (both orientations)", ok))
    # orientation pairs are mutual inverses
    qC, qq = dl[0][1], dl[1][1]
    checks.append(("deals: orient=C/q are mutual inverses",
                   all(qq[qC[i]] == i for i in range(N))))

    # (2) affine+power mutually distinct (dedup-by-construction holds).
    seen = {tuple(q.tolist()) for _, q in aff}
    dup = sum(tuple(q.tolist()) in seen for _, q in pw)
    checks.append((f"affine/power disjoint (overlaps={dup})", dup == 0))

    # (3) trigram: emitted maps are closed permutations; identity present.
    tri = list(fam_trigram(N, limit=4000))
    ok = all(sorted(q.tolist()) == list(range(N)) for _, q in tri[:200])
    ident = any((q == np.arange(N)).all() for _, q in tri)
    checks.append((f"trigram: {len(tri)} closed maps, identity found",
                   ok and ident and len(tri) > 0))

    # (4) keyword: hand-checked KAT of the columnar construction.
    #     word 'bad' -> ranks (1,0,2); N=6, width 3: cols [0,3],[1,4],[2,5]
    #     read order 1,0,2 -> C = [1,4,0,3,2,5].
    ok = (_rank_tuple("bad") == (1, 0, 2) and
          _keyed_columnar_C((1, 0, 2), 6).tolist() == [1, 4, 0, 3, 2, 5])
    checks.append(("keyword: columnar KAT ('bad', N=6)", ok))
    kw = list(fam_keyword(N, limit=300))
    ok = (len(kw) == 300 and
          all(sorted(q.tolist()) == list(range(N)) for _, q in kw[:50]))
    checks.append(("keyword: wordlist stream yields valid perms", ok))
    qC2, qq2 = kw[0][1], kw[1][1]
    checks.append(("keyword: orient=C/q are mutual inverses",
                   all(qq2[qC2[i]] == i for i in range(N))))

    # (5) engine z == scalar gsupport z, spot-checked through the wrapper.
    pl = plantlab.gen("pmp", seed=2, shared_prefix=20)
    null = null_calibration(pl.cts, N, seed=1)
    res = sweep(aff[:9], pl.cts, N, null=null, chunk=4)
    mu, sd = null[1]
    lab, q = aff[3]
    zs = (ordering_bridge.gsupport(q.tolist(), pl.cts, N, 1) - mu) / sd
    zw = next(z for z, d, l in res["top"] if l == lab and d == 1)
    checks.append((f"engine z matches scalar gsupport (d={zs - zw:+.2e})",
                   abs(zs - zw) < 1e-9))

    # (6) chunking equivalence: chunk=5 and chunk=64 give identical tops.
    r5 = sweep(aff[:20], pl.cts, N, null=null, chunk=5)
    r64 = sweep(aff[:20], pl.cts, N, null=null, chunk=64)
    checks.append(("chunking invariance", r5["top"] == r64["top"]))

    # (7) POSITIVE CONTROL: plant with q = 17*v; the affine sweep must
    #     surface a=17 as a decisive, isolated winner at drift +1.
    q17 = (17 * np.arange(N)) % N
    plq = _plant_with_q(q17, seed=3)
    r = sweep(aff, plq.cts, N, seed=2)
    top2 = {(lab, d) for _, d, lab in r["top"][:2]}
    z0, z2 = r["top"][0][0], r["top"][2][0]
    checks.append((f"affine plant: mirror doublet 17@+1 / 66@-1 "
                   f"(z={z0:.1f}, third={z2:.1f})",
                   top2 == {("affine a=17", 1), ("affine a=66", -1)}
                   and z0 < -10 and z2 > z0 + 5))

    # (8) drift sweep: a REVERSE-drift affine plant surfaces at drift -1.
    plr = _plant_with_q(q17, seed=4, drift=-1)
    rr = sweep(aff, plr.cts, N, seed=3)
    top2r = {(lab, d) for _, d, lab in rr["top"][:2]}
    z0r = rr["top"][0][0]
    checks.append((f"reverse plant: mirror doublet 17@-1 / 66@+1 "
                   f"(z={z0r:.1f})",
                   top2r == {("affine a=17", -1), ("affine a=66", 1)}
                   and z0r < -10))

    # (9) NEGATIVE CONTROL: a random-C plant swept with a family that does
    #     NOT contain the truth produces no survivor (multiple-comparison
    #     sanity for the -6 line at family scale).
    plu = plantlab.gen("pmp", seed=5, shared_prefix=20)   # random C inside
    rn = sweep(aff, plu.cts, N, seed=4)
    zmin = rn["top"][0][0]
    checks.append((f"random-C plant: affine family stays null "
                   f"(min z={zmin:.1f})", len(rn["survivors"]) == 0))

    # (10) END TO END: sweep -> survivor -> bridge verdict PASS with a
    #      readable decode, on the positive-control plant.
    bank = {"english": ordering_bridge.order_anneal.CharNgram.train(
        plantlab.SAMPLE_TEXT, plantlab.ALPHABET)}
    cards = verdict_survivors(r, plq.cts, N, bank=bank, max_verdicts=1,
                              read_restarts=12, read_iters=20000, seed=1)
    c = cards[0]
    checks.append((f"end-to-end: bridge verdict {c['verdict']} on "
                   f"{c['label']} (z={c['best_z']}, "
                   f"read={c['learned']['readability']})",
                   c["verdict"] == "PASS"
                   and c["label"] in ("affine a=17", "affine a=66")))

    # (11) determinism.
    ra = sweep(aff[:30], pl.cts, N, seed=7)
    rb = sweep(aff[:30], pl.cts, N, seed=7)
    checks.append(("sweep deterministic",
                   ra["top"] == rb["top"] and
                   ra["survivors"] == rb["survivors"]))
    return checks


def _run_selftest() -> int:
    ok = True
    for name, passed in selftest():
        print(f"[{'OK  ' if passed else 'FAIL'}] {name}")
        ok &= passed
    return 0 if ok else 1


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--families", default="affine,power,deals",
                    help=f"comma list from {sorted(FAMILIES)}")
    ap.add_argument("--limit", type=int, default=None,
                    help="cap candidates per family (trigram/keyword)")
    ap.add_argument("--topk", type=int, default=50)
    ap.add_argument("--verdicts", type=int, default=3,
                    help="max survivors to send to the bridge")
    args = ap.parse_args()
    if args.selftest:
        return _run_selftest()

    import corpus as cm
    c = cm.load()
    cts = [list(x) for x in c.ciphertexts]
    N = c.N
    xp, backend = order_gpu.get_backend()
    print(f"backend: {backend}; corpus: {len(cts)} msgs, N={N}")
    null = null_calibration(cts, N, xp=xp)
    for d, (mu, sd) in null.items():
        print(f"null drift {d:+d}: mu={mu:.2f} sd={sd:.3f}")

    for fam in args.families.split(","):
        gen = FAMILIES[fam.strip()]
        kw = {}
        if args.limit and fam.strip() in ("trigram", "keyword"):
            kw["limit"] = args.limit
        res = sweep(gen(N, **kw) if kw else gen(N), cts, N, xp=xp,
                    topk=args.topk, null=null)
        print(f"\n== {fam}: scored {res['scored']}, "
              f"survivors {len(res['survivors'])}")
        for z, d, lab in res["top"][:10]:
            print(f"   z={z:+7.2f} drift={d:+d}  {lab}")
        if res["survivors"]:
            print("   -> bridge verdicts on survivors:")
            for card in verdict_survivors(res, cts, N,
                                          max_verdicts=args.verdicts):
                print(f"   {card['label']}: {card['verdict']} "
                      f"(read z={card['best_z']}, "
                      f"lang={card['learned']['language']}, "
                      f"readability={card['learned']['readability']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
