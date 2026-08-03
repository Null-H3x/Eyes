# Field Report 59 — SEPARABLE ALPHABETS EXCLUDED ACROSS THE WHOLE FRAME GROUP, AND A FALSIFIABLE PREDICTION ABOUT THE PICTURES

*Instrument: `eyesep` (6/6 selftests, one rank failure caught before corpus contact). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the family FR58 could not reach

FR58 swept 432 frames because **affine structure is frame-dependent**: testing
`q[g] = a·g + b` asks whether the value is affine in `g`'s trigram label, and
relabeling changes the question. That sweep closed the algebraic families across
every frame the corpus permits.

But there is a family it could not reach, and which nobody has tested:

```
q[g] = F(d₂) + G(d₁) + H(d₀)      — each visual feature contributes independently
```

This is the natural construction if the value is read off the picture
feature-by-feature, and it has three properties that make it the right target:

1. **It strictly contains affine** (`F(a)=25am`, `G(b)=5bm`, `H(c)=cm`), so it is a
   weaker, more permissive hypothesis than anything FR28 or FR58 excluded.
2. **It is frame-INVARIANT.** Permuting digit positions or state labels merely
   permutes `F`, `G`, `H`. So a single test settles it for FR58's 432-frame
   stabiliser *and* the full 10,368,000-element group at once — a strictly larger
   scope than FR58 achieved, at a fraction of the cost.
3. **It is drift-free**, for FR58's reason: within a component
   `q[g₂]−q[g₁] = drift·(Δ₂−Δ₁)`, and absorbing the drift into `F,G,H` removes it.

379 equations against 12 effective unknowns. Wildly overdetermined, so the test is
decisive either way.

---

## 1. Gate — one failure, and it found a structural fact

`S2` asserted rank 12 (15 unknowns minus 3 gauge constants) and returned **11**.
The reason is not a bug:

**`d₂ = 4` is structurally impossible.** Trigrams with a leading digit of 4 label
100–124, above the corpus ceiling of 82. So `F(4)` appears in no equation and the
null space is 3 gauge constants **+ 1 vacuous variable**.

Consequence, small but new: **the most significant visual feature has only four
usable states, not five.** The glyph construction is `4 × 5 × 5 = 100` reachable
labels of which 83 are used, not `5³ = 125` of which 83 are used. That is a tighter
box than the doctrine has been carrying, and it yields a prediction (§4).

Remaining gate: planted separable alphabet consistent; affine consistent (subset
check); random alphabet rejected with 310 contradictions; a **single** planted
violation detected; null pass rate **0/200**.

---

## 2. Results — all four families excluded

| family | vars | rank | eqns | contradictions | verdict |
|---|---:|---:|---:|---:|---|
| fully separable `F+G+H` | 14 | 11 | 379 | **313** | EXCLUDED |
| MSB separable `F(d₂)+K(d₁,d₀)` | 27 | 25 | 379 | **141** | EXCLUDED |
| LSB separable `K(d₂,d₁)+H(d₀)` | 22 | 20 | 379 | **188** | EXCLUDED |
| mid separable `K(d₂,d₀)+G(d₁)` | 23 | 21 | 379 | **185** | EXCLUDED |
| arbitrary `C` *(positive control)* | 46 | 42 | 379 | **0** | FITS |

The positive control matters: an arbitrary alphabet fits with **zero**
contradictions, which confirms the Δ tables are internally consistent and that the
exclusions above are properties of the *families*, not of my data.

The three partial families are worth more than the full one. Each asks only that
**one** visual feature contribute independently while the other two are free to
interact arbitrarily — a much weaker claim, with 20–25 effective parameters against
379 equations. All three fail.

---

## 3. SELF-CORRECTION — three results I nearly published

Run per-component, the fully separable family **fits** components 2, 3 and 4 and
fails only component 1. I had "3 of 4 components are separable" drafted before
running the power audit.

| component | glyphs | random alphabet fits | |
|---|---:|---:|---|
| 1 | 25 | **0 / 300** | informative |
| 2 | 11 | **300 / 300** | **VACUOUS — cannot fail** |
| 3 | 7 | **300 / 300** | **VACUOUS — cannot fail** |
| 4 | 3 | **300 / 300** | **VACUOUS — cannot fail** |
| pooled | 46 | 0 / 300 | informative |

Components 2–4 have as many free parameters as glyphs, so separability fits
*anything* there. Those are not fits; they are the absence of a test. Only
component 1 and the pooled system carry information, and both exclude.

Sixth instance of this error family in the series (FR23 injectivity-by-asserting-
nothing, FR49 two vacuous selftests, FR55 a vacuous pre-registration branch, and
now this). The guard is unchanged and still not automatic: **ask what the test
returns if the hypothesis is false, and check the answer differs.**

---

## 4. A FALSIFIABLE PREDICTION ABOUT THE GLYPH PICTURES

§1 gives something the series has not had: a claim checkable from the **glyphs
themselves**, with no binary and no cryptanalysis.

> If the labels are base-5 trigrams enumerated over indices 0…82, then across all
> 83 glyphs the most significant visual feature must exhibit **exactly four
> distinct states**, while the other two features exhibit five.

If someone counts five distinct states in the MSB feature, the base-5 trigram
reading is wrong at the foundation — and FG3's standing caveat that "83 is
reading-dependent, not a fact" becomes the live problem rather than a footnote.
If four, the reading is corroborated from a direction entirely independent of the
ciphertext.

This is the cheapest falsification test currently available in the project, it
requires only the glyph inventory, and it is symmetric — informative whichever way
it lands.

---

## 5. What this buys

**`eyeforward` hiding place #2 narrows again, and on wider scope than FR58.** FR58
closed algebraic construction across the 432 permitted frames. FR59 closes
digit-separable construction across the **entire** frame group, because
separability is frame-invariant. Together:

> `C` is not built by any rule in which the visual features contribute
> independently, nor by any simple algebraic rule, in any labeling frame.

What survives in that hiding place is construction where all three features
interact irreducibly — which is a much less natural thing for a person to build by
hand, and correspondingly less likely, though untested and probably untestable
without a specific candidate.

---

## 6. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 768/1036 = 74.1%; repair A the unique maximal reading; drift
unpinned with H4 the only surviving hypothesis.

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Digit-separable `C` | never tested | **EXCLUDED**, all four variants, across the whole frame group |
| Scope of algebraic exclusions | 432 permitted frames (FR58) | separability closed on **all 10,368,000** via frame-invariance |
| MSB state count | assumed 5, as base-5 | **4** — `d₂=4` exceeds the label ceiling; box is 4×5×5=100, not 125 |
| eyeforward hiding place #2 | closed for algebraic (FR58) | **also closed for separable**; only irreducible 3-feature interaction survives |
| Per-component separability | — | vacuous for components 2–4; only component 1 tests anything |

---

## 8. Horizon

1. **Count the MSB states on the glyph pictures (§4).** No binary, no compute, and
   it either corroborates or falsifies the reading the last two cycles are built
   on. It is now the cheapest open question in the project and it outranks the
   radix trace on cost.

2. **Settle the radix** (`GHIDRA.md` base-7 vs corpus base-5). Still load-bearing
   for FR58 and FR59 both, still a fact in an invariant binary.

3. **Remaining hiding places for `C`:** a PRNG under an untested *family* (extend
   families, not seeds), irreducible 3-feature construction, a non-alphabet source,
   and unstructured `C` — which only anchors reach.

4. **Standing, unchanged:** two external anchors in component 1 (FR54 ordering);
   and the success criterion, which FR57 made decidable and which remains undecided.
