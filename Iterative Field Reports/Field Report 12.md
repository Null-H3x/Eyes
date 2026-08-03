# Field Report 12 — Progressive Is Selected, Then Killed

**Series note.** Twelfth report of the iterative series. FR11's horizon nominated
"constrained Gromark" as the untested middle of the trilemma. Rather than test one
Gromark, this cycle sweeps the **entire family of keystreams obeying a two-term linear
recurrence** — 6,889 members, containing every Gromark variant and the progressive
keystream alike — and settles the corner in one pass. Instrument `eyerecur.py`,
selftest 8/8 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Two results, one positive and one negative, from the same
sweep. **Positive:** against the atlas classes alone, **progressive is the unique
non-degenerate survivor of all 6,889 two-term linear recurrences.** Every other
member — Fibonacci Gromark included — fits only by collapsing its keystream to a
constant over the region the pairs occupy, which is monoalphabetic and excluded by
FG1. This is the first time the series has *selected* a model rather than excluded
one, and it explains structurally why progressive has carried SUPPORTED status: the
corpus's within-triplet isomorph shifts have **gcd 1**, and a constant offset
difference at coprime shifts forces the characteristic root λ = 1, which is exactly
the arithmetic keystream. **Negative:** add the literal openings and the survivor set
becomes **empty**. No two-term linear-recurrence keystream can carry both the
certified atlas classes and the literal opening identities. FR11's nominated rescue
for premise (iii) is therefore closed: constrained Gromark cannot save it, and neither
can any of its 6,888 relatives.

---

## 1. Corrections and negatives first

**The degeneracy guard was wrong three times, and each failure was different.** This
is the cycle's methodological content, so it goes first. (i) My first guard asked
whether the seed difference K[1] − K[0] is forced to zero. For β = 0 the K[0] seed is
*decoupled* — it never feeds the recurrence — so the difference is never forced, and
all 83 members of the β = 0 family were wrongly reported LIVE. (ii) Rewriting it to
test consecutive keystream differences did not help, because I still evaluated t = 0
first and broke on it — the same decoupled seed by another route. (iii) Restricting to
t ≥ 1 left one survivor, (0,0), whose keystream is identically zero from t = 2 onward:
constant across the whole body, but with a blip at t = 1 that the guard counted as
structure. The final guard tests constancy **over the position range the pairs
actually occupy** — [18, 109) — which is the only range where the question has
meaning. Every intermediate result in this cycle before that fix was an artifact, and
the lesson generalises: a degeneracy test must be evaluated on the domain the evidence
lives on, not at the seeds.

**A red flag I had to chase down.** Midway, my formulation reported progressive +
openings as *satisfiable*, contradicting FR10. The cause was that treating the drift as
a free variable lets the solver choose drift = 0 — the degenerate case FR9 excluded by
sweeping only nonzero drifts. To be sure FR10 was not the error, I re-ran its opening
contradiction across **all 82 non-degenerate drifts** rather than the single drift = 1
it originally used: 0/82 satisfiable, for T1 openings, T3 openings, and both. **FR10
stands, now on a complete sweep rather than one drift value.**

**No pins gained.** This cycle prices a model family; it certifies nothing new about
the alphabet.

## 2. Why the whole family is tractable at once

Under K_g[t] = α·K_g[t−1] + β·K_g[t−2], perfect isomorphy of a pair at shift Δ requires
the offset difference K[p₂+i] − K[p₁+i] to be constant across the span. That difference
obeys the same recurrence, and a constant c satisfies it iff c·(1 − α − β) = 0.

- **α + β ≢ 1:** only c = 0 survives — the keystream must repeat *exactly* at that
  shift.
- **α + β ≡ 1:** the characteristic roots are 1 and λ = α − 1, so K[t] = A + B·λ^t and
  the shift difference is B·λ^{p₁+i}(λ^Δ − 1). Constant across a span of length ≥ 2
  forces B = 0 (constant keystream), or λ = 1 (progressive), or λ^Δ = 1 (difference
  identically zero).

The corpus supplies within-triplet pairs at Δ = 1, 2, 3 with spans up to 33, and the
shifts have **gcd 1**. So λ^Δ = 1 for all observed Δ forces λ = 1. The algebra predicts
progressive as the unique non-degenerate member; the sweep tests that rather than
assuming it, and the selftest verifies both the constant-sequence criterion and the λ
characterisation numerically.

## 3. Results

Named models against the full pool plus openings:

| recurrence | model | verdict |
|---|---|---|
| (2, 82) | progressive / arithmetic | DEGENERATE |
| (1, 1) | Fibonacci Gromark | DEGENERATE |
| (1, 0) | constant keystream | DEGENERATE |
| (0, 0) | null keystream | DEGENERATE |

Full sweep over all 6,889 recurrences:

| pool | contradicted | degenerate | **LIVE** |
|---|---|---|---|
| atlas classes only | 0 | 6,888 | **1 — (2, 82), progressive** |
| atlas classes + literal openings | 0 | 6,889 | **0 — family excluded** |

Note the exclusion mechanism: nothing is *contradicted*. Every member is formally
satisfiable, and all but progressive fit only by driving the keystream to a constant —
which is absorbed into the per-message base and leaves a monoalphabet. Satisfiability
without determination is not a model, a point this series has now had to make in four
separate cycles (FR8's collapse, FR9's d = 0, FR11's Gromark, and here).

## 4. What this settles

**Premise (iii) cannot be rescued by a linear keystream.** FR10 identified the
progressive assumption as the cheapest premise to drop; FR11 showed the unconstrained
general-K that replaces it is vacuous, and nominated constrained Gromark as the
remaining hope. That hope is now closed — every Gromark is a two-term linear recurrence
with a primer, and the whole family dies with the openings included.

**Progressive's SUPPORTED status is explained, and simultaneously bounded.** The
atlas geometry *selects* progressive uniquely among linear keystreams. That is a real
structural fact and it is why the model has fit so well for so long. It is also why the
opening contradiction is so sharp: the one keystream the body evidence picks out is the
one the openings forbid.

**The trilemma narrows to three live branches:** (i) the literal openings are not
shared plaintext; (ii) some certified atlas classes are not same-plaintext (expensive —
FR10's shuffle null puts them at z = ∞); or (iii′) the keystream is **non-linear** —
outside the two-term recurrence family entirely, and constrained enough not to be
vacuous. FG5's "general aperiodic K" is (iii′), and FR11 already showed its
unconstrained form determines nothing.

## 5. Horizon

(1) **(iii′) needs a candidate with structure.** The natural next family is a
*table-driven* or PRNG-driven keystream — Petri's documented Park-Miller/Schrage
habits and the double Fisher-Yates idiom are the obvious priors — where K is
pseudorandom but reproducible, so it constrains without being free. The test shape is
already built: supply K's generator, ask whether the atlas classes plus the openings
survive. (2) **Higher-order linear recurrences** (three- and four-term) are a cheap
extension of this sweep and would close the linear corner completely rather than for
order 2 alone. (3) **Branch (i) deserves its own direct test**: FR11 nominated
extending the agreement statistic into the opening spans, which remains undone and does
not depend on any keystream model. (4) Standing: FR8's bridge-symbol search, anchor
calibration at rep = 4.

## 6. Reproduction

`eyerecur.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs
the 8-check gate — recurrence-table correctness for progressive and Fibonacci, the
constant-sequence criterion, the λ characterisation, the corpus gcd premise, a positive
control (progressive LIVE on the pool alone) and two guard-sanity checks (constant and
null keystreams must read DEGENERATE). The full run reproduces the baseline guard
(22/19/16), the named-model table, and both sweeps. Failures carry prefix
`XD-MBYG04K-URS3LF`. The algebra in §2 is checkable by hand in a few lines; the sweep
takes a few minutes.
