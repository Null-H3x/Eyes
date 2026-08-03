# Field Report 68 — A 54-SIGMA SWING FROM THE NULL ALONE: THE FREQUENCY-CONTROL CLAIM REFUTED

*Instrument: `eyefreq` (6/6 selftests). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — what the wiki scour actually delivered

A survey of the Noita wiki produced mostly corrections and dead ends (section 5).
One item was different in kind: a **mechanism claim about data the project now
possesses.**

> *"It is speculated that the out-of-place words and punctuation may be evidence of
> their **frequency in the text being controlled**, which suggests an unsolved
> puzzle."*

This concerns the **solved English secret messages** buried throughout the game.
The wiki flags genuine anomalies in them: `"Why else would be here"` (missing
"you"), `"expect us the reveal"`, `"FRIENDHSIP"` [sic], `"what your seeking"`.

If developers constrained letter frequencies in readable material, that is a
deliberate channel in plain sight and a candidate source of external bits, which is
the one thing this project has been unable to obtain. Testable today, no anchors, no
dependence on the eye corpus. Correct target for the cycle.

---

## 1. THE SPECTACULAR FALSE POSITIVE

Twelve messages, 1,946 letters pooled. Against a null sampling letters i.i.d. from
English frequencies:

```
chi2 vs English = 404.9
null mu 24.9, sd 7.1
z = +53.23
```

Fifty-three sigma. The pre-registered threshold was +3. Had I stopped here, this
cycle would have reported the strongest signal in sixty-eight reports and a
breakthrough in external evidence.

**It is an artifact of my null, and the artifact is enormous.**

---

## 2. The correction, in two stages

**Stage one: natural English also fires.** Running the identical test on control
texts, the orb-room translations and the wiki's own prose:

| text | letters | chi² | z |
|---|---:|---:|---:|
| **secret messages** | 1,946 | 404.9 | **+52.81** |
| orb-room translations | 977 | 53.0 | +3.79 |
| wiki prose | 725 | 56.7 | +4.14 |

Ordinary English fires at +4. A letter-level i.i.d. null cannot model **word
repetition**, which every English text has. Normalised per letter, though, the
messages were still 3 to 4 times more deviant than the controls, so this stage
weakened the result without settling it.

**Stage two: the correct null.** The messages have an extraordinarily narrow
vocabulary — 515 tokens over 129 distinct words, type-token ratio 0.250, with
`YOU` appearing 61 times, `THE` 24, `WE` 23, `GOD` 20.

The null must preserve that structure while randomising the letters: replace each
distinct word with a random English word of the same length, keeping every
repetition intact. Against a 416,296-word English lexicon, 1,500 draws:

```
observed chi2       404.9
null mu 1373.0, sd 1140.4      null 5th-95th pct: 529 - 3377
z = -0.85
```

**The observed value sits BELOW the null mean.** The messages are *less* deviant
than random word-substitution produces. The letter distribution is exactly what
ordinary English with a repetitive vocabulary looks like.

---

## 3. Verdict

**FREQUENCY CONTROL IS NOT SUPPORTED.** The wiki's speculation does not survive a
null that models the actual generative process. The grammatical errors it cites are
better read as ordinary authorial slips, of which `FRIENDHSIP` is plainly one.

**The magnitude is the finding.** The same statistic on the same data moved from
**z = +53.23 to z = −0.85** — fifty-four sigma — purely from the choice of null.
FR42 recorded the same failure at `P` = 0.0013 → 0.108. This is that lesson two
orders of magnitude louder, and it is worth carrying as the canonical example:

> A null must model the process that generated the data, not a simplified marginal
> of it. Letter frequencies are a marginal; English text is the process.

---

## 4. Methodological note, since it was raised

This cycle was run under the revised two-tier posture: **generative readings enter
freely, and the filter is the gate.** The frequency-control claim entered without
scepticism, was developed into a specific testable form, and was killed by
measurement rather than by prior judgement. That is the intended shape, and it is
why the cycle got as far as producing a real result rather than a dismissal.

It also demonstrates the risk the posture carries. Admitting readings freely means
occasionally producing a 53-sigma artifact, and the only protection is that the
**null** receives the scepticism the hypothesis was spared.

---

## 5. Other outcomes of the scour

**CORRECTION — the centre symbol.** The wiki identifies the circle as the *"Magical
symbol"* shown at Holy Mountain collapse, Suomuhauki spawn and the endings. Outer
ring reads **MGICK** repeating, inner ring **MAGICK** repeating, centre resembling
the Arabic-Indic digit three, **٣**. My measurements agree (32 outer glyphs =
MGICK×6 + "MG"; centre resolves to 3 strokes). Combined with √ω being degenerate
mod 83, **the √ω ligature hypothesis should be retired**, along with the Work-altar
flip as its falsification target.

**CORRECTION — a miscount.** The record's *"Layer 4: 17 symbols"* refers to
ornament. Only two rings carry glyphs; the 24/20/17 bands are ovals and radial
dashes.

**CLOSED — the solved alphabets.** The Noita rune alphabet is **27 symbols** (A–Z
plus blank) mapped to English by the **identity**: glyph *n* is letter *n*. It
contains no ordering information. 27 alone, 54 (both cases) and 55 (plus blank) are
all excluded by the ≥56 floor; the admissible 81- and 83-symbol constructions were
swept (108,896 candidates, zero survivors).

**A9 REOPENED, then paid down.** The wiki states eye glyphs come in five
orientations, three per trigram, with the orthodox reading using 83 consecutive
values of the 125 possible. If labels were derived by *reading orientations* rather
than from engine indices, the frame is a choice and FR58's 432-element stabiliser is
live. Every ordering family with real provenance was therefore re-swept composed
with all 432 frames: **52,923,456 candidates in 26 seconds at 2.03M/s, zero
survivors.**

**NEW, UNEXAMINED — the Cauldron Room** reportedly provides a **30-bit binary key**
for a "Cessation Cypher" the community solved independently. Thirty bits is roughly
twice the 14.46 required here. First indication that keyed material exists in-game
at all.

---

## 6. Model status — unchanged

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 74.1%; 22,550 consistent alphabets; 14.46 bits; first anchor spent
on gauge; alphabet size proven in [56, 83].

**Cumulative sweep total: 84.5 million candidates, zero survivors.**

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Frequency control in solved messages | community speculation, untested | **REFUTED** — z = −0.85 under a repetition-preserving null |
| Letter-level nulls | used without comment | **BANNED for text** — 54-sigma artifact demonstrated |
| Centre symbol of the Magical symbol | √ω ligature (project record) | **٣ (Arabic-Indic three)** per wiki; √ω degenerate mod 83 |
| "Layer 4: 17 symbols" | carried as symbol count | **ornament**, not symbols |
| Noita rune alphabet | unexamined | **27 symbols, identity mapping, no ordering content** |
| A9 (labels = engine indices) | [RESOLVED] on single source | **[ASSUMED, single source]**; 432 frames swept regardless |
| Cauldron Room 30-bit key | unknown to this project | **new lead, unexamined** |

---

## 8. Horizon

1. **The Cauldron Room key.** Thirty bits of in-game key material, already solved by
   the community, never connected to the eye corpus. It is the only new external
   lead the scour produced and the first evidence that keyed material exists at all.
2. **Eye-level transcription.** Under the five-orientation reading there is a sharp
   test: since 82 = 3·25 + 1·5 + 2, the **first eye of every trigram must never take
   orientation 4**. One violation in 1,036 trigrams falsifies the segmentation and
   reading order. Needs raw eye data, not the index corpus.
3. **Decide the success criterion** (FR66 §1). Unchanged, and still prior to
   everything else.
4. **Five anchors, one per component** (FR64). Unchanged.
