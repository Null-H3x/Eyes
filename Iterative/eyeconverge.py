#!/usr/bin/env python3
"""
eyeconverge -- the pre-registered template re-convergence census (FR3 S8
item 1). Read-only; no isomorph is modified, filtered, or weighted.

QUESTION. FR3 certified the opening stack: a T2/T3 template (six-deep at
3-5, four-deep at 6-9, three-deep at 10-20) and a T1 template (three-deep
at 3-24). Messages DIVERGE from their stack at known positions (W2 at 6,
W3 at 6, E3 at 10, the T3 trio at 21). Do diverged messages ever RE-MATCH
the template value at later positions? Each certified re-convergence is a
shared-template token beyond the contiguous runs -- one more depth cell in
exactly the crib-constrained region -- and under the one-gauge reading it
extends the single corpus-wide stack. Trigger (disclosed in FR3 S1): the
5-way value-47 match at position 20, found by eyeballing, watch-grade,
NOT counted as confirmatory here.

TRIAL DEFINITION (the part that took care). A trial is (message m,
position t) where m's value is FREE: m is outside BOTH certified cores at
t. Messages core-locked in the other template are excluded -- their values
are template-determined, and counting them triple-counts one deterministic
template-vs-template comparison (that comparison is reported separately as
the collision scan S4). Free trials:
    vs template A (T2/T3): W2 at 6..20, W3 at 6..20, E3 at 10..20   = 41
    vs template B (T1):    W2 at 6..24, W3 at 6..24, E3 at 10..24,
                           E4/W4/E5 at 21..24                        = 65
    total 106; null expectation 106/83 ~ 1.28.

STATISTICS.
  S1 pooled census. PRIMARY (confirmatory): all trials EXCEPT the two
     disclosed position-20 events (W2@20, E3@20); fire bar p < 0.01 under
     BOTH the uniform null (exact binomial, 1/83) and the unigram-adjusted
     null (per-trial match probability = frequency of the template value
     in that message). SECONDARY: the full census including the trigger.
  S2 joint positions: >= 2 free messages matching the same template value
     at the same position. Familywise expectation ~ 0.02 across the whole
     census, so any NEW joint position certifies; the known 47@20 joint is
     re-priced inside the registered frame and labeled as the trigger.
  S3 payoff: every certified event = one depth cell added to the stack
     table at its position.
  S4 template-collision scan (descriptive): positions where the A and B
     template values coincide.

Pre-registration: PREREG below, frozen on the plant suite before any new
corpus statistic is computed.
"""

import json, math, os, random, sys

ERR = "XD-MBYG04K-URS3LF"
N = 83
RNG_SEED = 20260724

PREREG = {
    "primary_fire_p": 0.01,       # under BOTH nulls, known events excluded
    "joint_new_certifies": True,  # familywise E ~ 0.02 for the whole census
    "known_events": [["West 2", 20], ["East 3", 20]],
}

def fail(msg): raise RuntimeError(f"{ERR}: {msg}")

TRIPLETS = {"T1": ["East 1", "West 1", "East 2"],
            "T2": ["West 2", "East 3", "West 3"],
            "T3": ["East 4", "West 4", "East 5"]}

# certified stack structure (FR3 C1), frozen
CORE_A = {**{t: ["West 2", "East 3", "West 3", "East 4", "West 4", "East 5"]
             for t in range(3, 6)},
          **{t: ["East 3", "East 4", "West 4", "East 5"] for t in range(6, 10)},
          **{t: ["East 4", "West 4", "East 5"] for t in range(10, 21)}}
CORE_B = {t: ["East 1", "West 1", "East 2"] for t in range(3, 25)}

FREE_A = ([("West 2", t) for t in range(6, 21)] +
          [("West 3", t) for t in range(6, 21)] +
          [("East 3", t) for t in range(10, 21)])
FREE_B = ([("West 2", t) for t in range(6, 25)] +
          [("West 3", t) for t in range(6, 25)] +
          [("East 3", t) for t in range(10, 25)] +
          [(m, t) for m in ("East 4", "West 4", "East 5") for t in range(21, 25)])

def load_corpus(path):
    c = json.load(open(path))
    return dict(zip(c["message_labels"], c["ciphertexts"]))

def template_values(msgs, core):
    """unanimity-verified template value per position; hard-fail otherwise."""
    vals = {}
    for t, members in core.items():
        vs = {msgs[m][t] for m in members}
        if len(vs) != 1:
            fail(f"core not unanimous at position {t}: {sorted(vs)}")
        vals[t] = vs.pop()
    return vals

def binom_tail(n, k, p):
    """P(X >= k), X ~ Binomial(n, p), exact."""
    if k <= 0: return 1.0
    s = 0.0
    for i in range(k, n + 1):
        s += math.comb(n, i) * (p ** i) * ((1 - p) ** (n - i))
    return s

def poisson_tail(lam, k):
    if k <= 0: return 1.0
    s, term = 0.0, math.exp(-lam)
    for i in range(0, k):
        s += term
        term *= lam / (i + 1)
    return 1.0 - s

def run_census(msgs, tA, tB, freeA, freeB, known):
    """returns dict with per-trial events and the S1/S2 statistics."""
    known = {tuple(k) for k in known}
    events = []
    for (m, t) in freeA:
        if t in tA and msgs[m][t] == tA[t]:
            events.append((m, t, "A", tA[t]))
    for (m, t) in freeB:
        if t in tB and msgs[m][t] == tB[t]:
            events.append((m, t, "B", tB[t]))
    n_all = len(freeA) + len(freeB)
    obs_all = len(events)
    new_events = [e for e in events if (e[0], e[1]) not in known]
    n_prim = n_all - len(known)
    obs_prim = len(new_events)
    # unigram-adjusted null
    lam_all = 0.0
    for (m, t) in freeA:
        v = tA[t]; lam_all += msgs[m].count(v) / len(msgs[m])
    for (m, t) in freeB:
        v = tB[t]; lam_all += msgs[m].count(v) / len(msgs[m])
    lam_prim = lam_all
    for (m, t) in known:
        tmpl = tA if t in tA else tB
        lam_prim -= msgs[m].count(tmpl[t]) / len(msgs[m])
    p_prim_uni = binom_tail(n_prim, obs_prim, 1.0 / N)
    p_prim_adj = poisson_tail(lam_prim, obs_prim)
    # joint positions among free trials (per template)
    joint = {}
    for e in events:
        joint.setdefault((e[2], e[1]), []).append(e[0])
    joint = {k: v for k, v in joint.items() if len(v) >= 2}
    return dict(events=events, new_events=new_events,
                n_all=n_all, obs_all=obs_all, n_prim=n_prim, obs_prim=obs_prim,
                lam_prim=lam_prim, p_prim_uni=p_prim_uni, p_prim_adj=p_prim_adj,
                p_all_uni=binom_tail(n_all, obs_all, 1.0 / N), joint=joint)

# ------------------------------------------------------------------ plants
def plant_corpus(rng, reconv_rate=0.0, joint_positions=(), stack_jitter=True):
    """9 messages with the FR3 stack shape; free-region values independent
    uniform except planted re-convergences. Returns msgs + planted event
    list. Free trials mirror the corpus definitions exactly."""
    L = {"East 1": 99, "West 1": 103, "East 2": 118, "West 2": 102,
         "East 3": 137, "West 3": 124, "East 4": 119, "West 4": 120,
         "East 5": 114}
    msgs = {m: [rng.randrange(N) for _ in range(L[m])] for m in L}
    hdr = [rng.randrange(N) for _ in range(2)]
    while True:                                          # collision-free templates
        tA_open = [rng.randrange(N) for _ in range(18)]  # A values at 3..20
        tB_open = [rng.randrange(N) for _ in range(22)]  # B values at 3..24
        if all(tA_open[i] != tB_open[i] for i in range(18)): break
    for m in msgs: msgs[m][1:3] = hdr
    for t in range(3, 6):
        for m in TRIPLETS["T2"] + TRIPLETS["T3"]: msgs[m][t] = tA_open[t - 3]
    for t in range(6, 10):
        for m in ["East 3"] + TRIPLETS["T3"]: msgs[m][t] = tA_open[t - 3]
    for t in range(10, 21):
        for m in TRIPLETS["T3"]: msgs[m][t] = tA_open[t - 3]
    for t in range(3, 25):
        for m in TRIPLETS["T1"]: msgs[m][t] = tB_open[t - 3]
    # scrub accidental free-trial matches so plants are exact
    planted = []
    for (m, t) in FREE_A:
        if msgs[m][t] == tA_open[t - 3]:
            msgs[m][t] = (msgs[m][t] + 1 + rng.randrange(N - 1)) % N
    for (m, t) in FREE_B:
        if msgs[m][t] == tB_open[t - 3]:
            msgs[m][t] = (msgs[m][t] + 1 + rng.randrange(N - 1)) % N
    # plant scattered re-convergences at the requested rate
    if reconv_rate > 0:
        for (m, t) in FREE_A:
            if rng.random() < reconv_rate:
                msgs[m][t] = tA_open[t - 3]; planted.append((m, t, "A"))
        for (m, t) in FREE_B:
            if rng.random() < reconv_rate:
                msgs[m][t] = tB_open[t - 3]; planted.append((m, t, "B"))
    # plant joint positions (two free messages matching template A)
    for t in joint_positions:
        for m in ("West 2", "West 3"):
            msgs[m][t] = tA_open[t - 3]; planted.append((m, t, "A"))
    return msgs, planted

def selftest():
    ok = True
    def check(name, cond, note=""):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name} {note}")
        ok = ok and cond
    def fresh(tag): return random.Random(f"{RNG_SEED}:{tag}")

    print("selftest: census exactness, nulls, joint detection, guards")

    # P1 null: quiet census over replicates (no known-event exclusion in plants)
    fires = 0; tot_obs = 0
    for i in range(12):
        msgs, _ = plant_corpus(fresh(f"p1{i}"))
        tA = template_values(msgs, CORE_A); tB = template_values(msgs, CORE_B)
        r = run_census(msgs, tA, tB, FREE_A, FREE_B, known=[])
        fires += (r["p_prim_uni"] < PREREG["primary_fire_p"]); tot_obs += r["obs_prim"]
    check("null: no false fires in 12 reps", fires == 0,
          f"(fires={fires}, mean obs={tot_obs/12:.2f})")

    # P2 scattered re-convergence fires and events recovered exactly
    msgs, planted = plant_corpus(fresh("p2"), reconv_rate=0.08)
    tA = template_values(msgs, CORE_A); tB = template_values(msgs, CORE_B)
    r = run_census(msgs, tA, tB, FREE_A, FREE_B, known=[])
    got = {(m, t) for (m, t, _, _) in r["events"]}
    want = {(m, t) for (m, t, _) in planted}
    check("reconv: census fires under both nulls",
          r["p_prim_uni"] < 0.01 and r["p_prim_adj"] < 0.01,
          f"(obs={r['obs_prim']}, p_uni={r['p_prim_uni']:.2e}, p_adj={r['p_prim_adj']:.2e})")
    check("reconv: events recovered exactly", got == want,
          f"(got {len(got)}, want {len(want)})")

    # P3 joint positions certified
    msgs, planted = plant_corpus(fresh("p3"), joint_positions=(12, 17))
    tA = template_values(msgs, CORE_A); tB = template_values(msgs, CORE_B)
    r = run_census(msgs, tA, tB, FREE_A, FREE_B, known=[])
    jpos = {t for (tmpl, t) in r["joint"]}
    check("joint: planted joint positions certified", jpos == {12, 17}, f"({sorted(jpos)})")

    # P4 guard: corrupted core hard-fails
    msgs, _ = plant_corpus(fresh("p4"))
    msgs["East 4"][12] = (msgs["East 4"][12] + 1) % N
    try:
        template_values(msgs, CORE_A); guard = False
    except RuntimeError as e:
        guard = str(e).startswith(ERR)
    check("guard: non-unanimous core hard-fails with prefix", guard)

    # P5 known-event exclusion arithmetic
    msgs, planted = plant_corpus(fresh("p5"), joint_positions=(20,))
    tA = template_values(msgs, CORE_A); tB = template_values(msgs, CORE_B)
    r_all = run_census(msgs, tA, tB, FREE_A, FREE_B, known=[])
    r_exc = run_census(msgs, tA, tB, FREE_A, FREE_B,
                       known=[["West 2", 20], ["West 3", 20]])
    check("primary excludes known events", r_all["obs_prim"] == 2
          and r_exc["obs_prim"] == 0 and r_exc["n_prim"] == r_all["n_all"] - 2,
          f"(all={r_all['obs_prim']}, excl={r_exc['obs_prim']})")

    print("selftest:", "ALL GREEN" if ok else "FAILURES PRESENT")
    if not ok: fail("selftest failed -- corpus verdicts must not be trusted")
    return ok

# ------------------------------------------------------------------ corpus
def corpus_run(corpus_path):
    M = load_corpus(corpus_path)
    print("\npre-registered thresholds:", json.dumps(PREREG))
    tA = template_values(M, CORE_A)
    tB = template_values(M, CORE_B)
    print(f"\ncore unanimity verified: template A at {len(tA)} positions, "
          f"template B at {len(tB)} positions")

    r = run_census(M, tA, tB, FREE_A, FREE_B, PREREG["known_events"])
    print(f"\nS1 pooled census: {r['n_all']} free trials")
    print(f"  all events ({r['obs_all']}):")
    for (m, t, tmpl, v) in r["events"]:
        tag = "KNOWN TRIGGER" if [m, t] in PREREG["known_events"] else "NEW"
        print(f"    {m:8s} @ {t:2d} matches template {tmpl} value {v:2d}   [{tag}]")
    print(f"  PRIMARY (known excluded): obs={r['obs_prim']} of n={r['n_prim']}, "
          f"E_uniform={r['n_prim']/N:.2f}, E_adjusted={r['lam_prim']:.2f}")
    print(f"    p_uniform={r['p_prim_uni']:.4f}  p_adjusted={r['p_prim_adj']:.4f}")
    fire = (r["p_prim_uni"] < PREREG["primary_fire_p"]
            and r["p_prim_adj"] < PREREG["primary_fire_p"])
    print(f"    -> {'CENSUS FIRES: re-convergence structure beyond the trigger' if fire else 'no re-convergence structure beyond the trigger (census quiet)'}")
    print(f"  SECONDARY (full, incl. trigger): obs={r['obs_all']}, "
          f"p_uniform={r['p_all_uni']:.4f}")

    print("\nS2 joint positions (>=2 free messages, same template, same t):")
    if r["joint"]:
        for (tmpl, t), ms in sorted(r["joint"].items(), key=lambda kv: kv[0][1]):
            known = all([m, t] in PREREG["known_events"] for m in ms)
            print(f"    template {tmpl} @ {t}: {ms}  "
                  f"[{'the disclosed trigger, re-priced familywise ~0.02' if known else 'NEW -> CERTIFIED'}]")
    else:
        print("    none")

    print("\nS3 payoff: each certified event adds one depth cell at its "
          "position; see report for the updated stack table")

    print("\nS4 template collision scan (A value == B value, t=3..20):")
    coll = [t for t in range(3, 21) if tA.get(t) == tB.get(t)]
    print(f"    {coll if coll else 'none'}")

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    corpus = os.environ.get("EYE_CORPUS",
        os.path.join(here, "..", "Eyes-main", "noita_eye_core", "corpus.json"))
    if "--selftest" in sys.argv:
        selftest(); sys.exit(0)
    selftest()
    corpus_run(corpus)
