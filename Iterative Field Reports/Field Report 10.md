# Field Report 10 — The Contradiction Is Progressive-Specific

**Series note.** Tenth report of the iterative series. This cycle discharges FR9's
horizon item 1: resolve the fork left by the opening/body contradiction. Instrument
`eyecore.py`, selftest 5/5 green, built on FR9's sound (direct-Gaussian)
satisfiability oracle and FR7's sound rows.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR9's fork sharpens into a **trilemma**: exactly one of
(i) the literal openings are shared plaintext, (ii) the certified atlas classes are
same-plaintext, (iii) the offset is linear in position, must fail. This cycle prices
all three. Premise (ii) is expensive: the implicated classes are real — 12-long
isomorphs with three repeats occur **53 times in the corpus and zero times in 30
unigram-preserving shuffles** — and rescuing progressive by discarding classes takes
at least three or four of the thirteen, spread across the #2-family, the #3-family
and #M⁻, because the contradiction has **multiple independent minimal cores**, not
one. Premise (i) costs FR3's depth-stack reading and the opening crib real estate.
Premise (iii) costs the least and resolves everything: rerunning the identical
constraint system with the **only** change being the keystream reading — from
progressive (within-triplet offset difference at shift (p1,p2) forced to
drift·(p2−p1)) to Gromark/general-K (that difference a free constant, while Δ=0 pairs
still force offset equality exactly because K cancels) — makes the whole system
satisfiable: openings and all thirteen classes coexist, and within-triplet base
equality flips from forbidden to permitted. **The contradiction is specific to the
linear-offset assumption.** The honest caveat, built into the instrument: Gromark rows
are strictly weaker, so their fitting is expected and is not evidence *for* Gromark —
the informative direction is that per-message progressive, the doctrine's SUPPORTED
model, made a sharp prediction here and it failed.

---

## 1. Corrections and negatives first

**A greedy result I had to walk back mid-cycle.** An early probe reported that
dropping just two classes (#3, #3+) restores satisfiability. The instrumented run
shows the greedy path actually needs four for the T3 opening (#3, #2⁻, #3+, #2) and
three for T1 (#2⁻, #2, #2+) — and the two runs differ only in which class each round
happens to drop first. Both are valid greedy paths; neither is a minimum. This is
FR6's greedy-subset lesson applying to hitting sets, and the instrument now prints
the caveat next to the result: **the count is an upper bound on the minimum hitting
set, not a minimum.** What is robust across paths is the qualitative fact — no single
class carries the contradiction.

**Two plant generations discarded, and the reason is now a standing rule.** A
synthetic corpus built over the real atlas geometry with an engineered non-linear
keystream would not reproduce the contradiction: random plaintext lacks the
cross-context symbol collisions that turn wrong constants into cycles. This is the
same wall FR7 hit. The gate therefore uses the FR7 remedy — a **certified corpus
exhibit** as the plant specification: the verified six-pair T3 core must come out
UNSAT under progressive and SAT under Gromark, with minimality re-verified at
runtime. The synthetic progressive plant is retained as the negative control (it must
show no contradiction), so the gate has both directions.

**What this cycle does not claim.** No pins were gained, no new certification. The
result is a model-family discrimination and a pricing of three premises.

## 2. The minimal ingredient

Only one opening pair is consistent with the body: **E1/W1** — the near-dup pair,
matching FR9's base-equality matrix exactly. Every other opening pair (E1/E2, W1/E2,
and all three T3 pairs) contradicts the pool on its own. And the contradiction does
**not** require the FR3 cross-triplet bridges: the within-triplet pool alone plus the
T3 opening is already contradictory. Span length is irrelevant — a two-position
prefix suffices — because the operative constraint is offset equality, not the length
over which it is witnessed.

## 3. Minimal unsatisfiable cores

Deletion filtering, each core verified minimal at runtime (core UNSAT; core minus any
one pair SAT).

**T3 opening (E4/W4), core = 6 pairs:** #M⁻ E1@40×E3@101 and E1@68×E3@101; #3
E4@51×E5@52 and W4@53×E5@52; strict W1@40×E2@80 and W1@70×E2@80.

**T1 opening (E1/E2), core = 10 pairs:** #2⁻ E4@73×E5@74 and W4@76×E5@74; #M⁻ three
pairs into E3@101; #3 two pairs; strict three pairs.

Both cores chain through all three triplets via shared refrain symbols — the same
detached island FR8 mapped. Notably the cores are small enough to audit by hand, and
neither is a single-class artifact.

## 4. Pricing premise (ii): are the classes real?

Unigram-preserving shuffle null on the isomorph search:

| window | min repeats | observed | null mean (max) | z |
|---|---|---|---|---|
| 12 | 3 | 53 | 0.0 (0) | ∞ |
| 15 | 3 | 82 | 0.0 (0) | ∞ |
| 8 | 2 | 51 | 1.4 (6) | 26.3 |

Long isomorphs are annihilated by shuffling. The implicated classes are real
structural repeats, not pattern coincidences, so premise (ii) cannot be dismissed
cheaply — and the class-localisation result says rescuing progressive would require
discarding several of them at once.

## 5. Pricing premise (iii): the model test

The same pool, the same openings, the same oracle; the only change is what the rows
assert about the within-triplet offset difference at shift (p1, p2).

| model | pool alone | + T1 openings | + T3 openings | + both |
|---|---|---|---|---|
| per-message **progressive** | SAT | **CONTRADICTION** | **CONTRADICTION** | **CONTRADICTION** |
| **Gromark / general-K** | SAT | SAT | SAT | SAT |

Under Gromark the within-triplet base merges that FR9 proved forbidden — E4/W4,
E1/E2, E3/W3 — all become permitted. The picture that emerges is coherent: within
each triplet the messages share one offset (forced by the literal openings, since a
Δ = 0 pair cancels the keystream exactly under *any* K), and the body isomorphs'
offset differences are keystream-determined constants rather than drift·Δ.

**The caveat matters and is printed by the instrument.** Gromark rows carry a free
constant per (triplet, p1, p2) where progressive rows carry none, so they are
strictly more permissive; fitting is expected and is not evidence for Gromark. What
is evidence is the failure of the sharp prediction: per-message progressive, carried
as SUPPORTED on the scoreboard, is contradicted by the conjunction of two bodies of
evidence this project treats as certified.

## 6. Where this leaves the trilemma

- **(iii) offset linear in position — cheapest to drop.** Resolves everything, keeps
  the openings as plaintext and all thirteen classes. Cost: the scoreboard's SUPPORTED
  model is downgraded, and drift ceases to be a meaningful parameter in the body.
- **(i) openings shared plaintext — moderate cost.** Also resolves it, but FR3's
  depth-stack reading and FR4's header argument lose their plaintext basis and the
  opening stack stops being crib real estate. Note (i) and (iii) are not exclusive.
- **(ii) classes same-plaintext — most expensive.** Requires discarding three or four
  certified classes that a shuffle null says are real.

I am not declaring a winner: (i) and (iii) both survive, and distinguishing them is
the natural next measurement.

## 7. Horizon

(1) **Discriminate (i) from (iii).** Under (iii)-only, the openings *are* plaintext,
so within each triplet all messages share one offset — a positive, testable
structural claim that should show up as extra certification once Gromark rows are
adopted. Under (i)-only, the openings impose nothing. Re-running the pin pipeline in
both readings and comparing what gets certified is the discriminator. (2) **Re-price
the scoreboard entry** for per-msg-progressive in light of §5. (3) **Anchor
calibration** (FR9 horizon) is still open and now more urgent: rep = 4 excluded the
openings from every pin computation to date, and under (iii) the openings are exactly
the constraints that pin within-triplet offsets. (4) FR8's bridge-symbol search
remains queued.

## 8. Reproduction

`eyecore.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs
the 5-check gate — synthetic progressive plant as negative control, the certified
corpus exhibit as the model discriminator, runtime core-minimality verification, a
satisfiable-system control, and the shuffle-null machinery. Full run reproduces the
baseline guard (22/19/16), C1 minimal ingredient, C2 verified cores, C3 class
localisation with the greedy caveat, C4 the reality null, and C5 the model test. All
failures carry prefix `XD-MBYG04K-URS3LF`.
