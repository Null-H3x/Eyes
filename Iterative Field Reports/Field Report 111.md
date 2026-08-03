# Field Report 111 — THE CONTROL FIRED: THE REPAIR FORK IS CLOSED TO INTERNAL ANALYSIS

*Instrument: `eyeholdout.py` (7/7 gate, one defect caught pre-corpus). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. The design, and why the naive version was rejected

FR110 left one internal route to adjudicating the reopened repair fork: the
FR37/FR38 out-of-sample methodology, never applied to repair B.

**CHALLENGE I rejected the naive form.** Comparing leave-one-pair-out rates
between the two repairs discriminates nothing: both repairs were *selected* for
injectivity-cleanness, so both models are coherent by construction and both
would score near 100%.

**The sharp form** uses the discarded instance as held-out evidence. Repair A
asserts East 1@68 spurious and builds without it; if A's model nevertheless
predicts East 1@68's cells, that instance behaves like genuine shared plaintext
and A discarded something real. Mirrored for repair B and East 4@51.

**Built-in negative control (R2, pre-registered):** East 3@101 is discarded by
*both* repairs and priced at coincidence grade by FR15. A sound method must
fail to predict it.

---

## 1. A defect caught by the gate, before corpus contact

The first build scored **14 of 27 random pairs as "predicted" — 52%** against
FR37's published 1.2% chance rate. Cause: a pair with a single determined cell
agrees with itself trivially. FR37's rate implies at least two determined cells
were required; pairs with fewer are **untestable, not predicted**.

Corrected, the chance rate falls to **1 of 14 (7%)** and in-sample prediction
still works (10 cells, agreeing). The gate is the reason this was found before
the measurement rather than after it.

---

## 2. The result — everything is predicted, including the control

At the shared clean ratios `{8, 9, 22, 40}`, where both repairs are
injectivity-clean:

| model | held out | pool pairs | testable cells | verdict at all four ratios |
|---|---|---:|---:|---|
| A | **East 1@68** (A calls spurious) | 11 | 20 | **PREDICTED** |
| A | East 3@101 (**control**) | 6 | 8 | **PREDICTED** |
| B | **East 4@51** (B calls spurious) | 3 | 6 | **PREDICTED** |
| B | East 3@101 (**control**) | 6 | 10 | **PREDICTED** |

> **[R2] The control is predicted under both models.** An instance that both
> repairs agree is spurious — and that cannot be included without producing
> contradictions — is nevertheless predicted by models built without it.
> **The method cannot separate genuine from spurious, and no verdict is
> drawn.**

The finding is doubly robust: even setting the control aside, **[R3] the two
candidates behave identically** (both predicted), so no verdict would follow
either way.

---

## 3. Why the test fails, and why that is itself informative

The mechanism is FR38's own result, seen from the other side. FR38 established
that the thirteen classes are **mutually predictive** — removing an entire class
and rebuilding still predicted 41 of 41 of its held-out cells, because *what one
class asserts, the others already imply*.

That coherence is exactly what defeats this discriminator. Removing **one
instance** of a class leaves its siblings in the pool — five of six for #M, six
of seven for #M⁻ — and those siblings carry the pattern. The removed instance's
cells are then constrained by its own class's other instances regardless of
whether that particular occurrence is genuine.

**The model's coherence, which FR37 and FR38 established as its greatest
strength, is precisely what makes instance-level holdout blind.** A test can
measure whether a *class* is redundant with the rest of the atlas; it cannot
measure whether one *occurrence* of a well-attested class is real.

---

## 4. Consequence — the fork is closed to internal analysis

Every internal route to adjudicating FR25's fork has now been tried:

| route | outcome |
|---|---|
| Injectivity (FR47) | gauge-contaminated — ratio 1 only (FR109) |
| Likelihood ratio on the passage (FR48) | collapsed with it (FR109) |
| Embeddedness (FR2, FR27) | atlas nesting, 0 of 43 containments incidental (FR110) |
| Minimal cores (FR25) | East 3@101 is in both repairs — no discrimination |
| **Out-of-sample holdout (FR37/FR38 method)** | **invalidated by its own control (this cycle)** |

> **The repair fork cannot be settled from inside the corpus.** Repair A remains
> the conventional reading, repair B a live alternative at five ratios, and the
> AB reading the conservative option asserting strictly less.

**This is a definite answer, not a failure.** FR110 posed the disjunction — "if
B scores comparably, the fork is closed to internal analysis and only
acquisition can settle it" — and this cycle returns the second branch. The
question moves entirely to acquisition, where the spec already handles it:
recovering the drift ratio adjudicates the fork unless it lands in the four-way
overlap `{8, 9, 22, 40}`.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Repair fork** | reopened (FR109), unsupported (FR110) | **closed to internal analysis** — every route exhausted |
| Instance-level holdout prediction | untried on the fork | **invalid** — control instance predicted by both models |
| FR37/FR38 methodology scope | tested pairs and classes | **cannot test single occurrences** of a well-attested class; siblings carry the pattern |
| Prediction testability | ≥1 determined cell | **≥2 required** — one cell agrees with itself (52% vs 7% chance rate) |
| Route to settling the fork | internal cross-validation | **acquisition only** |

---

## 6. Model status

Standing reading (repair A, by convention): 384 relations over 56 glyphs;
injectivity clean at 17 ratios; exposure 74.1%; components
(25, 11, 7, 3, 2, 2, 2, 2, 2). Live alternatives: repair B (393 relations,
55 glyphs, 5 ratios), AB (259 relations, 55 glyphs, 27 ratios). **The choice
among them is now formally an acquisition question.** Cumulative: 27.16 billion
candidates, zero survivors.

---

## 7. Horizon

1. **Nothing further is owed on the repair fork.** Re-running any internal test
   would re-cover exhausted ground; the acquisition spec already records the
   fork-resolution ratio check. Do not reopen without a genuinely new form of
   evidence.
2. **Continue the gauge audit** (FR107 horizon 3). Three targets examined, two
   broken (FR109's repair, FR110's embeddedness by a related mechanism). The
   remaining candidates — FR27's packing residual curve, the gauge ladder
   (0/82, 0/82, 82/82), FR21's injectivity census — are unchecked, and the hit
   rate so far argues for finishing the sweep.
3. **A standing methodological note for the doctrine.** FR38's mutual-predictivity
   result and this cycle's failure are the same fact: a coherent model cannot
   be probed at the granularity of a single instance. Any future test that
   removes one occurrence and asks whether the model notices will return the
   same non-answer.
