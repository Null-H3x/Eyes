# Field Report 23 — The Package Passes Because It Says Nothing

**Series note.** Twenty-third report of the EYESPIRAL series. FR22 read injectivity as
selecting FR16's coherent package out of a 2×2 of model choices. This cycle asks the
question FR22 skipped — how much does each cell actually *determine* — and the answer
withdraws FR22's headline. Instrument `eyedeterm.py`, selftest 6/6 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Measuring determination the sound way — per pair, asking
whether q[b] − q[a] = d is implied for exactly one d — gives a census that reframes the
last two reports. The global-drift pool determines **276** pair-differences across 49
symbols, and is refuted by injectivity. The per-triplet full pool determines **6** — and
those six are *precisely* the six false equalities. FR16's coherent package determines
**zero**. So the package does not satisfy injectivity on positive grounds: a system that
forces no differences cannot force an equality, and it passes the check vacuously.
FR22's claim that injectivity independently selects the package is **withdrawn**. The
doctrinal consequence is larger and uncomfortable: the pin inventory the project carries
— 16 strict pins, and FR7's 10 certified / 8 pin-grade — is computed under the
global-drift model that FR21 and FR22 refute, while **under the model that survives, the
corpus determines no alphabet relation at all.** Stated exactly, the wall is this: the
models that determine things are refuted, and the model that survives determines
nothing.

---

## 1. Corrections first

**FR22's headline is withdrawn.** It reported that of four configurations only
per-triplet-with-bridge-removed showed no forced collisions, and read that as
injectivity independently selecting FR16's package — "the strongest corroboration the
package has received." The reading was wrong because I never checked what the surviving
cell determines. It determines nothing, so it *cannot* exhibit a forced equality. Passing
a consistency check by asserting nothing is not corroboration, and I should have applied
Challenge I to my own result rather than to the next cycle's framing.

The finer detail makes it sharper: under the per-triplet **full** pool the model
determines exactly six pair-differences, and all six are the injectivity violations.
Remove the bridge and the six determinations and the six violations vanish *together* —
they were the same fact.

**`certified_domain` is unreliable outside the single-gauge case.** It pins the
reference to two values and keeps whatever co-shifts, which is sound when the global
rotation is the only freedom. Under the per-triplet model there are thirteen free
parameters, and the routine claims **10 certified symbols in a system with zero forced
differences**. FR8 and FR9 both recorded the underlying principle; this is the first
time it has been shown to misfire on a configuration the series was actively relying
on. Determination has to be measured per pair, via `classify`.

## 2. The census

| configuration | symbols | `certified_domain` claims | **forced pair-differences** | symbols involved | forced equalities |
|---|---|---|---|---|---|
| global drift, full pool (the doctrine) | 51 | 10 | **276** | 49 | 6 |
| global drift, reduced | 50 | 10 | 256 | 48 | 5 |
| per-triplet, full pool | 51 | 10 | **6** | 12 | 6 |
| **coherent package** | 50 | 10 | **0** | 0 | 0 |
| coherent + E4/E5 run merge | 50 | 10 | **0** | 0 | 0 |

Read the third and fourth rows together and the vacuity is plain. The per-triplet model
with the full pool determines six differences and every one of them is false. Dropping
E3@101 removes those six determinations, which is why the injectivity violations
disappear — not because the configuration is right, but because it has stopped saying
anything.

## 3. What this costs the doctrine

The project's pin inventory has always been model-relative, and the model it was
computed under is now refuted:

- the repo's **16 strict pins** — global drift;
- FR7's regrade to **10 certified / 8 pin-grade** — global drift;
- FR17's anchor leverage map (8 anchors → 51 glyphs), FR19's 67.7% exposure, FR20's 464
  usable pairs — all computed against the global-drift pool.

Under the per-triplet reading that survives injectivity, the corpus determines **no**
alphabet relation, so none of those inventories is licensed by it. They are not
*disproved* — the global-drift model might yet be rescued by finding the wrong
constraint that produces the six false equalities — but they cannot be quoted as
model-independent facts, and this series has been quoting them as though they were.

## 4. The wall, stated exactly

Twenty-three cycles have produced a consistent pattern, and this is its sharpest form.
Every configuration that resolves a contradiction does so by giving up determination:
FR8's collapse theorem, FR9's d = 0 degeneracy, FR11's Gromark collapse, FR12's family
sweep, FR13's flattened slopes, and now this. The trade has never once gone the other
way.

So the honest position is a dilemma rather than a model. **The configurations that
determine alphabet relations (global drift) assert six equalities that a permutation
forbids. The configuration that violates nothing (per-triplet, reduced) asserts
nothing at all.** Neither is a working reading of the cipher, and the space between them
is where the answer has to be: something that determines relations *and* respects
injectivity. Nothing tested in twenty-three cycles occupies it.

## 5. Where that points

The dilemma is informative about what to look for. A model in the gap would need more
constraint than per-triplet drifts allow but a different constraint than global drift
imposes — for instance drifts tied across *some* triplets but not all, or an offset
structure that is neither fully free nor fully shared. That is a small, enumerable
family, and the census in §2 is exactly the instrument for scoring it: count forced
differences, then check injectivity, and look for a cell with many of the former and none
of the latter.

That is a sharper search than anything the series has had. Previous cycles asked "is
this configuration consistent?", which every degenerate model answers yes. The right
question is "does it determine much *and* stay injective?", and only a two-dimensional
score can distinguish those.

## 6. Horizon

(1) **Sweep the intermediate offset/drift structures** — the 2×2 was too coarse; between
one global drift and three free ones lie the partial tyings (T1=T2 only, T2=T3 only, and
so on), each scored by forced-difference count *and* injectivity. (2) **If a cell scores
well, re-derive the pin inventory there**, and recompute FR17/FR19/FR20's numbers
against it. (3) **If no cell scores well**, that is itself a strong result: it would say
the additive-progressive family cannot carry this corpus at all, which is a much larger
claim than any single exclusion so far. (4) Standing: #2⁻'s instance-level audit, the 15
candidate glyphs.

## 7. Reproduction

`eyedeterm.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs
the 6-check gate — the global pool determining many differences, its forced equalities
matching the six injectivity violations, the coherent package determining nothing and
therefore forcing no equality, the `certified_domain` over-report demonstrated directly,
and the baseline guard. The full run reproduces the C1 census and the C2–C4 readings.
Failures carry prefix `XD-MBYG04K-URS3LF`.
