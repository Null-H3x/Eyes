# Field Report 157 — THE CONSTANT-OFFSET MECHANISM IS REFUTED

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The hypothesis

FR151 established that the 48 contradictory classes are **real isomorphs that
are not co-plaintext**, but never asked by what mechanism. There is a specific
one, derivable rather than guessed.

Under the progressive cipher, two positions in one message collide iff

```
c[a+i] = c[a+j]   <=>   p[a+i] - p[a+j] = -d(i-j)
```

so a window's equality pattern is fixed by which index pairs satisfy that. **Two
windows share a pattern whenever `p[b+i] = p[a+i] + C` for a constant `C`** —
all differences are preserved, so all collisions are, so the isomorph is perfect
while the plaintext is not equal.

**Prediction:** cross-message alignments already carry a free base difference,
which absorbs `C`. Same-message alignments do not. So a constant-shifted repeat
should contradict through its **same-message** alignments only, and dropping
those should clear it.

---

## 1. SELF-CORRECTION — the first test was invalid

I built a custom system with a free constant column per alignment. It reported
8 of 48 cleared. **The control failed:** with the constant disabled, 4 classes
still came out consistent, though all 48 contradict under `AUD.build`.

My hand-rolled construction differed from the canonical one — it omitted the
E4/E5 merge row and rebuilt the dot-masking independently. **A result whose
control fails is not a result**, and the 8-of-48 figure is withdrawn.

Re-run using `AUD.build` throughout, with the mechanism tested by *restricting
which alignments are supplied* rather than by adding machinery.

---

## 2. The result: refuted

```
classes with NO same-message alignment  : 24   (mechanism does not apply)
classes with NO cross-message alignment :  8   (untestable this way)
CLEARED by dropping same-message pairs  :  0
still contradict                        : 16
```

**Zero of sixteen.** The contradiction survives even when every same-message
alignment is removed, so it does not live where the constant-offset mechanism
would put it.

And **24 of the 48 have no same-message alignment at all** — they are purely
cross-message, where a constant offset is already absorbed by the base
difference. For half the population the mechanism cannot even be invoked.

> **Constant-shifted repeats do not explain the contradictory classes.**

---

## 3. What remains of FR151's finding

Unchanged and now sharper: the corpus contains **48 strong isomorph classes that
are not co-plaintext**, 40 of them at #M⁻ strength or better, and the reason is
**not** a constant plaintext offset. Whatever produces them is something the
model does not currently represent.

Three candidates survive, none tested:

1. **A second-order relation** — `p[b+i] = a·p[a+i] + C` for a multiplier `a`,
   which also preserves collision structure if the drift transforms with it.
2. **Chance at a rate the surprise calculation understates**, if class instances
   are not independent (the nesting FR136 found suggests they are not).
3. **A genuine model error**, localised — 794 relations survive, so not global.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Constant-offset mechanism | derived, plausible | **REFUTED** — 0 of 16 testable classes cleared |
| Custom-build test | reported 8 of 48 | **withdrawn** — control failed |
| The 48 classes | unexplained (FR151) | **still unexplained**, and one explanation eliminated |
| Their composition | unexamined | **24 purely cross-message**, where the mechanism cannot apply |

---

## 5. Model status

Unchanged: extended skeleton, 794 relations, 61 glyphs, 8 homophones, 79.1%
exposure, 435-position reading, 6 anchors, one of ~30 maximal readings, 18
invariant relations. Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **The multiplier variant** (`p → a·p + C`) is the natural next candidate and
   is testable by the same alignment-restriction method — no new machinery, so
   no control risk.
2. **If that fails too, the 48 are a standing anomaly** and should be recorded
   as one rather than repeatedly re-explained.
3. **Never test a mechanism by building a new system when restricting the inputs
   to the existing one will do.** The custom build cost a cycle and produced a
   number that had to be withdrawn.
