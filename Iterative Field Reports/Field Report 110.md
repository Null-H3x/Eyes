# Field Report 110 — EMBEDDEDNESS IS ATLAS NESTING: REPAIR A HAS NO SURVIVING SUPPORT

*Instrument: `eyeembed.py` (5/5 gate). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. The confound was pre-empted, and it fired

FR109 reopened the repair fork and left one candidate standing in favour of
repair A: FR27's **embeddedness asymmetry**, valued because it is
drift-independent and therefore untouched by the gauge contamination that
collapsed FR47 and FR48.

CHALLENGE II identified the confound before measurement (R1, pre-registered):
if a short class's pattern is a **sub-pattern of a longer class's pattern at the
implied offset**, then every long instance contains a short instance *by
construction*. Such containment is an artefact of atlas nesting and says nothing
about whether any individual instance is genuine. Only **incidental**
containment — where the child asserts an equality the parent does not — can be
evidence.

**Census over all 43 certified instances:**

```
STRUCTURAL parent relations : 43
INCIDENTAL parent relations :  0
```

**Every containment in the atlas is structural. Not one is incidental.**

---

## 1. The asymmetry, seen properly

The two candidates:

| | parents | classification |
|---|---|---|
| **East 1@68** (repair A discards) | none | — |
| **East 4@51** (repair B discards) | `#3+@51` | **STRUCTURAL** |

And the reason is visible on inspection:

```
#3  (L=12) = AB.C....B.AC
#3+ (L=15) = AB.C....B.AC..B      <- #3 is a literal PREFIX of #3+
```

`#3+@51` contains `#3@51` because `#3+`'s pattern *begins with* `#3`'s pattern.
The containment is automatic at the same start position and would hold whether
the instance were genuine or spurious.

> **So FR27's asymmetry is between "no parent" and "a parent that carries no
> information."** Neither state is evidence. **[R2] No likelihood ratio is
> reported, because embeddedness has no discriminating power to price.**

FR2 recorded the same observation descriptively ("the motif's only parentless
occurrence") and FR27 promoted it to evidence. It was never more than the
descriptive remark.

---

## 2. Consequence — the fork is genuinely open

Tracking what has happened to every argument that favoured repair A:

| argument | source | status |
|---|---|---|
| Injectivity refutes repair B | FR47 | **gauge-contaminated** — holds at ratio 1 only (FR109) |
| Likelihood ratio ~2.8e5 | FR48 | **collapsed** — its dominant term was the passage incompatibility, void at B's clean ratios (FR109) |
| Embeddedness asymmetry | FR2, FR27 | **dead** — atlas nesting, 0 of 43 containments incidental (this cycle) |
| Minimal cores all contain East 3@101 | FR25 | **does not discriminate** — East 3@101 is dropped by *both* repairs |
| Ratio 1 admits only repair A | FR109 | **conditional** on drift equality, itself unsupported (FR102) |

> **Repair A has no surviving discriminating evidence.**

It is not refuted — it remains injectivity-clean at 17 ratios against repair B's
5, and it determines one more glyph (56 against 55). But **"best supported" is
no longer an accurate description; "conventional" is.** The 384-relation model,
the nine components, the 74.1% exposure and the acquisition specification all
rest on a choice that is currently unsupported rather than merely conditional.

**The conservative option remains available and should be named.** The
both-dropped reading AB — discard East 3@101, East 1@68 *and* East 4@51 — is
injectivity-clean at 27 ratios with 259 relations over 55 glyphs. FR47 correctly
called it a strict weakening of A: it asserts strictly less and contradicts
nothing. Anyone wanting maximum caution can adopt it at a cost of 125 relations.

---

## 3. What could still discriminate

Neither internal argument survives, so the discriminator must be new. Two
candidates, in order of executability:

**(a) Out-of-sample cross-validation.** FR37 and FR38 tested repair A's model
predictively — leave-one-pair-out gave 59/59 with dot masking, and whole-class
removal gave 41/41 across all thirteen classes, against a 1.5% chance rate and a
planted-spurious control scoring 0/23. **Repair B's model has never been put
through that test.** If B predicts held-out evidence materially worse, that
discriminates on grounds independent of both injectivity and embeddedness. This
is internally executable and is the obvious next cycle.

**(b) Acquisition itself.** The two readings share only four clean ratios —
`{8, 9, 22, 40}`. Repair A is additionally clean at `{1, 15, 28, 35, 48, 51, 53,
55, 74, 76, 77, 78, 82}` and repair B additionally at `{7}`. So a recovered
ratio adjudicates the fork **unless** it lands in the four-way overlap. The
anchor programme therefore carries a fork-resolution payload it was not designed
for, and §7 item 4 of the acquisition spec — verifying the ratio lies in the
valid set — should be widened to record *which* repair's set it lands in.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **FR27 embeddedness** | soft evidence for repair A | **dead** — 0 of 43 containments incidental |
| **Repair A** | best-supported reading | **conventional, unsupported** — not refuted, not preferred |
| FR2's "only parentless occurrence" | structural anomaly | a descriptive remark; never evidence |
| Atlas containment | treated as informative | **artefact of pattern nesting**; `#3` is a literal prefix of `#3+` |
| Conservative fallback | noted FR47 | **AB reading**: 259 relations, 55 glyphs, clean at 27 ratios |
| Fork resolution | internal | requires cross-validation (untested for B) or acquisition |

---

## 5. Model status

Standing reading (repair A, by convention rather than support): 384 relations
over 56 glyphs; injectivity clean at 17 ratios; exposure 74.1%; components
(25, 11, 7, 3, 2, 2, 2, 2, 2). Live alternatives: **repair B** (393 relations,
55 glyphs, 5 ratios) and **AB** (259 relations, 55 glyphs, 27 ratios).
Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **Run FR37/FR38's cross-validation on repair B.** The only internal test that
   has never been applied to the alternative reading, and the only remaining
   route to adjudicating the fork without external evidence. If B scores
   materially worse out-of-sample, the fork closes on sound grounds; if it
   scores comparably, the fork is closed to internal analysis and only
   acquisition can settle it.
2. **Widen the acquisition spec's ratio check** to record which repair's clean
   set the recovered ratio falls in. Cheap, and it turns the anchor programme
   into a fork test at no cost.
3. **Continue the gauge audit.** Two of three targets examined so far have
   broken (FR109's repair, this cycle's embeddedness by a related mechanism).
   The remaining candidates — FR27's packing residual curve, the gauge ladder,
   FR21's injectivity census — have not been checked.
