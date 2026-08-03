# Field Report 34 — The Bridge Is Made of Dots

**Series note.** Thirty-fourth report of the EYESPIRAL series. FR33 recruited glyph 1 and
made FR5's H1 expressible, but noted the test cannot fail on its own — it needs a second,
independent drift prediction. H3 is the natural candidate and is blocked only because
glyphs 5 and 66 sit in different components. This cycle asks whether those components can
be joined from inside the corpus. Instrument `eyebridge3.py`, selftest 6/6 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** They cannot. For a same-passage cell whose glyphs lie in
different components, base(C_j) − base(C_i) = drift·z with z = (w + Δ − Δ_b + Δ_a), and
because that base difference is one fixed quantity **every bridging cell between the same
two components must give the same z**. The search finds 165 candidate alignments carrying
a cross-component cell while their same-component cells agree perfectly on w — but the
values they propose for base(C1) − base(C2) scatter across **fourteen distinct residues**,
so at most one can be right, and **every one of those bridging cells is a dot-masked
cell**: exactly the variable-interior positions FR7's sound rows remove and FR19 verified
all genuinely vary. Extending FR33's supported passage makes the point exactly: offsets 13
and 14 extend it cleanly, taking determination **350 → 384**, glyphs **54 → 56** and
exposure **72.3% → 74.1%** with injectivity still clean — and **offset 15 is the cell that
merges C1 with C2, and it violates injectivity.** The components are separated by
precisely the cells that carry no constraint. So H3 stays uncheckable, H1 stays
unfalsifiable, and the joint two-hypothesis drift test is blocked from inside the corpus.

---

## 1. What a bridge would have to satisfy

FR32 established w = base_diff/drift as a constant per *message pair*. The same algebra
applied to a cell spanning two components gives a constant per *component pair*:

  base(C_j) − base(C_i) = drift · z,  z = (w + Δ − Δ_b + Δ_a) mod 83

Every cell bridging the same two components must return the same z, whatever the message
pair, shift or position. That is a strong global condition and it is what distinguishes a
genuine bridge from an arbitrary cell.

## 2. B1 — extending the supported passage

| cells | determined | violations | components | C1+C2 merged |
|---|---|---|---|---|
| L = 13 (FR33) | 350 | 0 | 24, 10, 7, 3, … | no |
| **+ offsets 13, 14** | **384** | **0** | 25, 11, 7, 3, … | no |
| + offset 15 | 659 | **3** | 36, 7, 3, … | **yes** |
| + offsets 13–19 | 772 | **7** | 39, 7, 3, … | yes |

Cell by cell: offsets 13, 14, 16 and 19 are clean; **15, 17 and 18 violate injectivity**.
Offset 15 — E4 glyph 64 against W4 glyph 25 — is precisely the cell that would merge the
two largest components, and it is one of the violating ones.

## 3. B2 — the clean gain

Keeping only the clean extension:

| | determined | glyphs | exposure |
|---|---|---|---|
| FR33 | 350 | 54 | 72.3% |
| **FR34** | **384** | **56** | **74.1%** |

Components 25, 11, 7, 3 and five pairs; injectivity clean. Three quarters of the corpus is
now covered by glyphs whose mutual differences are determined.

## 4. B3 — why the bridge is blocked

Two independent signs, and they agree:

- **Every candidate bridging cell is dot-masked.** These are the variable-interior
  positions — the atlas encodes them as pattern dots, FR7's sound-rows repair removes them
  because full-span rows over-assert, and FR19 checked all 153 of them and found every one
  genuinely varies across its class's instances.
- **The candidates disagree with each other.** Fourteen distinct values are proposed for
  base(C1) − base(C2). A genuine bridge would produce one; arbitrary cells produce many.

That is a coherent structural explanation rather than a coincidence: the components are
separated by exactly the cells that carry no constraint. Any bridge built from them would
re-introduce the over-assertion that FR6 diagnosed, FR7 repaired and FR21 caught again
through injectivity.

## 5. B4 — consequence for the drift

- **H1** — q[1] − q[47] = 51·drift, so H1's predicted 4 selects drift **31**. As FR33
  said, this cannot fail, so it is not support.
- **H3** — q[5] − q[66] remains **not determined**, so H3 cannot be evaluated.

The joint test — two hypotheses either agreeing on one drift (a 1-in-83 coincidence worth
taking seriously) or disagreeing (falsifying at least one) — is therefore **blocked from
inside the corpus**. It needs an external anchor, which is the same conclusion FR31
reached by a different route and which this cycle now reaches for the drift specifically.

## 6. Where the model stands

- **384 determined relations over 56 glyphs**, components 25/11/7/3 plus five pairs,
  injectivity clean, **74.1%** of corpus positions exposed.
- **Everything remains a multiple of the drift** (FR30). The architecture is known; its
  scale is not, and no internal route to fixing it survives.
- **Both openings** must be read as stamped material (FR29, FR33).
- **Ten components** → two external anchors in the largest plus one each elsewhere, with
  FR27's packing tail making the last redundant.

## 7. Horizon

(1) **Re-run FR32's free-w scan on the widened skeleton.** With 56 determined glyphs
instead of 47, every window pair carries more informative cells, so the search that found
the FR32 passage should be strictly more sensitive — and a passage that bridges two
components *without* using a dot cell is the one thing that would unblock the drift test.
(2) **The message pairs with no forced w** — W2's, and the cross-triplet pairs — remain
unscanned because the method needs a known w; treating w as free and looking for shifts
where many cells agree on some value is the natural extension. (3) Standing: #2⁻'s
instance-level audit; two external anchors in component 1.

## 8. Reproduction

`eyebridge3.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
6-check gate — FR33's skeleton reproduced exactly, offsets 13–14 extending cleanly, offset
15 identified as the bridging cell, that cell shown to violate injectivity, H1's
coefficient confirmed invertible (the reason its test cannot fail), and the baseline
guard. The full run reproduces B1–B4. Failures carry prefix `XD-MBYG04K-URS3LF`.
