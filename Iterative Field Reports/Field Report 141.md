# Field Report 141 — THE ALPHABET BOUND IS WITHDRAWN: THE SIMULATION NEVER PASSED ITS OWN CONTROL

*Instrument: `eyehomo.py` (4/4 gate). July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The crack, and what CHALLENGE I found in it

FR138 claimed the alphabet is "probably ≥ 60, plausibly 70–82" on the strength
of a homophone simulation: heavy homophony destroys isomorphs, so a small `k`
should produce fewer long isomorphs than the corpus shows.

**CHALLENGE I: was that simulation ever calibrated?** Its own `k = 83` row —
the bijective case, where it should agree best — reads:

```
k=83 (no homophones)  ->  18.2 / 58.5 / 144.8
real corpus           ->  53   /  73  /  93
```

**3× low at L=12 and 1.6× high at L=16.** A simulation that cannot reproduce
the corpus at the alphabet size where it should agree best cannot bound `k` at
all. FR138 never checked, and I published the bound anyway.

---

## 1. The fix, and it fails harder

FR138 planted an **arbitrary 60-glyph shared head** across all nine messages.
The corpus's real shared structure is the atlas's thirteen classes at their
actual positions and lengths. Rebuilt with those planted instead, 30 seeds per
`k` rather than 4:

```
   k  merges          L=12            L=14            L=16
  83       0     4.5 +- 8.1      9.2 +- 13.3     15.4 +- 18.8
  80       3     2.8 +- 5.8      7.3 +- 11.7     13.4 +- 19.4
  75       8     3.1 +- 5.1      6.4 +-  7.8     10.4 +-  9.9
  70      13     1.3 +- 2.2      3.4 +-  4.4      6.5 +-  7.3
  60      23     1.0 +- 1.9      2.2 +-  3.2      3.2 +-  4.1
  56      27     1.1 +- 3.8      2.2 +-  6.8      3.7 +- 10.0
  30      53     0.0 +- 0.0      0.0 +-  0.0      0.0 +-  0.0

REAL CORPUS      53              73              93
```

**[R1] POSITIVE CONTROL FAILS, worse than before:**

```
L=12: simulated  4.5 +-  8.1   real 53   ratio 0.09   FAIL
L=14: simulated  9.2 +- 13.3   real 73   ratio 0.13   FAIL
L=16: simulated 15.4 +- 18.8   real 93   ratio 0.17   FAIL
```

**No bound is reported. FR138's "alphabet probably ≥ 60" is WITHDRAWN.**

---

## 2. What the failure means, and it is not nothing

The simulation produces **one tenth** the long isomorphs the corpus contains,
even with a bijective alphabet and the real shared spans planted. So:

> **The corpus has far more long isomorph structure than a progressive cipher
> over independent plaintext generates, even given its own shared passages.**

Three readings, and I cannot separate them:

1. **The shared structure is much larger than the atlas records.** FR136 found
   208 distinct classes against the atlas's 13 — planting only 13 would then
   under-plant badly. This is the explanation I find most likely.
2. **The plaintext is far more repetitive than independent draws**, in a way
   the seven "featureless" measurements cannot see, because they measure only
   the 191-position determined region.
3. **The generative model is wrong** in some way the constraint analysis does
   not expose.

Reading 1 is testable and reading 2 would be a major finding. Neither is
established here.

---

## 3. The methodological point

This is the **second** time in four cycles that a positive control has
overturned a published claim — FR137's autokey scored 100% out-of-sample and
was degenerate; FR138's bound rested on a simulation that never reproduced the
corpus. Both were caught by asking *what does this test do when the answer is
already known?*

**FR138's error is the sharper one:** I ran a simulation across ten values of
`k`, read off the shape, and never checked the row where the answer was known.
The control was **in the table** and I did not look at it.

**Standing rule, added:** *a simulation that varies a parameter must be checked
at the value where the answer is known, before any row is read.*

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Alphabet ≥ 60** (FR138) | supported by simulation | **WITHDRAWN** — control fails at ratio 0.09–0.17 |
| Alphabet range | [56, 82], probably ≥60 | **[56, 82], no internal narrowing at all** |
| FR138's simulation | indicative | **invalid** — arbitrary planted head, control never checked |
| Calibrated version | — | **also fails**, 10× low with real spans planted |
| Corpus isomorph density | unexamined | **~10× what the model generates** — unexplained |

---

## 5. Model status

Unchanged except the alphabet claim. Repair C: 409 relations, 57 glyphs,
191-position reading. **Alphabet [56, 82], with no evidence narrowing it from
either end.** Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **The isomorph-density gap is a real, unexplained observation** and the
   first new one in many cycles. The corpus carries ~10× the long-isomorph
   structure a progressive cipher over independent plaintext produces. FR136's
   208-class finding is the cheapest explanation and is directly testable:
   plant all 208 rather than 13 and re-run the control.
2. **The alphabet size is now genuinely unbounded within [56, 82]**, and
   nothing internal will move it.
3. Acquisition unchanged.
