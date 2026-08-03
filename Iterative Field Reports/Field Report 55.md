# Field Report 55 — THE LAG-4 EXCESS IS REAL AND ITS INFERENCE IS NOT

*Instrument: `eyelag` (9/9 selftests, all green before corpus contact). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. Why this cycle

Three claims sit in load-bearing doctrine and cannot all be true:

1. The **lag-4 coincidence excess** (~2.25–2.31×, z≈+4.4) is carried as "the most
   replicated signal," whose "arithmetic consequences constrain plaintext alphabet
   size" — implied consistent with 26-English or 29-Finnish.
2. **FR36** excluded small contiguous plaintext alphabets; **FR39** excluded small
   scattered ones at 3.3σ; **FR40** validated the instrument with a positive
   control. Effective inventory **exceeds ~60**.
3. **FG5 §1** offers a third reading — lag-4 is "generic autokey/progressive
   distance-4 coincidence" — which would dissolve the conflict. That reading was
   **asserted, never measured**.

Fifty-four cycles have quoted (1) and (2) side by side without confronting them.

---

## 1. CHALLENGE I — the inference dies on inspection

Under the surviving skeleton `c[t] = C[(p[t] + base_m + K_g[t]) mod 83]`, a
ciphertext coincidence at lag *d* requires

```
p[t] − p[t+d] = K_g[t+d] − K_g[t]        ( = drift·d under progressive K )
```

83 is prime and drift ≠ 0, so **`drift·d ≠ 0`**. A lag-4 ciphertext coincidence is
therefore **not a repeated plaintext token** — it is a plaintext pair at a specific
*nonzero* difference. Any inference from the coincidence *rate* to the plaintext
*alphabet size* requires `K[t+4] = K[t]` for a substantial fraction of positions,
which the SUPPORTED model (`per-msg-progressive`, scoreboard rank 1) forbids
outright. The "aligned fraction" framing is a depth argument smuggled into a
non-depth setting.

This is the ninth horizon item in the series to die on inspection rather than
measurement. It is **not** the report, because the interesting question survives it:
the two events are separately measurable, and drift-free. For glyphs `g₁,g₂` in one
component at distance *d*:

| event | condition on Δ |
|---|---|
| ciphertext repeat | `Δ(g₂) − Δ(g₁) ≡ 0` |
| **plaintext repeat** | `Δ(g₂) − Δ(g₁) ≡ d` |

Neither needs the drift, the bases, or the alphabet.

---

## 2. Instrument and pre-registration

`eyelag` carries nine selftests, all green **before** corpus contact. The two that
matter: **S6** — a *planted* ciphertext-repeat excess must stay quiet in the
plaintext channel (z = −1.74, channels separate); **S7** — neither channel fires on
a clean random corpus (z = −0.21, −0.62). Null is FR42's geometry-preserving
within-(message, component) glyph permutation, verified to preserve the Δ multiset
exactly (drift = 0).

Registered before running: **R1** replication z ≥ +4.0; **R2** d=4 must top lags
1–30 *and* survive max-statistic correction at α=0.05; **R3** doctrine vindicated
iff PT channel fires (z ≥ +3), refuted iff CT fires and |z_PT| < 2; **R4** ≥7/9
leave-one-message-out retain z ≥ +3; **R5** must appear in the body.

---

## 3. What failed — two hypotheses of mine, and one bad threshold

**HYPOTHESIS 1, REFUTED: the excess is a pooling artifact.** Given FR39
(near-duplicate contamination), FR42 (geometry-destroying null), FR45 (shared-prefix
pooling) and FR48 (self-corroboration) — four pooling errors in ten cycles — the
obvious guess was a fifth. It is not. Against a unigram-preserving within-message
null the excess replicates at **2.16×, z = +4.20**, and it is corpus-wide: leave-one-
message-out retains z ≥ +3.0 in **9 of 9** cases (range +3.49 to +4.35). No message
carries it.

**HYPOTHESIS 2, REFUTED: the excess is redistribution from the d=1 prohibition.**
The corpus forbids adjacent repeats (§5). My null did not preserve that constraint,
so it generated ~12.4 adjacent repeats per draw that the corpus cannot have —
mechanically depressing null counts elsewhere and inflating the observed z. This is
exactly the FR41→FR42 failure shape and I expected it to fire. It does not:
constraining the null to zero adjacent repeats moves the d=4 null mean from 11.79 to
**11.85** and the z from +4.21 to **+4.23**. Twelve repeats redistributed across
28 lags and 9 messages is too small an effect. The excess is independent.

**SELF-CORRECTION: R3's refutation branch was vacuous.** I registered "refuted iff
CT fires and |z_PT| < 2." The PT channel at d=4 has only **150 usable
same-component pairs** and a null expectation of **2.27**. At that expectation the
|z_PT| < 2 branch **cannot fail** for any alphabet k ≥ 40 — I registered a test one
side of which was guaranteed to pass. This is the same error family as FR23
(passing injectivity by determining nothing) and FR49 (two vacuous selftests
shipped). *Ask what the test would return if the hypothesis were false, and check
the answer differs.* Fifth instance; the guard is not becoming automatic.

Consequence: **R3 returns neither verdict on its own terms** (z_CT = +2.36 against a
+3.0 threshold; z_PT = −0.88). Reported as inconclusive rather than repaired after
the fact.

---

## 4. What the corrected test does support

The PT channel is underpowered against a *flat* alternative but has real power
against the *specific* doctrinal claim. Observed plaintext-repeats at d=4: **1**.

| plaintext alphabet | expected PT-repeats at d=4 | Poisson P(X ≤ 1) |
|---|---|---|
| k = 26 (English) | 5.8 | **0.021** |
| k = 29 (Finnish) | 5.2 | **0.034** |
| k = 40 | 3.8 | 0.107 |
| k = 60 | 2.5 | 0.287 |
| flat (83) | 1.8 | 0.463 |

So in the doctrine's own lag-4 window, tested for the event the doctrine's inference
actually requires, **26-English is rejected at p ≈ 0.021 and 29-Finnish at
p ≈ 0.034**. That is a modest exclusion on a small sample, and it is stated at that
strength — but it is a *direct* measurement where the previous claim was an
arithmetic inference resting on a keystream property the model forbids. It agrees
with FR36, FR39 and FR40, reached by an unrelated mechanism on the narrowest
possible sample.

---

## 5. What is newly established

**The lag-4 excess is confirmed on a better footing than doctrine had it.** It was
previously priced against a uniform 1/83 baseline. It now survives (a) a
unigram-preserving null, (b) an adjacency-constrained null, and (c) multiplicity
correction over 30 lags: **max-statistic corrected P = 0.0035**.

**Its shape, characterised for the first time.** The excess is:

- **corpus-wide** — 26 coincidences distributed 2,3,2,2,3,2,4,4,4 across the nine
  messages, near-uniform;
- **glyph-generic** — 20 distinct glyphs involved, maximum 3 for any one (glyph 2);
- **non-chaining** — zero chains of `c[t]=c[t+4]=c[t+8]`; every coincidence is
  isolated;
- **unphased** — start positions mod 4 give χ² = 2.92 on 3 df, no periodic frame;
- **body-located** — body z = +4.17 (2.22×) vs openings z = +1.14, consistent with
  the stamped-header reading (FR29/FR33/FR44/FR45);
- **graded across triplets** — T3 z = +4.25 (2.92×), T1 +1.84, T2 +1.40. Only T3
  clears significance alone, on a third of the data each; logged as a gradient, not
  a claim.

**THE ADJACENCY PROHIBITION IS HARD, AND IS PRICED FOR THE FIRST TIME.** FG1
recorded "zero adjacent doubles" as an identification-battery observation. It is
stronger than that: **0 adjacent repeats over 1,027 pairs against 12.4 expected**,
`P = e^−12.4 ≈ 4.1 × 10⁻⁶`. That is a deterministic constraint, not a tendency, and
my error guard caught it — the constrained null has zero variance at d=1, which is
the signature of a prohibition rather than a suppression.

Under the established model this reads as a **hard plaintext constraint**: for all
1,027 adjacent pairs, `p[t+1] − p[t] ≠ drift`. FG1 read it as evidence of a
double-mixed embedding; that reading is about the encoding, and the model-side
reading above is available alongside it. The two are not yet separated.

**The short-range profile is a shape that wants explaining.** Observed counts
against a null of ~11.8:

```
d :   1     2     3     4     5     6
n :   0     5     9    26    11    12
z : HARD -2.09 -0.84 +4.23 -0.21 +0.05
```

A hard zero at 1, suppression at 2, normality at 3, a spike at 4, normality
thereafter. Neither surviving cipher family privileges d=4, so this is not explained
by the mechanism, and §4 says it is not plaintext repetition. It is currently
unexplained — which is a more honest position than the one it replaces.

---

## 6. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; corpus exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift
unpinned with H4 the only surviving hypothesis. Nothing in this cycle touches the
skeleton.

**Reproduction note.** The component tables and exposure figures were re-derived
from `noita_eye_core/corpus.json` at the top of this cycle and reproduce FR53
exactly: C1 323/31.2%, C2 179/17.3%, C3 104/10.0%, C4 29/2.8%, total 768/74.1%.
FR54's frequency partition also reproduces exactly (all 27 undetermined
frequencies; means 9.93/13.71; medians 10/13; ranges 5–17/3–26). One numerical
note: FR54's separation statistic recomputes as Welch **z = +4.26** against the
published +4.32 — a variance-convention difference, not a discrepancy; a
20,000-draw permutation null over random 56/27 splits places the observed value
beyond all but 2 draws.

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Lag-4 excess, existence | "most replicated signal," priced vs uniform 1/83 | **CONFIRMED and better priced** — 2.16×, z=+4.23 vs constrained null, corrected P=0.0035, 9/9 messages |
| Lag-4 → small plaintext alphabet | carried as arithmetic consequence | **RETIRED.** Requires `K[t+4]=K[t]`, forbidden by the SUPPORTED progressive model; and directly rejected at d=4 for k=26 (p≈0.021) and k=29 (p≈0.034) |
| FG5's "generic distance-4 coincidence" | asserted | **INSUFFICIENT** — neither surviving family privileges d=4; the assertion explains nothing |
| Zero adjacent doubles | identification-battery observation (FG1 §4b) | **HARD PROHIBITION**, priced at P≈4.1×10⁻⁶; model-side reading `p[t+1]−p[t] ≠ drift` now available |
| Short-range profile | never characterised | **0 / 5 / 9 / 26 / 11 / 12** — unexplained |

---

## 8. Horizon

1. **The short-range profile is the live object.** The excess is real, corpus-wide,
   glyph-generic, unphased, non-chaining, and not plaintext repetition. That is a
   tightly constrained target and nothing in the surviving families produces it. The
   next cycle should ask what *does* — with the standing warning that "generic
   artifact" has now been offered once and failed to survive contact.

2. **The adjacency prohibition may be a drift lever and has never been used as
   one.** If `p[t+1] − p[t] ≠ drift` holds across 1,027 pairs as a *plaintext*
   property, then on the skeleton the observed Δ-difference distribution at d=1
   excludes drift values inconsistent with it. This is the first constraint in the
   series that is *not* scale-invariant in the FR36/FR53 sense — it names a specific
   difference rather than a distinctness property — so the FR53 impossibility proof
   does not obviously apply to it. **Whether it survives that proof is the single
   highest-value question this cycle raises**, and it is checkable from inside the
   corpus, which nothing else on the horizon is.

3. **Standing, unchanged:** two external anchors in component 1 (FR54 ordering); and
   the success criterion, still the most consequential open item and still the only
   thing this series can neither compute nor close.

4. **Repo hygiene.** The `eyes` repo at HEAD contains no Field Reports and none of
   the FR-cycle instruments. `WAY_FORWARD_next.md` §5 still lists the cross-triplet
   W2/E4/W4 bridge as Priority 1 — closed by FR34 (bridges are dot cells) and FR35
   (W2 is uncoupled) — and the "16 pins" framing survives in `tools.md`,
   `Eyesolver/`, `eyeforward/` and `order gate/`, superseded by FR23/FR24/FR26. FR52's
   lesson applies at document scale: *no mechanism prevents a third stale figure.*
