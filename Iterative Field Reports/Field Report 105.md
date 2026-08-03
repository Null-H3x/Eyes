# Field Report 105 — THE SEVENTEEN ARE UNSTRUCTURED, AND THE AMBIGUITY IS TOTAL BUT SHAPE-PRESERVING

*Instrument: `eyeratio.py` (6/6 gate, canonical machinery). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. Verify, do not inherit

E6 withdrew FR103's "77 of 82": that scan ran on a pool rebuilt from
`corpus.json` + `atlas.json`, which relates 64 skeleton pairs against the
model's 384 relations and never touches five skeleton glyphs. The FR104 cycle,
on restored canonical machinery, reported **17**. Before anything is built on
that number it has to be reproduced independently — inheriting a figure is how
the FR52 and E6 propagation errors happened.

**Standing guard (E6) satisfied first:** `eyeaudit.py` runs 11/11 in this
environment — sound pool 83, repair A → 67, 384 relations, 0 violations, 56
glyphs, components [25, 11, 7, 3, 2, 2, 2, 2, 2], exposure 74.1%.

---

## 1. A precondition FR104 did not state, now checked

The two-drift parameterisation puts the drift where `eyegauge.make_rows` puts
it — once per pool pair, `rhs = d_group * (p2 - p1)`. **That row form is only
valid if no pool pair straddles T1 and T2/T3.** For a straddling pair the
right-hand side would acquire an `i`-dependence (FR104 §0's ramp), and a
constant `rhs` would be silently wrong.

```
t3_no_T1_straddle    PASS    0 straddling pairs of 67 (must be 0)
```

Zero. The parameterisation is exact, not approximate — and this is now a gate
rather than an assumption. Also recorded: **49 of the 67 repaired pool pairs
are T1-internal**, so the `d1` group carries most of the evidence.

**R1 satisfied:** at `d1 = d2 = 1` the rebuild returns 384 relations, 0
violations, 56 glyphs, components [25, 11, 7, 3, 2, 2, 2, 2, 2] — the canonical
model exactly.

---

## 2. Reproduction: 17, and the same 17

```
contradictory                    :  0
consistent but injectivity fails : 65
CLEAN                            : 17

survivors: 1, 8, 9, 15, 22, 28, 35, 40, 48, 51, 53, 55, 74, 76, 77, 78, 82
```

Identical to FR104's list, element for element. **R3 satisfied; the figure
stands on two independent builds.** Ratio 1 is present, as R2 required.

---

## 3. NEW — the seventeen have no arithmetic structure

FR104's horizon item 1 asked whether the survivors share a property that would
constrain them further. Tested exhaustively:

| test | result |
|---|---|
| closed under negation `r → −r` | **no** (8 of 17 overlap) |
| closed under inversion `r → r⁻¹` | **no** (2 of 17) |
| closed under squaring | **no** (2 of 17) |
| closed under multiplication | **no** |
| quadratic residues among them | **8 of 17** — chance is 8.5 |
| multiplicative orders | {1: ×1, 2: ×1, 41: ×7, 82: ×8} — spread across every subgroup |
| consecutive gaps | 7, 1, 6, 7, 6, 7, 5, 8, 3, 2, 2, 19, 2, 1, 1, 4 — irregular |

The set is not a subgroup, not a coset, not closed under any natural operation,
and its quadratic-residue split is *exactly* chance. The eight elements that do
pair under negation — {1, 82}, {9, 74}, {28, 55}, {35, 48} — are four pairs
among seventeen, which is what negation-closure by chance looks like.

> **The enumeration cannot be reduced by arithmetic. Seventeen stands as a
> count, not as a structure.** FR104's horizon item 1 is closed, negatively.

---

## 4. NEW — the ambiguity is total in values, invariant in shape

FR104 established component structure is ratio-invariant. Measured here in both
directions, which is sharper:

**Invariant:** component *membership* is **identical** across all seventeen
ratios — same glyphs, same grouping, same partition — and the relation count is
384 at every one.

**Not invariant:** the Δ *values* differ at **every** ratio, in **every** one of
the nine components. Seventeen distinct Δ tables per component. Comparing
ratio 1 against ratio 8 on component 1: they agree on **3 of 25** Δ values.

**And the tables are not scalings of one another.** The elementwise multiplier
from the ratio-1 table to the ratio-8 table takes twenty distinct values across
component 1's twenty-five glyphs. The mechanism is FR102's mixed provenance:
each component draws relations from both drift groups, so changing `d1`
rescales *part* of each table and leaves the rest fixed — a non-uniform
transformation, not a global scalar.

> **The seventeen are seventeen genuinely different readings of the corpus,
> sharing a common structure.** FR54's per-component anchor *yield* is
> unaffected — the partition never moves — but the recovered *values* are not
> determined until the ratio is.

---

## 5. What this means under the settled criterion

The objective (FR101) is to solve the unknown variables and pin the mechanism.
Stated against that:

- **Mechanism:** progressive keystream, linear, no periodic component (FR56/91),
  no global polynomial or exponential bend (FR102), **two scale parameters**
  whose ratio is confined to seventeen values. That is a nearly complete
  mechanical description; what remains unpinned is numeric, not structural.
- **Variables:** `d2` (scale), `d1/d2` (17-way), 35 bases, and `C` over 56
  glyphs. The FR54 programme delivers the bases and the component structure;
  it does **not** deliver the ratio.
- **Cost of the residue:** one anchor whose evidence sits in T1 and one whose
  evidence sits in T2/T3 collapse the seventeen to one. Failing that,
  acquisition yields seventeen candidate alphabets — enumerable by hand, and
  distinguishable by any single further pin.

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Surviving drift ratios | 17 (FR104, one build) | **17, reproduced independently**; identical list |
| Two-drift row form | used | **precondition gated**: 0 of 67 pool pairs straddle T1, so the form is exact |
| Structure of the 17 | open (FR104 horizon 1) | **no arithmetic structure** — not a subgroup/coset, QR split at chance; count is irreducible |
| Component membership under ratio | "ratio-invariant" | **identical partition** at all 17; relation count 384 at all 17 |
| Δ values under ratio | unexamined | **17 distinct tables per component**; ratio 1 vs 8 agree on 3 of 25 in component 1 |
| Relation between the 17 readings | assumed scalar | **not a global scaling** — 20 distinct elementwise multipliers; mixed provenance is the cause |
| Evidence split | unquantified | **49 of 67** repaired pool pairs are T1-internal |

---

## 7. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; components
[25, 11, 7, 3, 2, 2, 2, 2, 2] — **invariant across all surviving ratios**.
Alphabet [56, 83], floor 56. **Drift: two parameters; ratio confined to 17
values with no further arithmetic reduction available.** Cumulative: 27.16
billion candidates, zero survivors.

---

## 8. Horizon

1. **Re-run FR54's anchor ordering on canonical machinery under two drifts.**
   This cycle proves the partition is ratio-invariant, so the ordering *should*
   survive intact — but FR54's numbers were derived under one drift and the
   inference is not the check. Internally executable, and it is the last piece
   of the acquisition pricing.
2. **Identify which anchors are cross-group.** The seventeen collapse on one
   T1-sourced plus one T2/T3-sourced pin. Which glyphs qualify is computable
   from pool-pair provenance and would tell an acquirer exactly which two
   targets matter most — a sharper statement than FR54's component ordering
   alone.
3. **Do not attempt further arithmetic reduction of the seventeen.** Section 3
   tested the natural operations and found chance. A further constraint must
   come from evidence, not from number theory.
