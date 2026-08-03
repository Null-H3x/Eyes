# Field Report 15 — Two Bridges, One Coincidence

**Series note.** Fifteenth report of the iterative series. FR14 reduced the trilemma
to two live branches and showed both turn on the same two objects — the cross-triplet
isomorph classes #2⁻ and #M⁻. This cycle audits them directly. Instrument
`eyebridge2.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** The two bridges are not comparable pieces of evidence, and
that asymmetry resolves the cheapest version of branch (ii). Each cross-triplet class
is a within-triplet **core** of several instances plus a single **bridging instance**
in another triplet — and only the bridge asserts that a passage recurs across
triplets. Both bridges live in East 3. **#2⁻'s bridge is solid:** its L=25 pattern
carries three skeleton equal-pairs, matches nothing anywhere in the corpus except its
own four instances, and prices at p ≈ 0.006 after correcting for every candidate
message searched. **#M⁻'s bridge is a coincidence-grade match:** its L=8 pattern
`A.B..B.A` carries only **two** equal-pairs, so the expected number of chance matches
across the windows searched outside its core triplet is **0.098** — and the shuffle
null agrees, giving p ≈ 0.096 corrected. A one-in-ten coincidence is not evidence.
And the removal is maximally surgical: dropping **just that one window**, keeping all
six core instances of #M⁻ and the whole of #2⁻, turns the body-internal system from
degenerate to live. Branch (ii) therefore has a concrete, cheap and specific form —
*E3@101 is not a genuine instance of #M⁻* — at the price of FR3's drift(T1) = drift(T2)
link, which rested entirely on that window.

---

## 1. Corrections and framing first

**FR10's null answered a different question than the one that matters.** It showed
that long isomorphs never arise in unigram-preserving shuffles (53 observed at L=12,
zero in thirty shuffles), and FR14 leaned on that to call branch (ii) expensive. But
that null prices *whole classes*, and a cross-triplet class is not one claim. Its core
— six instances of a refrain inside T1, say — can be entirely real while the single
window in another triplet is a chance pattern match riding on it. Only the bridge
carries the cross-triplet assertion, and only the bridge is load-bearing for the
contradiction. Pricing the bridge conditional on the core being real is a far weaker
requirement, and it changes the answer.

**No pins gained.** This cycle audits two objects and prices a branch.

## 2. C1 — the two bridges are not alike

| class | L | pattern | skeleton pairs k | chance/window | core | bridge | expected chance matches |
|---|---|---|---|---|---|---|---|
| #2⁻ | 25 | `A...A......B.....C...C..B` | **3** | 1.75 × 10⁻⁶ | T3 (3 inst.) | East 3 @ 64 | **0.001** |
| #M⁻ | 8 | `A.B..B.A` | **2** | 1.45 × 10⁻⁴ | T1 (6 inst.) | East 3 @ 101 | **0.098** |

The evidence weight of an isomorph class is the number of equal-pairs its skeleton
forces, because that is what a random window has to reproduce. #2⁻ demands three over
a 25-long span; #M⁻ demands two over eight. Across the 674 windows searched outside
#M⁻'s core triplet, roughly one chance match is expected every ten corpora.

Both bridges being in East 3 is worth flagging: E3 is the message FR3 already found
anomalous, sharing its opening more deeply with T3 than with its own triplet.

## 3. C2 — the surgical test

| configuration | verdict |
|---|---|
| full pool + E4/E5 offset equality | **DEGENERATE** (FR14's body-internal contradiction) |
| #2⁻ bridge removed, core kept | LIVE |
| #2⁻ whole class removed | LIVE |
| **#M⁻ bridge removed, core kept** | **LIVE** |
| #M⁻ whole class removed | LIVE |

Removing a single window is as effective as removing the entire class. So branch (ii)
does not require discarding a certified class at all — it requires rejecting **one
instance** of one class.

## 4. C3 — the targeted null

Shuffling the bridge message (unigram-preserving, 2000 shuffles) and counting windows
that match each class pattern:

- **#2⁻:** observed 1, null mean 0.001, p = 0.0010, corrected across the six candidate
  messages **p ≈ 0.006**. Corpus-wide, this pattern matches exactly four windows —
  E3@64, E4, W4, E5 — which are precisely its own instances. Nothing spurious anywhere.
- **#M⁻:** observed 1, null mean 0.015, p = 0.016, corrected **p ≈ 0.096**.
  Corpus-wide the pattern matches twice each in E1, W1 and E2 — its six real core
  instances — once in E3, and nowhere else. The analytic estimate (0.098) and the
  shuffle null agree to two decimal places.

So the two bridges differ by more than an order of magnitude in surprise. One is a
genuine cross-triplet repeat; the other is exactly what chance predicts.

## 5. C4 — what it costs

FR3 derived drift(T1) = drift(T2) from #M⁻ and drift(T2) = drift(T3) from #2⁻, and
FR4 built the one-gauge deduction partly on the chain. The two links are independent:
discarding #M⁻'s bridge removes the T1↔T2 link and leaves T2↔T3 intact. Under that
reading T1's drift is no longer tied to the other triplets, which is precisely the
freedom that makes the body-internal system live — the mechanism and the cost are the
same fact.

That is also a self-consistency check on the whole picture. The contradiction needs
cross-triplet coupling in order to bite; the coupling comes from two windows; one of
those windows is statistically unremarkable.

## 6. Where things stand

- **(i) openings not shared plaintext** — eliminated as a resolution (FR14).
- **(ii) some atlas instance not same-plaintext** — **now cheap and specific**: one
  window, E3@101, at coincidence grade p ≈ 0.10. Cost: FR3's drift(T1) = drift(T2).
- **(iii′) non-linear keystream** — still live: a single T3 reset at 66–68 or 102–103
  (FR13/FR14), at the cost of flattening most segment slopes.

These are no longer symmetric. Branch (ii) now names a specific, auditable object whose
statistical support is weak; branch (iii′) posits an unobserved cipher feature. Neither
is proven, but the burden has shifted.

## 7. Horizon

(1) **Re-run the pin pipeline with E3@101 excluded** and compare what gets certified
against the current inventory — if the sound core grows or stabilises, that is
independent corroboration; if it degrades, that argues the window is real after all.
(2) **Re-price FR3 and FR4** under the reduced bridge set, since the depth-stack and
one-gauge arguments both consumed the T1↔T2 link. (3) **Audit the remaining bridge**
the same way at the instance level — #2⁻'s core is three T3 instances, and its own
internal consistency deserves the same surgical treatment. (4) Standing: the T3 gap at
66–68, FR8's bridge-symbol search, anchor calibration at rep = 4.

## 8. Reproduction

`eyebridge2.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs
the 5-check gate — pattern-matcher exactness in both directions, null calibration
showing weak skeletons match often and strong ones essentially never, the
surgical-removal arithmetic, and the FR14 corpus control. The full run reproduces the
baseline guard, C1's geometry table, C2's removal tests, C3's shuffle nulls with
corpus-wide calibration, and C4. Failures carry prefix `XD-MBYG04K-URS3LF`. The
evidence-weight calculation in §2 is a two-line count from the atlas patterns.
