# Field Report 201 — THE SCAN THRESHOLD WAS THE WALL: NINE NEW CLASSES CERTIFIED, THE FRAGMENTS COLLAPSE FIVE-TO-THREE, EXPOSURE BREAKS 79.1%, AND TWO OF THE "INVISIBLE" GLYPHS COME INTO VIEW

*July 2026. Cycle: EYESPIRAL-C, executing FR200 horizon 2 (A2-full/A3 merged).
Instruments: `eyespan.py` (208/208 span recovery), `eyescan3.py` (certifier,
gates green after one control-forced redesign). This is the first exposure
gain since FR178 and the first reach into the 22 since FR135 declared them
invisible.*

---

## 0. Negatives and corrections first

**The first certifier failed its own fabricated control (7/150 false
admits) — and the failure was the finding.** `eyescan2` counted a row as
"implied" even when it re-derived a constraint through cell-pairs the
certified system already contains; a fabrication that scrambled only
two-glyph rows sailed through on inherited confirmations. Fix, enabled by
the span recovery: **implied counts only at NEW cell-pairs**, and the
control is geometry-preserving (same length, letter template, instance
count, messages; random positions — the FR41/FR42 doctrine). Rebuilt
certifier: plant admitted, **0/150** false admits, then **0/540** across
sixty replicates of each admitted shape.

**`eyespan` v1's contiguity assumption was wrong** (692 pairs located
nowhere): class rows use letter cells only — skeleton-repeat positions, the
FR7 sound-rows doctrine applied corpus-wide. Recovered convention:
letters = in-window repeated skeleton positions.

**The exhaustion theorem does not extend to the raw candidate universe.**
Over all 427 raw classes (208 + 219 scan candidates), 79 joint conflicts
appear among individually-pool-consistent survivors. Properly rescoped:
uniqueness-by-exhaustion is a property of the **certified** universe (§4).
The conflicting candidates are uncertified chance structure — FR151's kin
at the relaxed threshold; characterization against shuffle nulls queued.

## 1. Keystone: every class now has provenance

The 208 shipped classes' spans were recovered by fingerprinting their row
multisets against regenerated scans and gating on **exact multiset
identity** — the match is its own round-trip proof. Result: **208/208**,
across window lengths 7–59, including a stratum at `min_repeats = 1` the
main scan largely skipped. `spans_208.json` ships; A2-full (live class
re-derivation under perturbation) is now literally executable.

## 2. The sweep and the admissions

Grid L ∈ 6–59, single-repeat windows admitted. **219 candidates beyond the
208.** Certifier verdicts: 121 contradict the certified system, 42 fully
redundant, 47 insufficient evidence, **9 ADMITTED** — each with 0
contradictions, ≥ 4 out-of-sample hits at new cell-pairs (one with 8), and
novel content. Pricing: per-shape false-admit < 1/540 measured; expected
chance admissions over 219 candidates ≪ 1; joint coherence (below) is
itself further evidence no chance class survives.

## 3. Forensics — what the nine actually do

All four independent new constraints come from class #0 (L=14, 14
instances), each bridging through **glyph 29 at West 1 position 21**:

```
W1@21 <-> W2@56   W1@21 <-> E3@64   W1@21 <-> W3@65   W1@21 <-> E4@35
```

Glyph 29 is a **T1 header-stamp glyph** (it sits at offsets 7 and 21 of all
three T1 openings) — undetermined for 200 reports precisely because the
pool excluded opening pairs. Precedent audit: the shipped 208 already carry
**250 letter cells (7.0%) inside opening regions**, so opening cells as
cipher-conformant constraint sources are established practice, not a new
assumption; and the four bridges passed three independent 1/83 consistency
checks among themselves before classes #1–8 added ~650 further rows, **all
consistent**, largely at newly-determined cells — a silent out-of-sample
confirmation mass an order beyond the admission bar.

**System deltas, every prior invariant preserved:**

| | certified (FR197) | extended (this report) |
|---|---|---|
| relations / glyphs / equalities | 794 / 61 / 8 | **1603 / 63 / 20** |
| certified 794 inside, values identical | — | **yes, all** |
| invariant homophones 22=64, 36=68 | hold | **hold** (36/68 gains partner 23) |
| components (glyphs) | [37, 16, 4, 2, 2] | **[57, 4, 2]** |
| fragment positions | 491 / 222 / 48 / 29 / 29 | **771 / 48 / 29** |
| corpus exposure | 819 = 79.1% | **848 = 81.9%** |
| undetermined glyphs | 22 | **20** (29 and 43 determined) |

The equality count moves from 8 to 20 — from conspicuously *below* FR164's
calibrated control band (11–53) to inside it; the deficit was partly the
scan threshold's blind spot. The twelve new equalities close into coherent
triples ({19,35,63}, {37,57,66}, 23 joining {36,68}) — transitive closure
holding is a consistency property, not an assumption.

## 4. The theorem, rescoped and extended

Over the **certified universe** — the 208 curated classes plus the 9
admitted here — the exhaustion argument holds exactly as in FR199: 50
classes are individually pool-inconsistent (barred from every consistent
superset), and the **167 survivors are jointly consistent**, so every
maximal set equals pool + 167. Unique, proven. Over the raw 427-universe it
does not hold and should not: 79 conflicts among uncertified candidates is
what chance structure is supposed to do, and the certification bar exists
precisely to define the universe the theorem quantifies over.

## 5. Acquisition arithmetic, transformed

Three fragments, not five. The full programme is **four pins** (2 + 1 + 1),
not six. **Two indicator values now unlock 771 positions — 74.4% of the
corpus — in one step** (all five determined indicators sit in the merged
giant). The 8-token East 3 crib retains its self-verifying role and now
also lands in the giant. CURRENT_STATE / ACQUISITION_SPEC / the community
post need a v2.1 pass with these numbers; the asks themselves are unchanged
in kind, doubled in yield.

## 6. Artifacts

`eyespan.py`, `spans_208.json` (provenance for every class),
`eyescan3.py` (gated certifier), `scan3_admitted.json` (the nine, with
spans), `extended_reading_1603.txt` (sha `7b4132e8…`; supersets the
certified object, which remains the conservative floor alongside both
invariant cores).

## 7. Horizon

1. **A2-full proper**: re-run the transcription fuzz with live class
   re-derivation from spans — the airtight version FR200 scoped.
2. **Characterize the 121** contradicting candidates against
   geometry-preserving nulls (expected: chance, the FR151 pattern).
3. **Scale corroboration** (optional, Threadripper): regenerate the
   mandatory problem file with 217 classes and re-run `eyemax` — expected
   1 distinct, matching sha `7b4132e8…`.
4. **Doctrine v2.1** and the publication update with the new arithmetic —
   two symbols now buy three-quarters of the corpus.
5. The residual dark set is 20 glyphs / 188 positions; the sweep that found
   these nine is not exhausted — L > 59 and richer letter templates remain
   unswept, and the certifier is now proven against its controls.
