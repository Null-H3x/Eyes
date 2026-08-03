# Field Report 124 — REPAIR C AUDITED: IT HOLDS, AND IT IS NOT A RIVAL TO REPAIR A

*Seven-audit validation of FR122/FR123. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Why audit

FR122 and FR123 introduced repair C and a 686-position unique structure in two
cycles, fast, under a workflow that had just been retuned toward production.
That is precisely the condition under which this series has previously shipped
errors (FR97, FR103, FR107, FR110, FR113). The claims were checked before being
built on further.

---

## 1. The seven audits

**A1 — does repair C build cleanly at every drift?**
```
drifts where build fails      : none (0 of 82)
distinct relation counts      : {409}
distinct forced-equality sets : {(36,68)}
distinct component partitions : 1   sizes [26,11,7,3,2,2,2,2,2] = 57 glyphs
```
**PASS.** The partition is drift-stable, which the uniqueness claim requires.

**A2 — is the structure unique across ALL 82 drifts, not the 9 sampled?**
```
distinct position counts    : {686}
distinct position SETS      : 1
distinct equality signatures: 1
```
**PASS.** FR123 sampled nine drifts; all eighty-two agree.

**A3 — is East 3@101 really the sole T1 bridge?**
```
atlas classes spanning T1 and another triplet : #M- only
  its non-T1 instances                        : East 3@101 only
pool pairs straddling T1 / non-T1             : 6, ALL involving East 3@101
strict-tier straddling pairs                  : 0
FR32/33 passage                               : East 4 x West 4, both T3
```
**PASS.** The T1 bridge rests entirely on one instance.

**A4 — do repair A and repair C agree where they overlap?**

Repair C forces a single drift, i.e. ratio 1 — which is also one of repair A's
seventeen. If both are sound they must agree.
```
repair A positions 461 · repair C positions 686 · common 461
equality structures on all 461 common positions AGREE : True
```
**PASS, and it reframes the result** — see §2.

**A5 — is the visible E1~W1 shared passage real or a rendering artifact?**
```
East 1 vs West 1 identical CIPHERTEXT positions: 44 of 99
longest identical runs: 1-24 (24), 37-49 (13), 29-32 (4)
```
**PASS.** The near-duplicate is in the raw ciphertext; identical plaintext
structure there is expected, not an artifact of how I rendered it.

**A6 — is the West 1 internal repeat real?**
```
West 1@40..47 : [47,44,48,42,19,48,13,47]   pattern A.B..B.A
West 1@70..77 : [68,46,17,36,13,17,21,68]   pattern A.B..B.A
identical: False   isomorphic: True
```
**PASS.** They are isomorphs, not identical ciphertext — exactly as a shared
passage under a progressive shift should look. FR123's phrasing ("a passage
repeating inside West 1") was loose: the *plaintext* repeats, the ciphertext
does not.

**A7 — what is the homophone being accepted?**
```
q[36] = q[68]
glyph 36 = East 2's INDICATOR (position 0), undetermined under repair A
glyph 68 = component 1, determined under repair A
frequencies: glyph 36 -> 9,  glyph 68 -> 14
```
**Noted, not a failure.** Repair C asserts East 2's message-indicator shares a
plaintext value with glyph 68.

---

## 2. The reframing A4 forces

**Repair C is not a rival to repair A. It is repair A committed to ratio 1,
plus the T1 bridge.**

- repair C's 686 positions are a **strict superset** of repair A's 461
- the equality structures **agree exactly** on all 461
- repair C adds **225 positions** and changes nothing that was already there

So the choice is not between two incompatible readings. It is:

> **Accept one homophone (`q[36] = q[68]`) and you get ratio 1 forced plus 225
> extra positions. Refuse it and you keep strict bijectivity plus a 17-way
> ratio ambiguity.**

FR123 called them "alternatives, not refinements." **That was wrong** — C
extends A rather than competing with it, on the branch where A picks ratio 1.

---

## 3. Corrections to FR122 and FR123

| claim | status |
|---|---|
| repair C: 409 relations, 57 glyphs, 1 equality | **confirmed at all 82 drifts** |
| structure unique | **confirmed exhaustively** (FR123 sampled 9) |
| East 3@101 the sole T1 bridge | **confirmed** across atlas, pool, strict tier, passage |
| 686 positions / 66.2% | **confirmed** |
| "repair A and C are alternatives, not refinements" | **WRONG** — C strictly extends A at ratio 1 |
| "a passage repeating inside West 1" | **loose** — the plaintext repeats; the ciphertext is isomorphic, not identical |
| word-power 6.3% → 8.4% | confirmed; and FR121's projected 5× was over-promised, as FR123 already recorded |

---

## 4. What is still assumed, unchanged by this audit

The audit validates **internal consistency**, not correctness. Repair C still
rests on:

- **East 1@68 is spurious** — supported by arithmetic weight (five of six
  forced equalities against East 3@101's one) but not proven. FR110 removed
  the embeddedness argument entirely.
- **`C` is not strictly bijective** — one homophone. This gives up the
  17-ratio narrowing, since every one of those 65 rejections was an injectivity
  failure and none a linear contradiction.
- **The progressive form** — FR118's rival, plaintext autokey, is untouched by
  any of this.

A recovered drift ≠ 1 refutes repair C.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Repair C | proposed (FR122), built (FR123) | **audited, 7/7** |
| Repair A vs C | "alternatives" | **C extends A at ratio 1** — superset, agreeing structures |
| Uniqueness | 9 drifts sampled | **all 82 verified** |
| Sole-bridge claim | atlas-level | **verified at pool, strict-tier and passage level** |
| The homophone | unexamined | `q[36] = q[68]`; glyph 36 is East 2's indicator |

---

## 6. Model status

**Repair A**: 384 relations, 56 glyphs, 17 ratios, 44.5% linked, bijective.
**Repair C**: 409 relations, 57 glyphs, drift forced to ratio 1, 66.2% linked,
one homophone — a strict extension of repair A's ratio-1 branch. Both
conditional on the progressive form. Cumulative: 27.16 billion candidates, zero
survivors.

---

## 7. Horizon

1. **Re-run the vocabulary batch against the repair-C structure** — one target,
   T1 testable, decisive hits. Unchanged from FR123 and now safe to build on.
2. **The 17-ratio question is now a straight trade** and should be stated as
   one in the acquisition spec: bijectivity buys the narrowing, the homophone
   buys the coverage, and an acquired anchor decides which was right.
3. **Nothing further is owed on repair C's validation.** Seven audits, all
   passing, one wrong characterisation corrected.
