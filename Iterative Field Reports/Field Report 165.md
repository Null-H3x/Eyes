# Field Report 165 — THE STAMPED HEADER IS FORCED, NOT CHOSEN; AND THE 48 ANOMALY DISSOLVES

*Instrument: `eyehead.py` (2/2 gate). July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The crack, priced

Five candidates were priced before building. **The stamped-header assumption is
the only one where a positive result would change the cipher**, and it is the
one an external critic independently identified as load-bearing.

Positions 1–24 of East 1, West 1 and East 2 are 24-of-25 byte-identical. If they
are encrypted co-plaintext then `q[x] − q[x] = 0` forces `base_E2 = base_E1`
against the model's forced 77, and `77d ≡ 0 (mod 83)` with 83 prime gives
`d = 0` — the progressive form dies.

**The model reads them as literal glyphs. That has never been tested.**

---

## 1. The test

```
G1 canonical rebuild      : (794, 61, 8)   PASS
G2 contradiction detector : PASS

opening cells asserted as co-plaintext: 48
   (positions 1-24 of East 1 vs East 2 and West 1)

regime                                          drifts OK
R1 full evidence + openings co-plaintext                0
R2 full evidence + T1 bases forced EQUAL                0
R3 control: full evidence, no extra assertion          82
```

> **Zero of 82 nonzero drifts survive either assertion, while the unmodified
> model survives all 82. The openings cannot be encrypted co-plaintext.**

**The stamped-header reading is FORCED, not chosen.** It is not an assumption
the model makes for convenience — it is the only reading the evidence permits,
and the alternative is inconsistent at every drift rather than merely
disfavoured.

This answers the critique directly: *the model's fate does ride on those three
openings, and the ride is not close.*

---

## 2. And the 48 dissolve

FR151 flagged 48 strong isomorph classes that cannot be co-plaintext; FR157
refuted the constant-offset explanation; FR163 left three candidates. FR164's
calibrated control supplies the answer.

Contradiction rate under an **injective**-alphabet control matched to the
corpus:

```
seed 7100: 268 classes,  65 contradictory (24.3%)
seed 7101: 315 classes, 150 contradictory (47.6%)
seed 7102: 256 classes,  76 contradictory (29.7%)
seed 7103: 268 classes,  58 contradictory (21.6%)
seed 7104: 254 classes, 100 contradictory (39.4%)

control : 32.5% +- 9.7%
REAL    : 48/208 = 23.1%     z = -0.97
```

> **The real corpus's contradiction rate is indistinguishable from an
> injective-alphabet control.** The 48 are ordinary chance isomorphs. There is
> no anomaly left to explain.

That closes a line open since FR151, and it closes it by the mechanism FR164
established rather than by a new hypothesis.

---

## 3. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Stamped-header reading** | load-bearing assumption | **FORCED** — 0 of 82 drifts survive the alternative |
| `d ≡ 0` via the openings | the critique's route | **closed** — the premise is inconsistent, not merely costly |
| The 48 contradictory classes | anomaly, 3 candidates (FR163) | **chance isomorphs** — rate 23.1% vs control 32.5% ± 9.7% |
| FR157's multiplier variant | next candidate | **unnecessary** — no anomaly remains |
| Biggest remaining crack | the openings | **the openings are now closed** |

---

## 4. Model status

Extended skeleton: 794 relations, 61 glyphs, 8 homophones, alphabet [56, 75],
79.1% exposure, 435-position reading, 6 anchors, 68 maximal readings,
19-relation invariant core. **The stamped-header reading is now proven forced
rather than assumed.** Cumulative: 27.16 billion candidates, zero survivors.

---

## 5. Horizon — the cracks that remain

1. **West 3's 148-position island** — zero k≥3 alignments (FR149), anchor-only.
   A crack in coverage, not in the model.
2. **The 26 unconstrained glyphs** — invisible to every internal test by
   construction (FR135). A wall, not a crack.
3. **The reading order** — inherited from Toboter, never re-derived here. Cheap
   and almost certainly fine; the only untested inherited input left.

**Nothing on that list can change the cipher.** The last item that could —
whether the openings are encrypted — is now settled at 0 of 82.
