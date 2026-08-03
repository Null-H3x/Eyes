# Field Report 21 — The Constraint Nobody Checked

**Series note.** Twenty-first report of the iterative series. The last several cycles
established that the constraint system is capped, that offsets cannot grow it, and that
external anchors are the only lever. This cycle asks a different question — what
information exists *outside* the linear machinery — and finds that the one obvious
answer refutes the certified pool. Instrument `eyeperm.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR7 noted in passing that "GF systems carry no injectivity."
Every instrument since has worked inside a linear system over GF(83) in which the
alphabet map q is simply a vector of 83 unknowns — but **C is a mixed alphabet, hence a
permutation, hence q is injective**, and q[a] = q[b] is impossible for distinct glyphs.
That constraint is non-linear, the machinery discards it, and in nineteen cycles nobody
checked it. Checking it: **the certified domain of the sound pool forces q[46] = q[4],
and the difference is gauge-invariant across every shift, so it is certified rather than
incidental.** FR7 saw this collision, labelled the pair "collision-tainted", excluded
both from pin grade and treated it as benign degeneracy. It is not benign — it is a
proof that the pool asserts something false. The result holds under direct Gaussian
elimination (no consensus heuristic), at **all 82 drifts**, and survives every
single-pair removal. It localises sharply: dropping class **#M** clears it, and within
#M dropping the single instance **East 1 @ 68** clears it. That instance is the one FR2
identified nineteen cycles ago as the motif's *solo* occurrence — the only one with no
parent passage — and the one FR6's four-cycle contradiction ran through before FR7's
sound-rows repair healed the linear symptom. What the repair did not fix, the
non-linear check now exposes.

---

## 1. The gap, and why it went unnoticed

Every constraint this series has built is linear over GF(83): rows of the form
q[D] − q[A] − (base terms) = rhs. In that world q is an unconstrained vector, and two
glyphs receiving the same value is merely a degenerate solution — unattractive, but not
false. FR7 recorded exactly this when it found glyphs 4 and 46 sharing a certified
value: it called them "collision-tainted", removed them from pin grade, and moved on.
Every subsequent report inherited that framing, including my own repeated quoting of
"10 certified / 8 pin-grade, tainted {4, 46}."

But the cipher model says C is a **mixed alphabet** — a permutation of the 83 symbols.
Then q = C⁻¹ is injective and q[4] = q[46] cannot happen. The linear machinery cannot
represent that fact, so it never fired. The tainting was not a wart on an otherwise
sound inventory; it was the inventory telling us it was wrong, in the only language the
solver had available.

## 2. The finding, established soundly

| check | result |
|---|---|
| certified domain | {4:0, 12:50, 13:2, 19:55, 23:39, 37:82, 44:53, 46:0, 49:4, 72:37} |
| certified glyphs sharing a value | **(4, 46)** |
| is q[46] − q[4] = 0 gauge-invariant? | **yes** — identical across shifts 0, 7, 31 |
| oracle | direct Gaussian elimination, no consensus purification (FR9's lesson) |
| drift dependence | violation present at **all 82 non-degenerate drifts** |
| single-pair removals that clear it | **0** — carried by multiple redundant paths |

The minimal core is 10 pairs, verified minimal at runtime, drawn from classes #2⁻, #3,
#M, #M⁻ and the strict tier, chaining across all three triplets. So the false assertion
is not local to one pair; it is a property of how the pool coheres.

## 3. Localisation

Single-class removal clears the violation for exactly one class: **#M**, the XYZ-motif
class FR2 discovered. Within #M, dropping instances one at a time:

| instance dropped | violation |
|---|---|
| East 1 @ 40 | still present |
| **East 1 @ 68** | **CLEAN** |
| West 1 @ 40 | still present |
| West 1 @ 70 | still present |
| East 2 @ 45 | still present |
| East 2 @ 80 | still present |

One instance, and it is a familiar one. FR2 catalogued the XYZ-motif as embedded at
fixed offsets inside #1/#C1 and #F — "plus one solo occurrence at E1@68 with no parent
passage." FR6's four-cycle contradiction ran through {E1@40, E1@68, W1@40, W1@70}, and
FR7's sound-rows repair made the class linearly consistent again. Three independent
lines — a structural anomaly noticed in FR2, a linear contradiction in FR6, and a
non-linear contradiction here — converge on the same window.

## 4. What this does not settle

The honest limit of the result. The minimal repair is to reject E1@68 as an instance of
#M, but that instance is **not comfortably dismissed**: #M's pattern `A.B.CB.AC` carries
three skeleton equal-pairs, so a chance match prices at 83⁻³ per window and about
**0.0017 expected chance matches across the corpus** — roughly one in six hundred. By
the standard FR15 used to retire #M⁻'s bridge (p ≈ 0.10, unremarkable), E1@68 does not
qualify as coincidence.

So the contradiction indicts something, and which premise it indicts is open:

- **E1@68 is not the same passage** despite matching a three-pair skeleton — expensive
  on the pattern evidence, but it is the minimal repair.
- **Some other pool constraint is wrong**, and #M is merely where the inconsistency
  surfaces; the minimal core spans four classes plus the strict tier, so this is
  plausible.
- **The model is wrong** in a way that makes the linear rows misstate the relation —
  the same suspicion FR9–FR16 kept circling.

What is *not* open is that the pool as it stands is false. That much is now proved by a
constraint the cipher's own definition supplies.

## 5. Consequences for the doctrine

**The certified inventory needs re-grading, again.** FR7 regraded it once, from the
strict reading's 22/19/16 to the sound tier's 10 certified / 8 pin-grade. This cycle
shows the sound tier's 10 is itself unsound: two of the ten are in a certified relation
that cannot hold. Whatever survives a repair will be smaller than 10.

**Injectivity should be a standing rail.** Every future pool, tier or repair should be
checked against it before anything is certified — it costs one pass over the certified
domain and it caught something nineteen cycles of linear work could not. That is the
transferable methodological lesson: when a model supplies a non-linear constraint, an
all-linear toolchain will happily produce solutions that violate it and report them as
certified.

## 6. Horizon

(1) **Find the repair.** The minimal single-instance fix is E1@68, but the minimal
*class-level* fix may differ; enumerating small subsets whose removal restores
injectivity — and pricing each on independent evidence, as FR15 did for #M⁻'s bridge —
is the next concrete step. (2) **Re-run the certification chain under the repaired
pool** and re-derive the pin inventory; FR17's anchor leverage map and FR20's pair
counts are both computed against the current pool and will move. (3) **Apply injectivity
retroactively** to the configurations of FR14–FR16, particularly FR16's coherent
configuration, which was never checked against it. (4) Standing: #2⁻'s instance-level
audit, the 15 candidate glyphs.

## 7. Reproduction

`eyeperm.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — sound system construction, the injectivity detector firing on the
certified equality, gauge-invariance of that equality, the detector clearing when the
implicated class is removed (so it is not stuck-on), and the baseline guard. The full
run reproduces C1's certified domain and violation, C2's drift sweep, C3's verified
minimal core and C4's localisation with the chance pricing. Failures carry prefix
`XD-MBYG04K-URS3LF`.
