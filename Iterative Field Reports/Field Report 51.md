# Field Report 51 — Redundancy Is Not Waste

**Series note.** Fifty-first report of the EYESPIRAL series. FR49's sensitivity map found
the strict tier costs zero relations when withdrawn and described those pairs as "doing no
work." This cycle finds that framing wrong. Instrument `eyestrict.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The eighteen strict pairs come from `iso_relax`'s own scan of
the corpus; the thirteen classes were **inherited** from the atlas. They are two different
procedures identifying repeated structure, so asking whether one implies the other is not a
question about redundancy but about **agreement**. Building with the atlas classes alone
and then classifying every row the strict pairs emit: **158 rows, 158 redundant, zero
pivots, zero contradictions.** The atlas implies every constraint the strict tier asserts,
without exception. The converse fails — under a strict-only system 185 atlas rows remain
pivots — so the atlas is strictly stronger and the implication runs one way. **FR49
measured the strict tier's marginal contribution correctly and described its role wrongly:
this is method-level corroboration of the inherited atlas, not waste.** The caveat bounds
it: both derive from the same 1,036 glyphs, so this is agreement between procedures rather
than data-level independence. What it rules out is the atlas being an artefact of one
person's scanning choices.

---

## 1. S1–S2 — the test

| source | pairs | origin |
|---|---|---|
| atlas classes (repaired) | 49 | inherited |
| strict tier | 18 | `iso_relax`'s own scan |

Classifying every strict-pair row against an atlas-only system:

| verdict | count |
|---|---|
| **redundant** | **158** |
| pivot | **0** |
| contradiction | **0** |

Every one of the eighteen pairs is fully implied, row for row. There is no partial
agreement anywhere — no pair contributing a single new constraint, and none conflicting.

## 2. S3 — the implication is one-way

Under a strict-only system, the atlas rows come out **161 redundant, 185 pivots**. The
atlas is strictly stronger: it implies the strict tier and is not implied by it. That is
what a marginal contribution of zero means structurally.

## 3. S4 — where the strict pairs sit

All eighteen involve only **West 1 and East 2**, at positions 38–45 and 68–80 — the T1
refrain region that the #M, #1, #C0 and #C1 classes already describe. The independent scan
re-found the corpus's most conspicuous repeated passage and nothing else, which is exactly
what a scan tuned for exact isomorphy should do.

## 4. S5 — the correction

FR49's figure was right and its wording was not. A marginal contribution of zero can mean
two very different things: evidence that adds nothing because it is vacuous, or evidence
that adds nothing because **something else already establishes it**. The strict tier is the
second kind.

Two procedures read the same corpus and produced constraints agreeing on all 158 rows with
zero conflicts. Had the inherited atlas contained a fabricated or mis-transcribed class,
the independent scan would have had no reason to agree with it — and the gate checks that
the test can detect disagreement, by confirming a fabricated pair does *not* come out fully
redundant.

**The caveat, stated rather than buried:** both sources derive from the same 1,036 glyphs.
This is agreement between *methods*, not independent data. It does not confirm that the
atlas's classes are same-plaintext; it confirms that they are not an artefact of one
scanning choice.

## 5. What the doctrine should carry

Replace "the strict tier is fully redundant, doing no work" with:

> The strict tier is fully implied by the atlas classes — 158 of 158 rows redundant, no
> pivots, no contradictions — which is an independent scan corroborating the inherited
> atlas rather than surplus evidence.

Model unchanged: 384 relations over 56 glyphs, components 25/11/7/3 plus five pairs,
injectivity clean, 74.1% exposure, repair A the unique maximal reading, drift unpinned.

## 6. Horizon

(1) **Two external anchors in component 1** remain the only route to the drift.
(2) **The success criterion** is unchanged as the most consequential open item.
(3) The two load-bearing pieces are now both audited (FR48, FR50) and the atlas itself is
corroborated by an independent scan (here) — the internal evidence base is as examined as
it can be made without new data.

## 7. Reproduction

`eyestrict.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — the pool split, the atlas implying every strict row, the converse failing, a
fabricated pair failing to come out redundant (so the test can detect disagreement), and
the baseline guard. The full run reproduces S1–S5. Failures carry prefix
`XD-MBYG04K-URS3LF`.
