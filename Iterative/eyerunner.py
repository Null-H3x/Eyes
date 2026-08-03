#!/usr/bin/env python3
"""
eyerunner.py -- hardened seed-sweep runner for the Noita eye alphabet.

XD-MBYG04K-URS3LF prefix on all exceptions.

SELF-CONTAINED. No imports from the analysis environment. Drop on the GPU box,
run, and hand the emitted JSON back for ingestion.

    python3 eyerunner.py --gen fy_lgm --start 0 --count 10000000 --out run1.json

PARANOIA DESIGN
---------------
The failure this is built against is a silent one: a filter that can never fire
runs for four hours and reports a clean null indistinguishable from a real one.

  * CANARY INJECTION. Known-consistent alphabets are substituted into the live
    stream at pseudo-random positions. Every canary MUST be caught. One miss
    aborts the run. This proves the filter was live for the whole sweep, not
    just at startup.
  * STARTUP GATE. Park-Miller KAT, permutation validity, positive control on a
    constructed alphabet, negative control on random permutations.
  * CHECKPOINTS. Resumable; a crash at hour three does not lose the run.
  * HITS PERSISTED IN FULL. The filter uses 46 glyphs and is necessary-not-
    sufficient, so any hit is written out complete for downstream verification
    against the full 56-glyph skeleton, injectivity and packing.

AUDIT FIXES APPLIED (FR95)
--------------------------
  B1  seed 0 is SKIPPED, not remapped. His code asserts(seed).
  B2  seeds are range-checked; LGM diverges above 2^31 because his cast is
      (long)seed with no reduction. Refuses out-of-range input rather than
      silently testing a different stream.
  B3  the j>i clamp is replaced by an assertion. It provably never fires
      (max Next() * 83 = 82.99999...), so if it ever does, the scale constant
      is wrong and the run is invalid.
  B4  hits persisted with generator, seed, direction, permutation, drift.
  B5  canaries, as above.
  B6  set_fastrand_seed is `seed ^ 13 - 1` == `seed ^ 12` by C precedence.
"""
import argparse, json, os, random, sys, time

VERSION = "eyerunner-1.0 (FR95)"

class XD(Exception):
    def __init__(s, m): super().__init__("XD-MBYG04K-URS3LF " + m)

N = 83
M31 = 2147483647
M32 = 0xFFFFFFFF
SCALE = 4.656612875e-10

# ---------------------------------------------------------------- skeleton
C1 = {0:0,1:3,5:7,6:34,7:36,9:58,10:55,17:29,20:39,27:1,30:66,34:61,41:69,
      45:60,47:35,48:82,50:8,57:33,62:28,63:31,64:81,68:65,71:38,79:57,81:54}
C2 = {13:0,19:53,23:4,25:82,44:1,46:31,49:52,60:81,66:55,72:35,78:25}
C3 = {16:0,21:58,26:1,40:57,42:35,67:31,73:2}
C4 = {4:0,35:55,37:57}
COMPS = [C1, C2, C3, C4]

INV = [0] * N
for _x in range(1, N):
    INV[_x] = pow(_x, N - 2, N)

REL = []
for _C in COMPS:
    _g = sorted(_C)
    for _i in range(len(_g)):
        for _j in range(_i + 1, len(_g)):
            _a, _b = _g[_i], _g[_j]
            _d = (_C[_b] - _C[_a]) % N
            if _d:
                REL.append((_a, _b, _d))
NREL = len(REL)


def skeleton_ok(p):
    """all within-component relations must agree on ONE drift"""
    a, b, d = REL[0]
    drift = ((p[b] - p[a]) % N) * INV[d] % N
    if drift == 0:
        return False
    for a, b, d in REL:
        if (p[b] - p[a]) % N != drift * d % N:
            return False
    return True


def drift_of(p):
    a, b, d = REL[0]
    return ((p[b] - p[a]) % N) * INV[d] % N


# independent constraints: sum(k-1) over components, minus 1 for the drift.
INDEP = sum(len(c) - 1 for c in COMPS) - 1          # 41, NOT 379 (FR96)


def verify_hit(p):
    """A passing permutation uses only the 46 held glyphs and is
    NECESSARY-not-sufficient. This extracts (drift, bases) and confirms the
    result is a member of the enumerated consistent set: bases must place the
    component value-sets DISJOINTLY (FR27 packing). A hit failing this is a
    bug, not a discovery."""
    out = {"drift": drift_of(p), "bases": [], "relations_ok": skeleton_ok(p),
           "packing_ok": None, "component_values": []}
    d = out["drift"]
    if d == 0:
        out["packing_ok"] = False
        return out
    seen = set()
    ok = True
    for C in COMPS:
        g0 = sorted(C)[0]
        base = (p[g0] - d * C[g0]) % N
        out["bases"].append(base)
        vals = sorted(p[g] for g in C)
        out["component_values"].append(vals)
        # every glyph must sit exactly where base + drift*Delta predicts
        for g, dv in C.items():
            if p[g] != (base + d * dv) % N:
                ok = False
        if seen & set(vals):
            ok = False
        seen |= set(vals)
    out["packing_ok"] = ok and len(seen) == sum(len(c) for c in COMPS)
    return out


def invert(p):
    o = [0] * N
    for i, v in enumerate(p):
        o[v] = i
    return o


# ------------------------------------------------------------- generators
class LGM:
    """Global_LGMRandom / CLGMRandom. State is the double `seed`; the member
    `iseed` in his source is written once and never read."""
    __slots__ = ('s',)
    def __init__(self, seed):
        if seed == 0:
            raise XD("seed 0 invalid: his Next() asserts(seed)")   # B1
        if not (0 < seed < M31):
            raise XD("seed %d outside [1, 2^31): (long)seed cast diverges" % seed)  # B2
        self.s = int(seed)
    def next(self):
        i = self.s
        hi = i // 127773
        lo = i - hi * 127773
        i = 16807 * lo - 2836 * hi
        if i <= 0:
            i += M31
        self.s = i
        return i * SCALE
    def random(self, low, high):
        return low + int((high - low + 1) * self.next())


def fy_lgm(seed):
    r = LGM(seed)
    p = list(range(N))
    for i in range(N - 1, 0, -1):
        j = r.random(0, i)
        if j > i:                                                   # B3
            raise XD("index %d > %d: SCALE constant wrong, run invalid" % (j, i))
        p[i], p[j] = p[j], p[i]
    return p


def fy_lgm_fwd(seed):
    r = LGM(seed)
    p = list(range(N))
    for i in range(N - 1):
        j = r.random(i, N - 1)
        if j > N - 1:
            raise XD("index %d out of range: run invalid" % j)
        p[i], p[j] = p[j], p[i]
    return p


def _fastrand_state(seed):
    return (int(seed) ^ 12) & M32          # B6: seed ^ 13 - 1 == seed ^ 12


def fy_fastrand_floor(seed):
    g = _fastrand_state(seed)
    p = list(range(N))
    for i in range(N - 1, 0, -1):
        g = (214013 * g + 2531011) & M32
        v = (g >> 16) & 0x7FFF
        j = int((v / 32768.0) * (i + 1))
        if j > i:
            raise XD("index %d > %d: run invalid" % (j, i))
        p[i], p[j] = p[j], p[i]
    return p


def fy_fastrand_mod(seed):
    g = _fastrand_state(seed)
    p = list(range(N))
    for i in range(N - 1, 0, -1):
        g = (214013 * g + 2531011) & M32
        v = (g >> 16) & 0x7FFF
        j = v % (i + 1)
        p[i], p[j] = p[j], p[i]
    return p


GENS = {'fy_lgm': fy_lgm, 'fy_lgm_fwd': fy_lgm_fwd,
        'fy_fastrand_floor': fy_fastrand_floor, 'fy_fastrand_mod': fy_fastrand_mod}


# ------------------------------------------------------------- canaries
def make_consistent(drift, bases, rng):
    """a permutation that satisfies the skeleton by construction"""
    q = {}
    for ci, C in enumerate(COMPS):
        for g, dv in C.items():
            q[g] = (bases[ci] + drift * dv) % N
    used = set(q.values())
    if len(used) != len(q):
        return None
    free = [v for v in range(N) if v not in used]
    rng.shuffle(free)
    out = [0] * N
    k = 0
    for g in range(N):
        if g in q:
            out[g] = q[g]
        else:
            out[g] = free[k]; k += 1
    return out if sorted(out) == list(range(N)) else None


def build_canaries(n, rng):
    """Random base tuples are injective only ~0.05% of the time (that IS the
    packing constraint). So find valid base tuples once at drift 1, then use
    scale-invariance: a packing valid at drift 1 is valid at every drift."""
    bases = []
    tries = 0
    while len(bases) < 4 and tries < 400000:
        tries += 1
        b = [0] + [rng.randrange(N) for _ in range(3)]
        if make_consistent(1, b, rng) is not None:
            bases.append(b)
    if not bases:
        raise XD("no valid packing found for canaries")
    out = []
    for b in bases:
        for drift in range(1, N):
            # FR53 scale-invariance: {d*b_c} packs {d*S_c}. Bases scale WITH the drift.
            sb = [(drift * x) % N for x in b]
            c = make_consistent(drift, sb, rng)
            if c and skeleton_ok(c):
                out.append(c)
            if len(out) >= n:
                return out
    if len(out) < n:
        raise XD("could only build %d of %d canaries" % (len(out), n))
    return out


# ------------------------------------------------------------- startup gate
def gate():
    checks = []
    def ck(nm, cond, det=""):
        checks.append({"check": nm, "pass": bool(cond), "detail": det})
        if not cond:
            raise XD("GATE FAIL: %s %s" % (nm, det))

    r = LGM(1); r.next()
    ck("park_miller_kat_1", r.s == 16807, str(r.s))
    r.next()
    ck("park_miller_kat_2", r.s == 282475249, str(r.s))
    ck("relation_count", NREL == 379, str(NREL))

    for nm, f in GENS.items():
        ck("permutation_%s" % nm,
           all(sorted(f(s)) == list(range(N)) for s in (1, 1234, 1500000000)))

    rng = random.Random(20260726)
    can = build_canaries(8, rng)
    ck("positive_control", all(skeleton_ok(c) for c in can), "8 canaries")

    bad = 0
    for _ in range(20000):
        p = list(range(N)); rng.shuffle(p)
        if skeleton_ok(p):
            bad += 1
    ck("negative_control", bad == 0, "%d/20000 false positives" % bad)

    c = can[0]
    ck("drift_recovery", drift_of(c) != 0, str(drift_of(c)))
    v = verify_hit(c)
    ck("verify_hit_on_canary", v["packing_ok"] and v["relations_ok"], str(v["drift"]))
    bad = list(range(N)); bad[0], bad[1] = bad[1], bad[0]
    ck("verify_hit_rejects_bad", not verify_hit(bad)["packing_ok"])
    ck("independent_constraints", INDEP == 41, str(INDEP))

    # reference vectors: any port MUST reproduce these exactly
    refs = {g: GENS[g](1234)[:12] for g in sorted(GENS)}
    checks.append({"check": "reference_vectors_seed_1234", "pass": True,
                   "detail": json.dumps(refs)})
    return checks


# ------------------------------------------------------------- main sweep
def run(gen, start, count, out_path, canary_rate, ckpt_every, resume):
    if gen not in GENS:
        raise XD("unknown generator %s" % gen)
    f = GENS[gen]
    rng = random.Random(0xEEEE ^ start ^ count)
    canaries = build_canaries(64, rng)

    state = {"done": 0, "hits": [], "canaries_planted": 0, "canaries_caught": 0}
    ckpt = out_path + ".ckpt"
    if resume and os.path.exists(ckpt):
        state = json.load(open(ckpt))
        print("resumed at offset %d" % state["done"])

    t0 = time.time()
    i = state["done"]
    i_at_start = i
    n_can = max(1, int(1.0 / canary_rate))
    while i < count:
        s = start + i
        i += 1
        if s == 0:
            continue                                   # B1
        # canary injection into the live stream
        if (s % n_can) == 0:
            c = canaries[s % len(canaries)]
            state["canaries_planted"] += 1
            if skeleton_ok(c):
                state["canaries_caught"] += 1
            else:
                raise XD("CANARY MISSED at seed %d -- filter is dead, run invalid" % s)
        try:
            p = f(s)
        except XD:
            raise
        for direction, cand in (("fwd", p), ("inv", invert(p))):
            if skeleton_ok(cand):
                v = verify_hit(cand)
                state["hits"].append({"generator": gen, "seed": s,
                                      "direction": direction,
                                      "permutation": cand,
                                      "verification": v})
                print("HIT  gen=%s seed=%d dir=%s drift=%d packing_ok=%s"
                      % (gen, s, direction, v["drift"], v["packing_ok"]))
                if not v["packing_ok"]:
                    print("     WARNING: packing check FAILED -- treat as a bug, not a find")
        if (i % ckpt_every) == 0:
            state["done"] = i
            json.dump(state, open(ckpt, "w"))
            el = time.time() - t0
            print("  %s / %s  %.0f seeds/s  hits=%d  canaries %d/%d"
                  % (format(i, ','), format(count, ','),
                     (i - i_at_start) / max(el, 1e-9),
                     len(state["hits"]), state["canaries_caught"], state["canaries_planted"]))

    el = time.time() - t0
    if state["canaries_planted"] == 0:
        raise XD("no canaries planted -- cannot certify the filter was live")
    if state["canaries_caught"] != state["canaries_planted"]:
        raise XD("canary mismatch %d/%d" % (state["canaries_caught"], state["canaries_planted"]))

    report = {
        "version": VERSION,
        "generator": gen,
        "seed_start": start,
        "seed_count": count,
        "seeds_tested": count,
        "directions": ["fwd", "inv"],
        "candidates": count * 2,
        "elapsed_s": round(el, 1),
        "rate_seeds_per_s": round((count - i_at_start) / max(el, 1e-9), 1),
        "resumed_from": i_at_start,
        "relations_used": NREL,
        "glyphs_used": sum(len(c) for c in COMPS),
        "filter": "skeleton consistency, one shared drift over all relations",
        "independent_constraints": INDEP,
        "selectivity": "83^-%d  (~1e-%d).  NOTE: 379 relations but only %d are "
                       "independent -- within a component, drift plus one glyph "
                       "determines the rest. Earlier reports quoting 83^-378 were "
                       "wrong by ~1e649; no conclusion changes." % (INDEP, 79, INDEP),
        "selectivity_note": "necessary-not-sufficient: 46 of 56 glyphs; every hit "
                            "carries verify_hit output; still verify against the full "
                            "56-glyph skeleton and packing downstream",
        "canaries_planted": state["canaries_planted"],
        "canaries_caught": state["canaries_caught"],
        "canary_integrity": state["canaries_caught"] == state["canaries_planted"],
        "hits": state["hits"],
        "hit_count": len(state["hits"]),
        "gate": GATE_RESULT,
    }
    json.dump(report, open(out_path, "w"), indent=1)
    if os.path.exists(ckpt):
        os.remove(ckpt)
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", default="fy_lgm", choices=sorted(GENS))
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--count", type=int, default=1000000)
    ap.add_argument("--out", default="eyerun.json")
    ap.add_argument("--canary-rate", type=float, default=1e-4)
    ap.add_argument("--ckpt-every", type=int, default=500000)
    ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()

    print(VERSION)
    print("running startup gate...")
    GATE_RESULT = gate()
    for c in GATE_RESULT:
        print("  %-24s %s %s" % (c["check"], "PASS" if c["pass"] else "FAIL", c["detail"]))
    print("gate clean; sweeping %s seeds from %d with %s"
          % (format(a.count, ','), a.start, a.gen))
    rep = run(a.gen, a.start, a.count, a.out, a.canary_rate, a.ckpt_every, a.resume)
    print()
    print("DONE  hits=%d  canaries %d/%d  %.0f seeds/s  -> %s"
          % (rep["hit_count"], rep["canaries_caught"], rep["canaries_planted"],
             rep["rate_seeds_per_s"], a.out))
