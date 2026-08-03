# Field Report 46 — The Model, Rebuilt From Scratch

**Series note.** Forty-sixth report of the EYESPIRAL series. After a run of cycles in
which results were corrected (FR32, FR33, FR35) and one was overturned outright (FR41,
withdrawn in FR42), this cycle rebuilds the entire model in a single pass from the raw
corpus and checks every published figure against it. Instrument `eyeaudit.py`, gate 11/11
green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The model has been assembled across forty-five reports by a
succession of instruments, each verifying its own numbers in the cycle that produced them.
None of it had ever been rebuilt end-to-end from the corpus with every step applied in
order — which, after this many corrections, is a test it could genuinely have failed. It
does not. **Every published figure reproduces exactly**: baseline guard 22/19/16, sound
pool 83 pairs, repair A leaving 67, the FR32/33 passage at 14 cells with offset 4 excluded
as variable interior, the E4/E5 merge admissible, **384 determined relations, zero
injectivity violations, 56 glyphs, components 25/11/7/3 plus five pairs, 768/1036 = 74.1%
exposure**, the gauge ladder at 0/0/82, and both openings still contradicting. The second
half of the cycle exhibits what all of that actually *is*: the Δ tables. Inside a
component q[s] = base_C + drift·Δ_s, with the Δ values fixed by the corpus and base_C and
the drift not. That turns the success-criterion question into arithmetic — two anchors in
component 1 determine **25 glyphs and 31.2% of positions**, ten anchors determine
**56 glyphs and 74.1%**, and the output is **768 plaintext values in 0…82**, which the
plaintext measurements say is a token stream rather than a reading.

---

## 1. A1 — the reproduction

| step | result | published |
|---|---|---|
| baseline guard (iso_relax) | (22, 19, 16) | ✓ |
| sound pool (atlas + strict) | 83 pairs | ✓ |
| repair A (drop E3@101, E1@68) | 83 → 67 pairs | ✓ |
| FR32/33 passage | 14 cells, offset 4 excluded | ✓ |
| E4/E5 merge (FR14 body runs) | admissible | ✓ |
| **determined relations** | **384** | ✓ |
| **injectivity violations** | **0** | ✓ |
| **glyphs in components** | **56** | ✓ |
| **component sizes** | **25, 11, 7, 3, 2, 2, 2, 2, 2** | ✓ |
| **corpus exposure** | **768/1036 = 74.1%** | ✓ |
| gauge ladder (1 / 3 / 9 gauges) | 0/82, 0/82, 82/82 | ✓ |
| + T1 openings / + T3 openings | 0/82, 0/82 | ✓ |

Eleven checks, all passing. The model reproduces from the raw corpus in one pass.

## 2. A2 — the deliverable

Inside a component, q[s] = base_C + drift·Δ_s. The Δ values are fixed by the corpus; base_C
and the drift are not. These tables *are* the result of forty-six cycles.

**Component 1 — 25 glyphs, 323 positions (31.2%)**

| glyph | 0 | 1 | 5 | 6 | 7 | 9 | 10 | 17 | 20 | 27 | 30 | 34 | 41 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Δ | 0 | 3 | 7 | 34 | 36 | 58 | 55 | 29 | 39 | 1 | 66 | 61 | 69 |

| glyph | 45 | 47 | 48 | 50 | 57 | 62 | 63 | 64 | 68 | 71 | 79 | 81 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Δ | 60 | 35 | 82 | 8 | 33 | 28 | 31 | 81 | 65 | 38 | 57 | 54 |

**Component 2 — 11 glyphs, 179 positions (17.3%):** 13:0, 19:53, 23:4, 25:82, 44:1, 46:31,
49:52, 60:81, 66:55, 72:35, 78:25

**Component 3 — 7 glyphs, 104 positions (10.0%):** 16:0, 21:58, 26:1, 40:57, 42:35, 67:31,
73:2

**Component 4 — 3 glyphs, 29 positions (2.8%):** 4:0, 35:55, 37:57

Plus five two-glyph components. Every pairwise difference within a component is fixed;
nothing across components is.

## 3. A3 — what anchors would buy

| anchors | determines | corpus |
|---|---|---|
| **2** (both in component 1) | 25 glyphs | **31.2%** |
| 10 (one per remaining component) | 56 glyphs | **74.1%** |

The first two are the decisive ones: one fixes base_C1, the second supplies a known
pair-difference, and a pair-difference is bijective in the drift (FR26), so it pins the
drift for the *whole* system at once. Every later anchor then costs only one component.
FR27's packing tail makes the tenth redundant — nine anchors leave 44 enumerable
completions.

## 4. A4 — what they would not buy

The output is **768 plaintext values in 0…82**. FR36 excluded small contiguous alphabets,
FR39 excluded small scattered ones, and FR40 validated the instrument behind both. The
effective inventory exceeds roughly 60, so those values are not letters of a small
alphabet, and the remaining 268 positions cannot be filled by context.

**Recovering C yields a token stream, not a reading.** That is the success-criterion
question stated in concrete numbers, and it is a question about the project's goal rather
than about the corpus. Nothing measurable bears on it.

## 5. What the audit does and does not certify

**Does.** That the published model is internally reproducible: every figure the series
carries follows from the corpus, the atlas, and the stated repairs, with no drift between
what was reported and what the code now produces.

**Does not.** That the repairs are correct. The model remains conditional on repair A —
the assertion that E1@68's three-pair skeleton match is spurious — and on the
stamped-header reading, which FR45 established cannot be independently tested. Those
conditions are unchanged by a reproduction audit, which checks bookkeeping rather than
premises.

## 6. Horizon

(1) **Two external anchors in component 1** remain the only route to the drift, and the
audit makes their value exact: 25 glyphs and 31.2% of the corpus from the first two alone.
(2) **The success criterion** is unchanged as the most consequential open item, and A4
states it in numbers rather than in principle. (3) Should the stamped-header reading ever
be abandoned, H1 revives and FR33's widening needs revisiting — recorded so that the
condition is not lost.

## 7. Reproduction

`eyeaudit.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` *is* the
audit — eleven checks rebuilding the model from the corpus and comparing each published
figure. The full run prints the reproduction table, the Δ tables, and the anchor
arithmetic. Failures carry prefix `XD-MBYG04K-URS3LF`.
