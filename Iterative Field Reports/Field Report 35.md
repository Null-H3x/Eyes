# Field Report 35 — What Injectivity Does Not License

**Series note.** Thirty-fifth report of the EYESPIRAL series. FR34 left two searches
unrun: the message pairs the w-method could not reach, and a re-scan on the widened
skeleton. This cycle runs both, finds no bridge, and catches an unsound extension method
that would have inflated the published skeleton by 118 relations. Instrument
`eyefree2.py`, selftest 6/6 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The free-w scan — treating the message-pair constant as
unknown, which is the only way to reach West 2's pairs and the cross-triplet pairs —
returns 16 alignments against a shuffle background of 1–3. **Fifteen are within-triplet
and already known.** The single cross-triplet candidate, West 3 / East 4 at shift −32,
prices at ~4 × 10⁻⁵ for 5 of 14 cells and is **not significant** against that background.
**West 2 produces nothing at any shift against any message**, which matches its status
throughout the series as the uncoupled one. No bridge is found, so the drift test stays
blocked. The constructive result is that the widened skeleton makes FR32's passage far
better attested than when it was found: **fourteen consecutive cells now agree on w = 54**
where FR32 had five, with the first disagreement at offset 21 — chance 83⁻¹³ for a fixed
value. And the cycle's most important content is a **self-correction**: extending that
passage by greedily adding any cell that does not trip the injectivity rail reaches
offsets 22, 30 and 31 — far past where the passage's own evidence stops — and inflates
the skeleton from 384 relations to 502, exposure 74.1% to 78.5%. **Injectivity is a
necessary condition, not evidence that a cell is same-passage.** The greedy figures are
rejected; the principled rule returns FR34's 384 / 56 / 74.1%, and the 118-relation gap
between them is the size of the error I nearly published.

---

## 1. The correction, first

Having a supported passage, the tempting move is to extend it by adding whichever cells
the injectivity rail accepts. I did that, got 502 relations over 60 glyphs and 78.5%
exposure, and had it drafted before checking *where* the added cells were. They were at
offsets 16, 19, 22, 30 and 31 — while the passage's own w-agreement stops at offset 14
and the first outright disagreement is at 21. Offsets 22, 30 and 31 are not in the
passage at all.

This is the same error the series has caught three times in other guises: FR6's
full-span rows, FR7's dot cells, FR21's certified collisions. **A cell that fails to
produce a contradiction has not thereby been shown to belong.** The rail is a filter on
what may be admitted, never a reason to admit. The correct rule is to bound the passage
by its own evidence first, and only then remove cells that violate injectivity — which
returns exactly FR34's numbers.

The selftest now encodes this as a negative gate: the greedy method must be shown to
reach past the supported span.

## 2. F1 — the free-w scan

| | result |
|---|---|
| alignments with ≥5 agreeing cells | **16** |
| unigram-preserving shuffles | 3, 1 |
| within-triplet | 15 |
| **cross-triplet** | **1** |
| **involving West 2** | **0** |

Free w is a weaker test than FR32's fixed-w version — it calibrates at 83⁻⁽ᵏ⁻¹⁾ rather
than 83⁻ᵏ — so the shuffle background is no longer zero, and the bar has to be read
against it.

The one cross-triplet candidate, **West 3 / East 4 at shift −32**, has 5 agreeing cells of
14, chance ~4 × 10⁻⁵ per alignment. Against a background that already produces 1–3 hits
per shuffled corpus, that is **not significant** and is not claimed.

**West 2 produces no alignment at any shift against any message.** That is a clean
negative and it converges with everything else the series has found about W2: FR9 found
it permissive with every offset merge, FR29 and FR32 found no forced base difference
involving it, and now no shared passage either. W2 is not merely weakly coupled; on
present evidence it is uncoupled.

## 3. F2 — the passage, better attested

| | FR32 (47-glyph skeleton) | FR35 (56-glyph skeleton) |
|---|---|---|
| cells agreeing on w = 54 | 5 | **14** |
| span | offsets 0–12 | offsets **0–14** |
| first disagreement | — | offset 21 |

Fourteen consecutive informative cells agreeing on one specific value is chance 83⁻¹³.
The passage found in FR32 at 3.6 × 10⁻⁶ is now attested well beyond any reasonable doubt
— not because new evidence arrived, but because the widened skeleton makes more of its
cells readable. That is a satisfying consistency: the skeleton the passage helped build
now confirms the passage.

## 4. F3 — the two extension rules compared

| rule | offsets used | relations | glyphs | exposure |
|---|---|---|---|---|
| greedy by injectivity | 0–14, 16, 19, 22, 30, 31 | 502 | 60 | 78.5% |
| **principled (supported span)** | **0–14 minus 4** | **384** | **56** | **74.1%** |

The 118-relation, 4.3-point gap is the measure of what injectivity alone would have
licensed without evidence.

## 5. Where this leaves the programme

- **Determined skeleton: 384 relations over 56 glyphs**, components 25/11/7/3 plus five
  pairs, injectivity clean, 74.1% of corpus positions exposed. Unchanged from FR34, now
  with its one new passage far more strongly attested.
- **No bridge exists** between components 1 and 2 — FR34 showed every candidate cell is a
  dot, and this cycle's broader search finds no alternative anywhere, including in the
  regions the w-method had never reached.
- **The drift remains unpinnable internally.** H1 selects drift 31 but cannot fail; H3
  stays uncheckable; the joint test needs an external anchor.
- **West 2 is uncoupled** on every measure the series has applied.

Internal routes are now exhausted along three independent lines: FR31 (skeleton cannot
bootstrap past its own reach), FR34 (bridges are made of dots), FR35 (nothing left in the
unscanned pairs).

## 6. Horizon

(1) **#2⁻'s instance-level audit** is the last standing structural item from FR15 and now
the only unexecuted internal task. (2) **The acquisition target is unchanged and fully
specified**: two external anchors inside component 1, which fix rotation and drift
together and determine 25 glyphs; then one anchor per remaining component, with FR27's
packing tail making the last redundant. (3) Should an anchor ever arrive, H1 becomes a
genuine test immediately — it predicts drift 31, and an independently pinned drift either
confirms or refutes it.

## 7. Reproduction

`eyefree2.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
6-check gate — FR34's skeleton reproduced, the free-w scan recovering the known passage,
the shuffle background bounded, the passage's supported span mapped to a contiguous head
ending at offset 14, the **negative gate** showing greedy-by-injectivity reaches past that
span, and the baseline guard. The full run reproduces F1–F3. Failures carry prefix
`XD-MBYG04K-URS3LF`.
