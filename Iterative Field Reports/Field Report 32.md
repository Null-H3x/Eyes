# Field Report 32 — What w Depends On

**Series note.** Thirty-second report of the EYESPIRAL series. FR31 left a pre-registered
commitment, so it runs first. Discharging it exposes that my own registration was
mis-specified, and repairing the test yields a correction to FR29 and a much better
calibrated instrument. Instrument `eyepair.py`, selftest 6/6 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The algebra behind FR31's scan says more than FR31 used. For a
same-passage cell between two messages at shift Δ with both glyphs in one component,
**w = (Δ_{c₂} − Δ_{c₁} − Δ) = base_diff / drift**, which depends *only on the message
pair* — not on the shift, not on the position. FR31 asked whether a window's cells agree
among themselves; the sharper question is whether they agree with the value that pair's
certified alignments already fix, which is one hypothesis per cell and calibrates at 83⁻ᵏ
rather than 83⁻⁽ᵏ⁻¹⁾. That reframing produces three results. **First, a correction to
FR29:** it reported two forced base differences, computed *without* the E4/E5 merge that
FR14 forces from literal body runs and FR26 showed the repaired pool accepts. With the
merge, **seven** are forced — and they reproduce the corpus's near-duplicate structure
exactly, from constraints alone: within T1, E1 = W1 with E2 displaced by 77; within T3,
E4 = E5 with W4 displaced by 54. **Second**, the rescan finds 14 alignments against 0 on
shuffles, with agreement appearing as *localized runs* rather than global — the signature
of shared passages inside otherwise different messages. **Third**, FR31's lead is
discharged: my registered test (does it survive window lengthening?) was **mis-specified**,
because every finite passage breaks once the window runs past its end — the certified
control breaks too. Tested properly, the lead's five informative cells all equal the
established w = 54, a *specific* value, at chance 3.6 × 10⁻⁶ across all E4/W4 window
pairs. Upgraded from watch-grade to supported.

---

## 1. Corrections first

**My own pre-registration was flawed.** FR31 registered: "a genuine passage should survive
lengthening, an alignment artefact will not." Run, the lead holds to L = 20 and breaks at
L = 25 — but so does the certified control W1@38 × E2@43, which is a genuine length-13
passage. Passage length is a confound I did not anticipate when registering, and the test
as written cannot separate "artefact" from "short." Registering a test does not make it
sound; this one had to be replaced rather than merely run.

**A correction to FR29.** It reported two forced base differences and I carried that into
the model summary. FR29 computed them without the E4/E5 offset merge — evidence-forced by
FR14's literal body runs (three runs of length 3, chance 2.4 × 10⁻⁶ each, against an
empirical null of zero among all 27 cross-triplet pairs) and admissible under repair A per
FR26. It belongs in the licensed model. With it included, seven are forced.

## 2. P1 — the offset structure, corrected

| | without the merge (FR29) | with the merge |
|---|---|---|
| forced base differences | 2 | **7** |

The seven:

| relation | value |
|---|---|
| base[W1] − base[E1] | **0** |
| base[E2] − base[E1] | 77 |
| base[E2] − base[W1] | 77 |
| base[E5] − base[E4] | **0** |
| base[W4] − base[E4] | 54 |
| base[E5] − base[W4] | 29 |
| base[W3] − base[E3] | 54 |

Read as structure: **within T1, E1 and W1 share an offset and E2 sits 77 away; within T3,
E4 and E5 share an offset and W4 sits 54 away.** That is precisely the near-duplicate
structure the doctrine records from agreement statistics — T1's near-dup pair is E1/W1
with E2 odd, T3's is E4/E5 with W4 odd — recovered here from constraint algebra alone,
with no appeal to agreement rates. Two independent routes to the same architecture.

T2 remains the weakly-coupled triplet: only E3/W3 is fixed, and W2 floats.

## 3. P2 — the rescan

Testing each cell against its message pair's established w:

| pair | shift | informative | agreeing | longest run |
|---|---|---|---|---|
| E4 / E5 | +1 | 23 | 17 | 7 |
| E4 / W4 | +3 | 23 | 15 | 7 |
| W1 / E2 | +5 | 22 | 13 | **13** |
| W4 / E5 | −1 | 18 | 13 | 11 |
| E1 / E2 | +5 | 15 | 10 | 10 |
| W1 / E2 | −25, +10, +40 | 16–19 | 10 | 9–10 |
| E4 / W4 | +2 | 7 | 6 | 6 |
| **E4 / W4** | **+1** | 13 | **5** | 5 |

Fourteen alignments in total; **zero on unigram-preserving shuffles.** The agreement
appears as *localized runs* — at E4/W4 shift +1, only 5 of 13 informative cells agree, and
those 5 are consecutive. That is what a shared passage embedded in otherwise different
text looks like, and it is a more convincing signature than global agreement would be.

The multiple E4/W4 shifts (+1, +2, +3) read naturally as one near-duplicate relationship
with indels, different regions aligning at different offsets.

## 4. P3 — the lead, discharged

Tested properly — do the cells hit the *specific* established value?

| quantity | value |
|---|---|
| informative cells at E4@28 × W4@29 | 5 |
| equal to the established w = 54 | **5** |
| chance for 5 cells to hit a specific value | 83⁻⁵ = 2.5 × 10⁻¹⁰ |
| E4/W4 window pairs available | 14,280 |
| expected by chance | **3.6 × 10⁻⁶** |

**Upgraded from watch-grade to supported.** The lead is corroborated by the *value* it
produces, not merely by internal agreement — and that value was fixed independently by two
other E4/W4 alignments. The caveat stands: it was found by a scan I designed after seeing
the corpus, so it deserves confirmation from a source that did not.

## 5. What this adds

- **The offset architecture of T1 and T3 is now fully determined** (up to the drift
  scalar), and it matches the near-duplicate structure derived by completely different
  means.
- **The scan is properly calibrated** — one hypothesis per cell against an
  independently-fixed value, with a clean shuffle null.
- **A new same-passage region is supported**, the first the series has added since the
  atlas was inherited.

None of this loosens the drift. Every value here is a multiple of it (FR30), so the
architecture is known and its scale is not.

## 6. Horizon

(1) **Feed the new alignment into the pool** and re-derive: a supported same-passage
region is exactly the kind of constraint that could widen the components, which FR31
showed is otherwise closed. Whether it recruits any of the eight unknown glyphs in its
span is directly checkable. (2) **Extend the rescan to message pairs whose w is not yet
fixed** — W2's pairs, and the cross-triplet pairs — by treating w as a free parameter and
looking for shifts where many cells agree on *some* value. (3) Standing: #2⁻'s
instance-level audit; the acquisition target of two external anchors in component 1.

## 7. Reproduction

`eyepair.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
6-check gate — the w identity proved on synthetic data with everything known (constant
across a shared passage, and equal to base_diff/drift), forced-base recovery on a plant
with equal within-triplet offsets, FR29's count reproduced without the merge, the licensed
model forcing more, and the baseline guard. The full run reproduces P1's corrected table,
P2's scan with shuffles, and P3's discharge of the registered lead. Failures carry prefix
`XD-MBYG04K-URS3LF`.
