# Field Report 199 — UNIQUENESS BECOMES A THEOREM, AND THE ASSUMPTION SURFACE THAT REMAINS: EVERY UNTESTED PREMISE, WITH THE TOOLING TO ATTACK EACH

*July 2026. Cycle: EYESPIRAL-C, CHALLENGE phase over the certified record.
The question posed: what can still be assumed, tested, and attacked without
community input. Part I is the first attack, executed live — it overshot a
feasibility probe into a proof. Part II is the surface itself.*

---

# PART I — THE THEOREM (instrument: `eyeproof.py`, gates 4/4)

## I.1 Statement

**With the atlas pool mandatory, the corpus has exactly one maximal
consistent class set — provably, not by sampling.**

## I.2 Proof

Row-system consistency is subset-monotone: any subset of a consistent system
is consistent. Measured on the mandatory system: **50 of 208 classes are
individually inconsistent with the pool** — by monotonicity, none can belong
to *any* consistent set containing the pool. The remaining **158 are jointly
consistent** — all coexist in one system. Let `S` be any maximal consistent
set containing the pool. `S` can contain only survivors; for any survivor
`c`, `S ∪ {c} ⊆ pool + all 158`, which is consistent — so by maximality
`c ∈ S`. Therefore `S = pool + all 158`. ∎

The forced set's signature is the certified object exactly: 794 relations,
61 glyphs, 8 equalities, sha `7e9ab7231a6eb285…`.

## I.3 Gates

```
G1 control-negative  classes-only system (known: 68 readings) -> 16 joint
                     conflicts among survivors. The method can say no.    PASS
G3 planted           a fabricated conflicting class is detected.          PASS
G4 identity          forced set == certified object, sha exact.           PASS
G5 joint             158 survivors, 0 conflicts.                          PASS
```

## I.4 What this changes

The measure-zero caveat carried since FR162 — "sampling cannot exclude a
reading reachable only on exotic orders" — is **eliminated**. The 795,545 ×
2-machine campaigns (FR196/197) are re-scoped from evidence to
corroboration: 795,545 independent confirmations of a theorem. The
uniqueness claim now has no epistemic tail at all.

Reconciliation notes, so no zombie discrepancies survive: the historical
"143 accepted classes" figure (FR164 table) was the **consensus heuristic's
basin count** — a quantity `eyegauge`'s own docstring warns is not
satisfiability; the true accepted set is 158, and the two never measured the
same thing. The 50 dead-on-arrival classes sit adjacent to FR151's 48
non-co-plaintext classes; the near-match is noted without forcing identity —
the definitions differ (48 measured co-plaintext failure, 50 measure
pool-inconsistency under repair C).

---

# PART II — THE ASSUMPTION SURFACE

Everything below is testable with zero community input. Ranked by expected
value. For each: the assumption, why it is genuinely live, the attack, its
gates, and what *both* outcomes buy.

## A2 — "The transcription is correct at all 1,036 positions" — now the largest untested premise in the record

**Why live.** `corpus.json`'s own provenance: *"validated against journal
entry 005 spot-check (first 10 trigrams) and entry 002 lengths."* Ten of
1,036 positions checked. Every relation, class, and the theorem itself sit
on this. FR174 re-verified the *sprites*, never the full stream.

**Attack — `eyefuzz`.** Three passes. (1) *Confusion model from geometry:*
a misread eye is an adjacent orientation, so each glyph's plausible
confusions are a small structured set, not 82 alternatives — build the set
from the five-sprite geometry. (2) *Sensitivity map:* perturb each position
through its confusion set, rebuild via the parity-gated mirror, record
whether the forced set survives / shrinks / gains. Positions whose
perturbation is invisible retire from concern; load-bearing positions get
flagged for manual re-verification against source imagery — a finite,
targeted checklist instead of 1,036 acts of faith. (3) *Error hunt:*
positions where a plausible confusion **increases** global consistency
(fewer DOA classes, longer reading, merged fragments) are transcription-
error candidates. Priority target: **East 1@68** — five independent lines
mark that instance spurious; if a single-eye misread at or near it
reconciles the instance, the record's one repair dissolves into a typo.

**Gates.** Planted: inject a known error into a copy, `eyefuzz` must locate
it; null: random perturbations must *lower* consistency at the measured
base rate. **Payoffs.** Robust ⇒ the data layer closes and the theorem
inherits it. An error found ⇒ potentially a fragment merge (one fewer
unknown constant — direct progress toward solution) or the E1@68 story
completed. Cost: one cycle; compute is mirror-rebuilds × confusion set,
batchable.

## A3 — "The 208-class scan is complete at its thresholds" — the only internal route to more than 79.1%

**Why live.** The 22 unconstrained glyphs (217 positions) are invisible *to
the current constraint pool* (FR135). The pool came from one scan at one
parameter point. FR135's proof is conditional on that pool.

**Attack — `eyescan2`.** Sweep scan parameters (minimum span, exactness
tolerance, dot-handling variants) with the discipline this exact terrain
punished twice (FR41's geometry-preserving nulls, FR97's negative
control): every candidate class from a relaxed setting is priced against
permutation nulls, then adjudicated by the **FR146 out-of-sample
certification pipeline** (the machinery that admitted the 19 at 100% vs
2.8%). Admitted classes re-enter `eyeproof` — the theorem recomputes in
minutes. Target the scan at spans touching the 22 first.

**Payoffs.** New certified classes ⇒ exposure above 79.1%, possibly reach
into the 22, possibly fragment merges. Clean null across the sweep ⇒ FR135's
invisibility proof upgrades from pool-conditional to sweep-conditional —
the 22 close harder. Cost: one to two cycles.

## A5 — the two unexplained numbers left anywhere in the record

FR102's **29th excess dimension** (28 of 29 were local wiggle; the last was
never named — almost certainly the global scale, but *named* is the
standard) and FR184's **+1.2σ residual** (logged, never characterized).
**Attack — `eyedim`:** nullspace decomposition of the FR102 alignment
solve, each basis vector classified; re-run FR184's statistic on the
certified reading with its original null. Payoff either way: the record
reaches zero unexplained quantities, or one of them is real and small
things that are real have been the best leads in this series. Cost: an
evening.

## A6 — the last inherited input: Toboter's reading-order derivation

Reproduce in-house: `eyeorder`, the 0–82 unbroken-census over all digit
conventions. Expected: exactly the known six symmetric orders. Cost:
trivial. Value: the assumption ledger reads *empty* afterward — every input
either derived here or reproduced here.

## A4 — index/AP laws for the base vector — **closed by inspection, no tooling needed**

Any law `b_m = ρ·f(m)+c` with `f` injective over messages (every index
scheme, any ordering; any arithmetic progression) requires nine distinct
`b` values. The vector has two forced equalities (`E1=W1`, `E4=E5`).
All such laws are refuted at once. Logged so no cycle re-derives it.

## A7 — the inner layer (gated on the L-8 ruling; listed for completeness)

If ruled in scope, two instruments are fully specified and null-disciplined:
**`eyestream`** — the FR182 survivor: candidate base-83 digit streams
(pre-registered list: 16807, 2³¹−1, `0xe4bc7e0`, release timestamps, the
Mnemonica sequence, π/e/φ) matched against fragment 1's 491-position
equality structure, drift- and offset-free, shuffle nulls. **`eyegram2`** —
what FR173's uniformity did *not* cover on the certified reading: lag
correlations, positional periodicity in `p`, cross-message correlation at
equal `t`. A null from either still pays: it prunes FR182's surviving
explanations for the flatness. If L-8 stays closed, neither runs — and the
record should say so once instead of carrying the ambiguity.

## Execution order

**A2 → A3 → A5/A6 → (A7 iff L-8).** A2 first because it is now the single
largest untested premise under everything, including Part I; A3 second
because it is the only remaining internal path to new corpus coverage; A5/A6
close the ledger to zero; A7 awaits the one ruling only the principal can
make.

---

## Doctrine changes

| item | prior | now |
|---|---|---|
| uniqueness | certified at 795,545 with sampling caveat (FR197) | **proven** (Part I); campaigns re-scoped to corroboration |
| accepted-class count | "143" in circulation | **158**; 143 was the consensus-heuristic basin, a different quantity |
| assumption ledger | "audited shut" (FR197) | four live items enumerated with attacks (A2, A3, A5, A6); one closed by inspection (A4); one scope-gated (A7) |
| transcription fidelity | implicit | **named as the largest open premise**; spot-check provenance quoted |

## Horizon

1. `eyefuzz` — build and run (A2). 2. `eyescan2` (A3). 3. `eyedim` +
`eyeorder` (A5/A6). 4. The L-8 ruling, whenever it comes. The external asks
(ACQUISITION_SPEC v2) stand unchanged and now rest on a theorem.
