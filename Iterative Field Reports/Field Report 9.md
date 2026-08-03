# Field Report 9 — Nine Gauges, and the Opening Contradicts the Body

**Series note.** Ninth report of the iterative series. This cycle asked how many
gauges the corpus needs, caught a methodological error of my own that would have
invalidated the answer, re-derived everything with a sound oracle, and arrived at a
result that retires one of the series' own headline deductions. Instrument
`eyegauge.py`, selftest 7/7 green with one measured power note.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
results conditional on the static additive family under FR7's sound-rows reading —
with the drift multiplier now swept rather than assumed.

**One-paragraph verdict.** The corpus requires **per-message effective offsets**.
A single global gauge — FR4's one-gauge deduction, which concluded the whole corpus
is one monoalphabet in u-space — is **unsatisfiable against the sound constraint
inventory at every one of the 82 non-degenerate drift multipliers**, and so is the
per-triplet (three-gauge) model; the per-message model is satisfiable at all 82,
reproducing the doctrine's drift-degeneracy certificate. **FR4's one-gauge
deduction is therefore refuted**, drift-independently. The base-equality matrix
localises this: within triplets, only the E1/W1 near-dup pair may share an offset —
E1/W1 vs E2, E3 vs W3, and all three T3 pairs are forbidden, at every drift tested.
And the sharpest consequence: the literal opening identities that FR3 mapped (T1
identical over positions 1–24, T3 over 1–20) turn out to be **absent from the
constraint pool** — the calibrated anchor (rep = 4) rejects those windows — and when
they are added, they **contradict the body atlas**. The openings force exactly the
offset equalities the body forbids. Minimal exhibit for the T3 opening: the class
pair (#1, #2). The corpus's two strongest bodies of evidence, the shared openings
and the certified isomorph classes, cannot both be shared plaintext under a common
per-message offset.

---

## 1. Corrections first — including one that nearly invalidated the cycle

**I used the wrong satisfiability oracle for most of this cycle.** I inferred "the
system is unsatisfiable" from `consensus_alphabet` returning kept < total. That
inference is invalid: `consensus_alphabet` is a heuristic — deterministic restarts,
greedy purify-to-fixed-point, keep whichever basin *explains* the most pairs — so it
can drop pairs merely because the chosen basin does not explain them. This is FR6's
greedy-subset trap wearing a new hat, and I walked into it despite having written
that lesson myself. Caught by a plant that made no sense: masking rows (asserting
strictly *less*) made a plant look *less* satisfiable, which is impossible. The
sound test is direct Gaussian elimination over all rows, which is order-independent
and exact. **Every result below was re-derived with the sound oracle**; they all
survived, and the base-equality matrix came out identical — but that is luck, not
licence, and the selftest now carries an explicit negative gate asserting the two
disagree on a known-satisfiable system (sound = SAT while the heuristic keeps 41/45).

**A pre-registration I got wrong.** I registered that cross-triplet base merges
would be *vacuous*, reasoning that a free base gap absorbs the per-triplet keystream
constant. Wrong: the row generator carries no separate κ, so its base variable *is*
the effective per-message offset, and merging two of them asserts equal effective
offsets — substantive in any pairing. Six cross-triplet prohibitions are real
findings, not artifacts. Registration retracted in the instrument and here.

**Two plant generations were discarded.** A hand-built two-class toy could not
produce contradictions at all: with no within-message instance pairs, a wrong merge
is just a consistent relabelling. The replacement follows FR7's doctrine — certified
corpus geometry is the right plant spec — regenerating synthetic plaintext over the
*real* atlas instance geometry under known offsets. It now gates sensitivity
correctly: an equal-offset plant is consistent under one gauge (no fabricated
prohibition), a distinct-offset plant is not.

**A measured limitation, not asserted away.** On the geometry plant, pairwise merge
detection fired 0/36 while the global one-gauge test fired reliably. Pairwise power
depends on how tightly two messages are coupled by shared classes. Therefore: a
corpus **"forbidden" verdict is exact** (a genuine unsatisfiability proof), while a
corpus **"permitted" verdict is weak evidence** — absence of coupling, not evidence
of equal offsets. The permitted cells in §3 must be read that way.

## 2. The gauge ladder

Sound pool: 65 atlas pairs (pattern rows) + 18 strict pairs (dot-masked) = 83, the
FR7 tier. Drift swept over all 83 multipliers; d = 0 is excluded by construction —
it asserts q[D] = q[A] at every aligned cell, merging symbols, and since GF systems
carry no injectivity it is always satisfiable and always degenerate (pin-grade 0,
all symbols collapsed to one value). The guard is in the selftest.

| model | satisfiable at d = 1 | non-degenerate drifts satisfiable |
|---|---|---|
| 1 gauge (pure / FR4 one-gauge) | **NO** | **0 / 82** |
| 3 gauges (per-triplet) | **NO** | **0 / 82** |
| 9 gauges (per-message) | YES | **82 / 82** |

Two readings fall out. First, the corpus needs nine gauges: neither a single global
offset nor a per-triplet offset can carry the certified isomorph inventory, and this
is not an artifact of the drift = 1 that both repo row generators hardcode — no drift
rescues it. Second, the per-message row being satisfiable at *every* drift is the
drift-degeneracy certificate the doctrine already holds (eyedrift): with nine free
offsets, drift is unidentifiable. The two rungs are complementary — the freedom that
makes the model fit is exactly the freedom that makes drift unrecoverable.

## 3. The base-equality matrix

For each message pair, merge their offset variables and test satisfiability.

```
      E1 W1 E2 W2 E3 W3 E4 W4 E5
E1     .  o  X  o  X  X  o  o  o
W1     o  .  X  o  X  X  o  o  o
E2     X  X  .  o  X  X  o  o  o
W2     o  o  o  .  o  o  o  o  o
E3     X  X  X  o  .  X  o  o  o
W3     X  X  X  o  X  .  o  o  o
E4     o  o  o  o  o  o  .  X  X
W4     o  o  o  o  o  o  X  .  X
E5     o  o  o  o  o  o  X  X  .
```

**Forbidden within-triplet (6):** E1/E2, W1/E2, E3/W3, E4/W4, E4/E5, W4/E5 — every
within-triplet pair except E1/W1 and W2's two. **Forbidden cross-triplet (6):** the
whole T1 trio against E3 and W3. Every prohibition holds at drifts 1, 2, 3, 17, 41,
82; E1/W1 is permitted at all of them. W2 is permissive with everything, which per
§1 means only that W2 is weakly coupled — it appears in few classes.

The one within-triplet permission is interpretable: E1 and W1 are the near-dup pair
with literal Δ = 0 identity across the opening and a 13-long body run, exactly what
equal offsets under a shared keystream would produce.

## 4. The opening/body contradiction

Two facts collide.

First, an inventory gap I did not expect: **the literal opening identities are not
in the constraint pool at all.** The strict scan calibrates its anchor at rep = 4 —
four repeated values inside a 13-window — and the opening windows do not qualify, so
zero strict pairs fall in the opening region, and the scan only ever touches W1 and
E2. Every pin the doctrine carries was computed without the corpus's most literal
shared spans.

Second, when those spans are added as exact Δ = 0 pairs — verified literal against
the corpus at runtime — the system breaks:

| pool | verdict |
|---|---|
| sound pool alone | SATISFIABLE |
| + T1 openings (E1/W1/E2 over 1–24) | **CONTRADICTION** |
| + T3 openings (E4/W4/E5 over 1–20) | **CONTRADICTION** |
| openings alone | satisfiable |
| strict tier + openings | satisfiable |

The mechanism is exactly §3: an exact Δ = 0 pair between two messages forces their
offsets equal (the selftest verifies this equivalence), and those are precisely the
equalities the body atlas forbids. Minimal exhibit for the T3 opening: the class
pair **(#1, #2)** — a T1 class and a T3 class, chaining through shared symbols. The
T1 opening needs more than two classes.

## 5. What this refutes, and the fork it opens

**FR4's one-gauge deduction is refuted.** It concluded from the universal header
plus FR3's drift equality that all nine effective offsets are equal and the corpus is
a single monoalphabet in u-space. The sound inventory rules that out at every drift.
The T1 tier of that argument was always the weak link (FR4 itself priced it at
~2.2σ, later ~3.5σ); the failure is now hard rather than probabilistic.

Something in the conjunction must go, and the honest position is a fork rather than
a pick:

- **(a) The opening blocks are not shared plaintext under the body's cipher
  parameters.** The most economical option, and it has independent support: position
  0 is a per-message indicator, positions 1–2 are universal, and the whole opening
  behaves like a structural prelude. If the openings are a literal header rather than
  encrypted shared text, they impose no offset constraint and the contradiction
  dissolves — but FR3's depth-stack and FR4's header argument both lose their
  foundation, and the crib real estate FR3 recommended stops being plaintext.
- **(b) Some atlas classes are not same-plaintext.** FR6/FR7 established the classes
  are mutually consistent under sound rows, but consistency is weak evidence (FR6);
  the cross-triplet classes are the natural suspects.
- **(c) The progressive model fails** — for instance the offset is not constant
  within a message, which would break the single-base-per-message assumption that
  both the ladder and the matrix are built on.

**What is unaffected.** FR3's drift *equality* (derived from cross-triplet increment
equalities, which cancel offsets) and its literal cartography as observation. FR6's
epistemology, FR7's sound-rows repair, FR8's collapse theorem. FR7/FR8's per-message
certifications are in fact *vindicated*: the ladder shows per-message freedom is
required, so the 10-certified/8-pin inventory was computed under the right model.

## 6. Horizon

(1) **Decide the fork.** The sharpest discriminator available: test whether the
opening contradiction survives when each suspect class is removed in turn — if a
single class family carries it, (b) gains; if it is robust to every removal, (a) or
(c). (2) **Re-price the openings for cribs.** Under (a) the opening stack FR3
recommended as the densest crib real estate is not plaintext at all; before any crib
work goes there, the fork must resolve. (3) **Anchor calibration as a first-class
knob.** The rep = 4 calibration silently excluded the corpus's most literal spans
from every pin computation the project has made; a calibration sweep is now a
doctrine-level item, not a tuning detail. (4) FR8's bridge-symbol search remains
queued and is unaffected.

## 7. Reproduction

`eyegauge.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` for
the 7-check gate — geometry-plant sensitivity both directions, matrix soundness, the
negative gate proving the consensus kept-count is not a satisfiability oracle, two
oracle unit tests, the d = 0 degeneracy guard, and the exact-pair/base-merge
equivalence, plus the measured pairwise-power note. Full run reproduces the baseline
guard (22/19/16), the opening-region inventory gap, the ladder, the matrix with
drift-robustness, the opening/body test and the minimal exhibits. All failures carry
prefix `XD-MBYG04K-URS3LF`.
