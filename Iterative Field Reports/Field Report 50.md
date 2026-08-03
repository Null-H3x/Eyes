# Field Report 50 — The Second Load-Bearing Piece

**Series note.** Fiftieth report of the EYESPIRAL series. FR49's sensitivity map showed the
model rests on exactly two pieces of evidence and named the one that had never been
audited. Instrument `eyeclass2.py`, selftest 7/7 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** Class #2 carries 159 of the model's 384 relations, second only
to the FR32/33 passage, and had never been examined individually the way FR15 examined the
cross-triplet bridges. **It audits clean and strong.** Its skeleton carries **five**
equal-pairs over a 30-glyph span, giving a chance of 83⁻⁵ per window and about
**2 × 10⁻⁷ across the 775 windows the corpus offers**; corpus-wide the pattern matches
**exactly its own three instances and nothing else**; and 2000 unigram-preserving shuffled
corpora produce **zero** matches. No instance weakens the class. One observation is worth
recording rather than glossing: **East 5 @ 69 is standalone** — it sits inside no larger
certified passage, which is precisely the property FR27 used against E1@68. The two cases
are not comparable, and the reason is skeleton weight: #M carries three equal-pairs, giving
about 0.0017 expected chance matches corpus-wide, while #2 carries five, giving 2 × 10⁻⁷.
A standalone instance of a class this heavy is unremarkable; a standalone instance of a
class as light as #M is the anomaly FR27 identified.

---

## 1. Corrections first

**A calibration check I got wrong twice.** I first asserted that a two-pair sub-skeleton
would match more often than the full five-pair one; it matches exactly as often (3 versus
3), because two well-separated pairs over a 30-glyph window are already highly
restrictive — worth knowing in itself. I then set a threshold of 5× on a one-pair
skeleton and it gave 10 versus 3. The meaningful assertion, now in the gate, is that a
one-pair skeleton matches at the **chance rate**: 10 observed against 9.3 expected. That
demonstrates the matcher is calibrated, which is what the check was for.

## 2. Q1–Q3 — the audit

| property | value |
|---|---|
| length | 30 |
| pattern | `AB...C...C......D.A...E...EB.D` |
| skeleton equal-pairs | **5** — offsets (0,18), (1,27), (5,9), (16,29), (22,26) |
| instances | East 4 @ 68, West 4 @ 71, East 5 @ 69 — all in T3 |
| chance per window | 83⁻⁵ = 2.5 × 10⁻¹⁰ |
| windows corpus-wide | 775 |
| **expected chance matches** | **2.0 × 10⁻⁷** |
| **actual matches** | **East 4: 1, West 4: 1, East 5: 1** |
| **matches in 2000 shuffled corpora** | **0** |

The pattern matches its own three instances and nothing else anywhere in the corpus. That
is the cleanest result of any class audit in the series.

## 3. Q4–Q5 — the standalone instance

| instance | parent passages |
|---|---|
| East 4 @ 68 | inside #2+@68 |
| West 4 @ 71 | inside #2+@71 |
| **East 5 @ 69** | **STANDALONE** |

FR27 used exactly this property to favour repair A: E1@68 is the only instance in #M or #3
with no parent passage, and that asymmetry made it the natural candidate to discard. So a
standalone instance here deserves a straight answer rather than silence.

The two situations differ by four orders of magnitude in skeleton weight:

| class | k | expected chance matches corpus-wide |
|---|---|---|
| #M | 3 | 0.0017 |
| **#2** | **5** | **2 × 10⁻⁷** |

Standalone-ness is only evidence against an instance when the class it belongs to is light
enough that a chance match is plausible. For #M at roughly one in six hundred, a
parentless instance is the one place a coincidence could hide. For #2 at 2 × 10⁻⁷, it
cannot. **The comparison turns on skeleton weight, not on standalone-ness by itself** —
and that distinction is worth carrying, because it is the kind of surface similarity that
invites a false parallel.

## 4. Where this leaves the model

Both load-bearing pieces are now audited:

| piece | relations held up | support |
|---|---|---|
| FR32/33 passage | 161 | 3.6 × 10⁻⁶ (FR48, five held-out cells) |
| **class #2** | **159** | **2 × 10⁻⁷ (here, zero in 2000 shuffles)** |

Class #2 is the better-supported of the two by more than an order of magnitude. The
model's concentrated dependency, which FR49 made explicit, rests on evidence that has now
been examined directly rather than inherited.

Model unchanged: 384 relations over 56 glyphs, components 25/11/7/3 plus five pairs,
injectivity clean, 74.1% exposure, repair A the unique maximal reading, drift unpinned.

## 5. Horizon

(1) **Two external anchors in component 1** remain the only route to the drift.
(2) **The strict tier's redundancy** (FR49: zero relations lost) is worth understanding
rather than merely noting — if the strict pairs are implied by the atlas classes, that is
two independent sources agreeing, which is corroboration rather than waste.
(3) The success criterion is unchanged as the most consequential open item.

## 6. Reproduction

`eyeclass2.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
7-check gate — the five-pair skeleton over length 30, every instance satisfying it, the
pattern matching exactly its own instances, a one-pair skeleton matching at the chance rate
(calibration), shuffles producing nothing, no instance weakening the class, and the
baseline guard. The full run reproduces Q1–Q6. Failures carry prefix
`XD-MBYG04K-URS3LF`.
