# Field Report 207 — THE SECOND-STAGE-KEY HUNT: EVERY REACHABLE IN-GAME ARTIFACT TESTED AND NULL, THE CESSATION DESIGN-GRAMMAR CORRECTION THAT REOPENED THE INNER LAYER, AND A CREATIVE REFRAME OF WHAT AN ANCHOR CAN BE

*July 2026. Cycle: EYESPIRAL-D, external-source campaign. This report catalogs
a full session of ruled-out key hypotheses driven by the Cessation Cipher
parallel (the principal's contribution), records one genuine correction to the
program's standing conclusion, and — per the closing brief — reassesses the
solution space with an eye to which creative assumptions could still move it.*

---

## 0. The correction that has to lead

Prior reports (FR173/203) concluded the eye payload is "flat, non-linguistic,
IC at the random floor, not a 26-letter language," and treated that as a
ceiling. **That verdict tested the wrong layer, and the Cessation Cipher
proves it.** Cessation's pipeline is: six pixel-symbols → base-6 digits →
skip-index a 30-bit binary key → a ~456-bit binary string → group into 7-bit
ASCII → the English sentence "SEEKING TRUTH, THE WISE FIND INSTEAD ITS
PROFOUND ABSENCE." The intermediate binary string in that pipeline **also has
flat IC** — it is an encoding *en route* to language, not language itself.

The eye "plaintext layer" this program recovered is almost certainly the
analog: an intermediate stream, not the terminal message. Flat IC at that
layer is *expected* for an intermediate encoding and is **not** evidence
against a solution. The standing "not language" finding is downgraded from a
ceiling to a floor: it says *this layer* isn't the message, not that *no
message exists downstream*. This is the most important single update in the
session and it is owed to the principal's Cessation reframe.

## 1. What was tested this session, and the verdict on each

Every candidate below was run against the certified reading with the standard
null discipline (geometry-preserving or shuffled-value nulls, never a
single-flag call). The catalog:

| candidate (source) | mechanism(s) tried | verdict |
|---|---|---|
| **Void Liquid Calendar** — normal (365 bit) + leap (366 bit), 3 slices each (first-30 / after-30 / full) | drift-value, additive keystream, Cessation skip-index, plaintext-XOR, direct plaintext-overlap, bit-gate | **null on all**; drift-sweep best is *pinned* to its shuffled null (145.5 = 145.5) — provably chance |
| **Coordinate RNG** (Lymm's binoculars script) | is the placement generator the cipher key? | keys *position* only; is the exact Park-Miller-XOR generator FR99/100 already swept null (27B candidates) — now *confirmed* to be the real generator, strengthening the null |
| **Launch asset files** (12,197 files, v1.0 Oct-20-2020 build) | scan for any fixed-length countable artifact in 83–366 | **none** — no embedded bitstring/numlist in any of 4,065 text files; 119 low-color image strips all identifiable art |
| **Orb coordinates** (11–12 per world) | fixed-coordinate key | **too few independent values** — parallel-world copies are rigid shifts (0 new info); ~22 independent numbers, below the 83-floor |
| **Emerald Tablet** (Purho's own orb_plan.txt transcription, 249 letters, in-band) | keystream, XOR, Vigenère, skip-index, base-generation, keyword-alphabet, direct crib | **null on all**; skip-index flagged chi2 7.4 but is *structurally vacuous* (readout is English by construction — raw tablet chi2 11.5) |
| **All orb-lore prose** (10 in-band Hermetic passages: Turba, Hermetic Museum, etc.) | XOR, Vigenère, base-generation | **zero signals**; no passage generates the bases |
| **Fixed structure coordinates** (111 tile-placements / 38 distinct structures, all independent, in-band) | 7 canonical orderings × 8 reductions × {keystream-collapse, base-gen, Vigenère}, primary "as above, so below" (Y-ascending) | **null on all** — best glyph-collapse 0/57, best base-gen 1/9, best Vigenère 115.6 vs English 36 |

Two of these deserve a note as *method* results, not just outcomes:

- **The Emerald Tablet skip-index false positive** (chi2 7.4, better than
  English's 36) was the session's sharpest trap. It dissolved instantly
  against the null: any readout that *emits key-text* scores English by
  construction, because the key *is* English, so shuffled eye data scores
  identically. **Doctrine, now explicit: for any natural-language key, the
  text-readout mechanisms (skip-index, direct-crib) are permanently vacuous;
  only mixing mechanisms (XOR, Vigenère, base-generation) that make the
  output depend on the eye values can discriminate.** This is a standing
  filter for all future key tests.
- **The fixed-structure coordinate set** was the strongest-constructed
  hypothesis of the session — genuinely independent values (unlike orbs), in
  the 83–366 band, tested in the *sacred* ordering (Y-sort by the Emerald
  Tablet's own "as above, so below," drawn from the very document the
  coordinates spawn near). It is null. When the best-built version of an idea
  tests clean, that is the informative kind of negative.

## 2. The convergent negative, stated plainly

Across the session, **every reachable, named, thematically-motivated in-game
key candidate tests as noise against the cipher.** This is no longer a string
of unlucky guesses; it is a near-exhaustive sweep of what is countable and
reachable in the game files, and it converges:

> The second-stage key, if one exists, is not an in-game artifact.

This is consistent with — and now strong evidence for — the principal's
original framing: **the eyes were encrypted *outside* the game and input into
it.** Every in-game sweep finds nothing because the key was never shipped in
the files; it lived with the author, before the encoding, and the game merely
renders the pre-made result (the wiki confirms the messages are
engine-generated with no associated sprites).

The negative is not discouraging — it is *locating*. It says the lever is
external, which is exactly where four independent theorems already pointed
(FR206): the whole determinable solution hangs on one `(message, position,
value)` anchor the corpus cannot supply from within.

## 3. What the certified model still guarantees (unchanged)

None of the above touches the recovered mechanism. The cipher remains:

`c[m][t] = C[(p[m][t] + b_m + d·t) mod 83]`

with the bases `b = [0,0,77,39,52,23,53,24,53]`, a single global linear drift
`d` (the one scalar unknown), and `C` fixed up to 8 homophones. The reading is
certified unique (FR199, proven by exhaustion), the mode is won by a
falsifiable 1,558-relation margin (FR205), and the structure is fully named
with zero loose quantities (FR204). **The mode-recovery half of FR101 is
done.** What remains unknown is the drift, three fragment constants, and — now
reopened by §0 — *what the intermediate stream decodes to* once absolute
values exist.

---

## 4. Creative reassessment — assumptions worth making to move the work

The brief asks what creative assumptions could further the solve. The honest
frame: internal cryptanalysis has hit its mathematical horizon, and the
external-artifact hunt is exhausted. Progress now requires *assuming* our way
past a barrier the data cannot cross alone. Five reframes, ordered by
leverage, each with the assumption it rests on and the test it enables:

### 4.1 Assume the payload is a *second cipher layer*, not a message (highest leverage)

The Cessation correction (§0) licenses this directly. **Assume the recovered
83-value stream is Cessation's "intermediate binary" analog** — an encoding
that requires one more transform to reach English. Under this assumption the
flat IC is not a wall; it is the expected signature, and the question shifts
from "what does the drift make it say" to "what *second operation* turns the
intermediate stream into text." The eye analog of Cessation's key-skip step is
the unknown. This is the single most promising reframe because it converts the
program's most persistent negative (flatness) into a positive prediction, and
it is testable the moment absolute values exist: run the Cessation-family
second-stage transforms (regroup base-5 → binary → 7-bit ASCII, digit-plane
splits, parity/threshold-to-bit) against an English gate — with the §1
vacuity filter enforced.

### 4.2 Assume the *header stamp* is the crib, not a preamble

FR206 judged the header a structural marker. **Assume instead it is authored
text** — the one place a human author would put something legible, and the
place with the richest drift-invariant structure (the ladders: T1 positions
1=12, 4=13, 5=22, 7=21). A single correct guess at *one* repeated-glyph's
meaning pins the drift outright (the ladder gives `gap × d`), which cascades to
the whole body. The assumption is cheap and self-validating: if the guessed
header word makes the body resolve, it is right; if not, discard. The
`HEADER_DECRYPTION_TABLE.md` kit already tests any such guess in one pass.

### 4.3 Assume the alphabet is *thematic*, not arbitrary

Every mechanism test so far assumes the plaintext-value → symbol map is
unknown/arbitrary. **Assume Purho keyed the substitution `C` with a word** —
the keyword-alphabet mechanism, but seeded from the *right* keyword. This
session tested the Emerald Tablet as a keyword and it failed, but the space of
thematically-plausible keywords is small and human: TRUTH, KNOWLEDGE, WISDOM,
HERMES, the names of the orbs, "the mad god of knowledge." A keyword sets `C`
directly; applying it to the recovered values and gating English is a bounded,
cheap sweep — and unlike a free permutation, it is *non-vacuous* because the
keyword fixes a specific ordering the eye values must satisfy.

### 4.4 Assume the drift `d` is a *meaningful constant*, not arbitrary

`d` is a single scalar in 1–82. **Assume it is a number Purho would choose on
purpose** — 42, 7, 33, a date, a game constant reduced mod 83. This is a
finite list, and each candidate `d` yields a complete absolute plaintext to
inspect *by eye* (not by gate — human judgment on 82 concrete decryptions is
tractable and immune to the vacuity trap). The calendar-as-drift test (d=33)
already fell, but the space of *deliberate* small constants is short enough to
walk manually. Combined with §4.1, a lucky `d` plus the second-stage transform
is a complete solve.

### 4.5 Assume the puzzle is *externally documented* — pursue the author's trail

Every in-game source is exhausted, so **assume the key's provenance is
external and discoverable**: Purho's public statements, dev streams, the
Noita ARG community's out-of-game findings, or the puzzle's original posting
context. The eyes were placed by a community member's tooling (Lymm) and
solved externally by design; the key may live in that external record, not the
binary. This is not cryptanalysis but *research* — and given the convergent
in-game negative, it is now proportionate.

---

## 5. The one assumption NOT worth making

For discipline's sake: **do not assume a new in-game artifact will succeed
where all others failed.** The session's convergent negative is strong. Any
further in-game candidate should clear a prior bar before it earns a battery
run — a *specific* fixed-length structured object (like the calendar's daily
bits), not more Hermetic prose (a falsified class) and not more coordinates (a
tested class). The vacuity filter (§1) and the independent-information check
(the orb-coordinate lesson) are the two gates every future candidate passes
first.

## 6. Artifacts and horizon

New this session: `struct_coords.json` (111 fixed structure coordinates,
extracted), `orb_passages.json` (20 orb-lore passages), the calendar
bitstrings (`cal_normal.txt`, `cal_leap.txt`), the Emerald Tablet forms, and
the coordinate/passage batteries (`/tmp` instruments, archived to the cycle
log). Ground-truth confirmed: exactly five eye sprites in the Oct-20-2020
launch build, locking base-5.

Horizon, reordered by the reassessment:
1. **The second-stage-transform battery (§4.1)** — build it now; it is
   internally runnable the instant any anchor fixes absolute values, and it
   attacks the reopened inner layer the Cessation correction exposed.
2. **The header-crib and keyword-alphabet sweeps (§4.2, §4.3)** — cheap,
   non-vacuous, human-checkable; either could pin the drift from one guess.
3. **The deliberate-constant walk (§4.4)** — 82 concrete decryptions,
   inspected by eye.
4. **The external author-trail research (§4.5)** — now proportionate given
   the exhausted in-game hunt.

The through-line of this cycle: the internal mechanism is solved, the in-game
key hunt is exhausted and null, and the Cessation parallel — while not
yielding a key — delivered the session's real prize, which is the correction
that the inner layer is *not* closed but merely one transform deeper than the
program was looking. The creative assumptions above are the ways to reach that
transform without the external anchor the mathematics says is otherwise
required — and the anchor, if it comes, makes all of them mechanical.
