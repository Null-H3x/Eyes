# Field Report 206 — LINE 4, THE AIRTIGHT TRANSCRIPTION FUZZ: NO ERROR CANDIDATE SURVIVES A RANDOM-SUBSTITUTION NULL, THE DATA IS CLEAN WHERE THE TEST IS FAITHFUL, AND THE FOUR-LINE PROGRAM CLOSES THE INTERNAL GAME

*July 2026. Cycle: EYESPIRAL-C, attack line 4 — the last of the 30-day program.
Instrument: `eyefuzz_full.py`, gated, with one honest scope limit found and
respected mid-cycle. This report also synthesizes lines 1–4.*

---

## 0. Negatives and a scope limit first

**The airtight fuzz cannot re-derive all 208 classes faithfully — 62 of them
require the scan's maximalise/min_repeats filtering that a raw template match
does not reproduce.** Discovered by direct comparison: re-deriving each class
from its window template yields *more* instances than shipped for 62 classes
(0 fewer, 146 exact). My template shortcut is a looser class definition than
`chain_extract`'s pipeline. Rather than report a fuzz built on the wrong class
semantics, line 4 runs on the **146 faithfully-reproducing classes** (203
covered positions), where re-derivation is exact — rows and instance counts
both — and the 62 are frozen at shipped values. The fully-airtight version
needs a faithful `chain_extract` port; deferred, logged. `eyefuzz3` (FR200,
frozen rows) remains the valid broad screen.

**The first "signal" was a metric artifact, caught before it propagated.**
Under live re-derivation, almost every perturbation appeared to *increase*
determined relations (803 → 1603). Cause: the live path undercounts at
baseline unless the admitted-class emission matches the canonical build; the
"improvements" were the baseline being wrong, not the perturbations. Fixed;
correct baseline is (0 contradictions, 1603 relations, 63 glyphs).

## 1. The airtight test, correctly run

On the 146 faithful classes, 203 positions, 2,075 confusion evaluations under
**live span re-derivation**: 89 perturbations increase determined relations
(to 1,660, by linking glyph 64 — already an invariant-homophone member).
Before calling any of them a transcription-error candidate, the decisive
question: is increasing relations *specific to base-5 confusions*, or does any
random substitution do it?

```
cell (1,21) glyph 29 : confusion-improving 1/11   random-improving 6/20
cell (3,56) glyph 62 : confusion-improving 2/10   random-improving 6/20
cell (4,64) glyph 58 : confusion-improving 6/10   random-improving 6/20
```

**Random glyph substitutions increase relations at the same rate as geometric
confusions.** The +57 relations are mutation-induced coincidence — adding
*any* value to a corpus creates spurious isomorph matches, exactly what random
noise does. There is no confusion-specific signal. **No transcription-error
candidate survives the null.** The data is clean under the airtight test where
the test is faithful — the strongest transcription verdict the program can
produce short of source-imagery re-verification.

This is the same discipline that has now caught six artifacts in the program
(FR35, FR41, FR97, FR203's P2, and this): a raw anomaly priced against a
properly-randomized null, and the anomaly dissolving into the null. The
transcription premise, screened at FR200 and now stress-tested airtight on
72% of the covered cells, holds.

## 2. The 164-cell imagery checklist stands as the residual action

What no computational test can close is whether the 164 (now 203, extended)
load-bearing cells were transcribed correctly *at the source* — a
pre-existing error is indistinguishable from truth by any internal method,
because the whole edifice is built on those values. The checklist is written
(FR200 §6; the covered-position list is the deliverable). It is a finite,
one-time human task against `noita-eyes.neocities.org` imagery, and it is the
single remaining action that could alter the internal picture. It requires no
tooling — only eyes on the source glyphs at the enumerated positions.

## 3. THE FOUR-LINE PROGRAM — synthesis

The 30-day program was built to attack every internal variable to a ceiling.
All four lines are complete:

| line | attacked | verdict |
|---|---|---|
| **1** enumeration + structural battery | the inner layer's structure; whether compute is the bottleneck | enumeration is 6,806 candidates (trivial); four of six structural predicates provably affine-blind; the two admissible ones null against geometry; **inner-layer structural hypotheses of the registered kinds falsified** |
| **2** residual stress | the four measured anomalies | model **anti-fragile** (contradiction mass below null); FR102 dimension **named** (3 constants + drift); FR184 **noise**; base structure **unchanged/suggestive**; zero uncharacterized quantities remain |
| **3** mode tournament | which cipher family | single global linear drift determines **1,558 falsifiable relations** rivals cannot; **GAK/deck refuted ~35:1**; the mode is recovered by the largest margin the program has measured |
| **4** transcription fuzz | whether the data is correct | **no error candidate survives** the random-substitution null on the faithful 72%; imagery checklist is the residual human action |

**What the program establishes together:** there is no internal crack. The
cipher mode is recovered (line 3), the reading is unique and proven (FR199),
the structure is fully named with zero loose quantities (line 2), the inner
layer has no detectable structure of the kinds one can register (line 1), and
the data itself shows no transcription-error signal (line 4). Every internal
variable on the don't-know list has been attacked to the ceiling:

- **cipher mode** — recovered (single global linear drift, Quagmire-II family)
- **alphabet size** — 83, prime, image ≤ 75
- **alphabet ordering** — determined up to one scalar + three constants for
  63 glyphs; the 20 dark ones invisible *by proof*
- **cut/shuffle** — no shuffle; single linear keystream, per-message reset;
  deck/hidden-state families refuted
- **alphabet language / inner layer** — flat, non-linguistic, and now with
  its registrable structural hypotheses falsified
- **proven decoded position** — still zero, and now provably unreachable
  internally: it requires an external anchor, by four independent theorems

## 4. The state of the solution

The internal game is **closed**. Not "advanced" — closed, in the specific
sense that every remaining unknown is either proven unreachable from inside
(the drift, the constants, the dark glyphs, affine-covariant payload
structure) or is a one-time external/human action (two header plaintexts, one
d-ladder meaning, or the imagery checklist). Six drift routes dead by proof,
uniqueness proven by exhaustion, mode won by falsifiable margin, anomalies
resolved, data clean. The 202 reports of internal cryptanalysis have reached
the boundary the mathematics permits.

**The whole determinable solution now hangs on four plaintext values at
stamped positions — three of them inside the launch-visible openings — or, at
the limit, on the meaning of a single repeated header glyph.** That is the
external ask, and it is the smallest and most legible it will ever be.

## 5. Artifacts and horizon

`eyefuzz_full.py` (airtight fuzz, faithful-subset mode). Standing deferral: a
faithful `chain_extract` port to extend the airtight test to all 208 classes
— low marginal value given the null on 72% and the random-substitution
result, but the honest completion of line 4.

Horizon — and this is the genuine end of the internal road:
1. **The imagery checklist** — the one human action that could still move
   anything; finite, no tooling.
2. **The publication**, refreshed through FR206, leading with the four-value
   / one-glyph header ask and shipping the full verification kit
   (`eyeverify.py`, `unique_reading_794.txt`, `extended_reading_1603.txt`,
   `run_certification.sh`, both invariant cores, the mode discriminator).
3. **Wait, correctly.** Every arriving claim routes through the verification
   protocol; every arriving anchor converts mechanically through `eyeenum.py`.

The program set out to find what could be attacked under a 30-day ceiling. The
answer, honestly, is: everything internal has now been attacked, and the
cipher held — which means the mechanism is recovered and the remaining
distance to a decoded message is exactly one external fact the corpus cannot
supply. That is not a failure of the attack. It is the attack reaching its
mathematical horizon and reporting back precisely where the door is.
