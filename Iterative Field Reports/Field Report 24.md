# Field Report 24 — Every Cell Fails, and Why

**Series note.** Twenty-fourth report of the EYESPIRAL series. FR23 ended by naming a
two-dimensional search: score each model configuration by how much it *determines* and
whether it stays *injective*, and look for a cell with many determinations and no false
equalities. This cycle runs that sweep across thirty configurations and finds no such
cell — then locates the reason, which is not where FR23 expected. Instrument
`eyescore.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Across five drift partitions × three base structures × two
pools, **no configuration determines a single pair-difference without also asserting a
false equality.** In every free-drift cell the two counts are *identical* — forced
differences equal forced equalities exactly, whether that is 6, 269, 439 or 0. FR23's
anticipated major negative is realised. But the sweep also exposes an axis FR23 did not
name and which matters more than the partition structure: **whether the drift is a free
parameter or fixed to a known constant.** All of the doctrine's determinations come from
fixing it. With the drift fixed, the corpus determines 276 pair-differences of which 6
are false — and that count is **identical at every drift value tested** (1, 2, 3, 17, 41,
82), so the drift *value* is not what produces determination; the *conditioning* is.
With the drift left free, determination collapses to 6 (all six false) on the full pool
and to **zero** on the reduced pool. The doctrine's pin inventory is therefore
conditional twice over: on the global-drift structure that FR21/FR22 refute by
injectivity, and on fixing a parameter that eyedrift's degeneracy certificate says
cannot be identified.

---

## 1. Corrections and method first

**A measure that made the sweep possible.** FR23's determination census tried all 83
values of d per pair — roughly 100,000 `classify` calls per configuration, far too slow
to sweep thirty of them. There is an O(1) reformulation, and it is exact:
`classify(row, 0)` returns **pivot** when the difference is free, **redundant** when it
is forced to zero, and **contradiction** when it is forced to something nonzero. One
call settles both axes. The selftest verifies the fast measure reproduces FR23's
exhaustive census on the global-drift cell (276 forced, 6 equalities) before anything is
swept.

**A key-type bug caught before it produced a table.** The first run of the sweep crashed
on a partition dictionary keyed by triplet *name* being indexed by triplet *number*.
Worth recording only because it crashed loudly rather than silently returning a plausible
number — the failure mode this series has repeatedly had to guard against is the quiet
one.

## 2. C1 — the sweep, drift free

Cells read *forced differences / forced equalities*.

**Full pool**

| drift structure | 9 per-message bases | 3 per-triplet | 1 global |
|---|---|---|---|
| 1 global | 6 / 6 | 289 / 289 | 439 / 439 |
| T1=T2 \| T3 | 6 / 6 | 289 / 289 | 439 / 439 |
| T1=T3 \| T2 | 6 / 6 | 289 / 289 | 439 / 439 |
| T2=T3 \| T1 | 6 / 6 | 289 / 289 | 439 / 439 |
| 3 per-triplet | 6 / 6 | 289 / 289 | 439 / 439 |

**Reduced pool (E3@101 removed)**

| drift structure | 9 per-message bases | 3 per-triplet | 1 global |
|---|---|---|---|
| 1 global | 5 / 5 | 269 / 269 | 412 / 412 |
| T1=T2 \| T3 | 5 / 5 | 269 / 269 | 412 / 412 |
| T1=T3 \| T2 | 5 / 5 | 269 / 269 | 412 / 412 |
| T2=T3 \| T1 | **0 / 0** | 269 / 269 | 412 / 412 |
| 3 per-triplet | **0 / 0** | 269 / 269 | 412 / 412 |

**Cells with determination and no violation: none.** The striking regularity is that
the two columns are equal in every cell: *everything these models determine, they
determine to be zero*. Tightening the base structure (per-triplet, then global) buys
hundreds more determinations and every single one is a collision. Loosening it to
per-message leaves six, or none. There is no middle.

## 3. C2 — the axis that actually matters

With the drift **fixed** to a known constant rather than left free:

| drift | pool | symbols | forced | equalities |
|---|---|---|---|---|
| 1, 2, 3, 17, 41, 82 | full | 51 | **276** | 6 |
| 1, 2, 3, 17, 41, 82 | reduced | 50 | **256** | 5 |

Identical at every value. So the drift *value* contributes nothing — what produces the
doctrine's 276 determinations is the act of fixing it at all. And fixing it never removes
the six false equalities: they are present at every value (FR21) and in the free-drift
reading too.

That is the sharpest available statement of where the pin inventory comes from. It is
not a fact about the corpus; it is a fact about the corpus *conditioned on a parameter
the project has separately certified as unidentifiable*.

## 4. What this settles

- **FR23's negative is realised, and broadly.** Thirty configurations spanning every
  partition of the drift and base structures; none escapes the trade.
- **The trade has a shape.** More constraint on the offsets buys more determination and
  proportionally more collisions — exactly proportionally, in every cell. That is not
  the signature of a model that is nearly right and needs adjusting; it is the signature
  of a family whose determinations come from over-constraining rather than from the
  data.
- **The doctrine's inventory is doubly conditional** — on the global-drift structure
  refuted by injectivity, and on fixing the drift. Neither condition is knowledge.

What it does *not* settle is whether the additive-progressive family is wrong or whether
some constraint in the pool is. The six false equalities survive every offset structure
and every drift value, which points at the pool rather than the model; but no single
pair removal clears them (FR21) and no single class removal clears them under the
free-drift reading either.

## 5. Where this leaves the programme

Twenty-four cycles have narrowed the failure to a precise shape: **within the additive
family, determination and injectivity are mutually exclusive on this corpus.** Every
configuration either says nothing or says something false. That is a strong constraint
on what the answer can be, and it points outside the family — to a cipher whose offset
structure is not an affine function of position at all, which is where FR12's exclusion
of every two-term linear recurrence and FR13's piecewise-affine analysis were already
pointing.

The honest summary for the doctrine is that the pin inventory should be re-labelled
rather than deleted: **16 strict pins / 10 certified / 8 pin-grade, conditional on
per-message bases and a fixed global drift** — a conditioning that is now known to be
refuted by injectivity. Everything downstream of it (FR17's leverage map, FR19's
exposure figure, FR20's pair counts) inherits that label.

## 6. Horizon

(1) **Find the constraint that produces the six false equalities.** They survive every
offset structure and drift value, so they are the most model-independent defect
available — a minimal unsatisfiable core computed under the *free*-drift reading would
name it precisely, and that is a cheap computation now that the measure is O(1).
(2) **Take the exclusion seriously**: if determination and injectivity cannot coexist in
the additive family, the next family to test is one where the offset is not affine in
position — and FR13's model-free cartography already says K is arithmetic *where the
corpus can see it*, which constrains how such a model must behave. (3) Standing: #2⁻'s
instance-level audit; the 15 candidate glyphs.

## 7. Reproduction

`eyescore.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — the O(1) measure reproducing FR23's census, the free-drift collapse, the
identity of forced differences with forced equalities, the reduced pool determining
nothing, and the baseline guard. The full run reproduces the C1 sweep over both pools,
the C2 fixed-drift table and the C3 reading. Failures carry prefix
`XD-MBYG04K-URS3LF`.
