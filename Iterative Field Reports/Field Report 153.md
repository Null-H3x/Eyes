# Field Report 153 — THE SPACE IS ABOUT THIRTY READINGS, AND CONFLICT IS THIRD-ORDER

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Measuring the headline uncertainty

FR152 established that maximal mutually-consistent class sets are not unique and
give genuinely different alphabets. The question left open was **how many**.

90 greedy runs from random orders over the corpus's 208 strong classes, built
from classes alone (no pool, no E4/E5 merge, no FR32/33 passage):

```
runs reaching the maximum (496 relations) : 62
DISTINCT maximal skeletons                : 15
frequency profile : [19, 13, 8, 6, 5, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1]
Chao1 estimate of the total               : 33
discovery curve : 1, 5, 5, 7, 10, 10, 10, 10, 11, 12, 15
```

> **Roughly thirty distinct maximal readings**, of which 15 were observed. The
> discovery curve is still climbing, so 33 is an estimate rather than a count.

Two dominate — 19 and 13 of 62 runs — and nine were seen exactly once, which is
the shape of a space with a few attractors and a long tail.

**This is the project's real uncertainty**, and it is larger than "17 ratios,"
"62 repairs," or "2 serious readings." It also subsumes them: the repair choice
is one axis inside it.

---

## 1. Conflict is third-order, not pairwise

```
780 sampled class PAIRS tested for joint inconsistency : 0 conflict (0.0%)
```

**No two classes conflict.** Every inconsistency requires at least three
classes acting together. A found example:

```
L=19 s=1.50  East 3@77, East 4@2, West 4@2, East 5@2
L=11 s=3.56  East 1@39, East 1@67, West 1@39, West 1@69, East 2@44, East 2@79
L=17 s=3.28  East 4@48, West 4@50, East 5@49
```

Each pair is fine; all three together are impossible.

**This explains why the space is large and why greedy order matters so much.**
A pairwise conflict graph would let maximal sets be enumerated directly; a
third-order one does not, and it is why 90 runs still had not saturated.

It also explains FR151's irreducible contradiction: no single removal cleared
it because no single element was responsible.

---

## 2. What this does to the standing model

The adopted skeleton (794 relations, 61 glyphs) is built on the pool **plus**
the FR32/33 passage **plus** 19 classes, so it is richer than any pure-class
maximum — but it is a member of this family, and the family has ~30 members
that disagree on most values.

**Every figure conditional on the class selection:**

- the 435-position reading
- the 6-anchor programme
- `q[36] = q[68]` and the eight homophones
- the alphabet ceiling of 75

None is refuted. All are **one reading of about thirty**.

---

## 3. What survives untouched

- **The cipher form**: progressive keystream, linear in position (FR137 refuted
  the only rival)
- **The modulus 83** and the corpus transcription
- **The generator sweep**: 27.16 billion candidates, zero survivors
- **The plaintext negatives**: seven independent lines
- **Acquisition works regardless** — an external anchor is consistent with only
  some maximal sets, so it discriminates here too, and probably sharply

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Maximal-set space | unmeasured (FR152) | **~30 readings**, 15 observed, Chao1 33 |
| Conflict structure | assumed pairwise | **third-order** — 0 of 780 pairs conflict |
| Why greedy order matters | unexplained | **third-order conflict** makes it path-dependent |
| FR151's irreducible contradiction | puzzling | **explained** — no single element is responsible |
| Project uncertainty | repairs and ratios | **class selection, ~30-fold**, subsuming both |

---

## 5. Model status

Content unchanged: 794 relations, 61 glyphs, 8 homophones, 79.1% exposure,
435-position reading, 6 anchors. **Standing: one of approximately thirty
maximal-consistent readings.** Cumulative: 27.16 billion candidates, zero
survivors.

---

## 6. Horizon

1. **Measure how sharply an anchor discriminates the ~30.** If one known glyph
   value is consistent with only a few, acquisition is far more powerful than
   the 6-anchor figure suggests, and that changes the practical outlook.
2. **The artifacts must be rebuilt with this uncertainty stated.** Every shipped
   document describes a single reading as though it were the reading.
3. **Do not attempt to enumerate the space exhaustively** — third-order conflict
   makes that combinatorial, and 90 runs did not saturate a ~30-member space.
