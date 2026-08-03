# Field Report 143 — THE GAP IS EIGHT CLASSES, NOT MISSING STRUCTURE

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. CHALLENGE I retires the obvious test

FR142 nominated lowering the class-enumeration threshold below `k ≥ 2` and
re-planting. **That is not a clean test.**

```
expected CHANCE instances corpus-wide:
   k=1 : 12.05        k=2 : 0.145        k=3 : 0.002
```

At `k = 2` a class with two or more instances is almost certainly real. At
`k = 1` it is almost certainly not. **Lowering the threshold would plant chance
matches as genuine shared plaintext, the simulated count would rise, and the
gap would appear to close as an artifact of planting noise.** Thirteenth
horizon item retired on inspection.

---

## 1. The cleaner measure, and it passes

Isomorph *pair* counts are quadratic in class size, so a few large classes
dominate them. Counting **distinct classes** instead:

```
REAL CORPUS              208 distinct classes
SIMULATION (k=83, all planted)   272.8 +- 24.8
ratio 1.31   -> MATCHED
```

Class-size distributions are close too: real `{2:117, 3:43, 4:28, 6:11, 7:9}`
against simulated `{2:165, 3:56, 4:30, 6:13, 7:6}`. And the simulation actually
carries **more** long classes than the corpus (215 vs 149 at length ≥20, mean
length 26.5 vs 22.7).

> **The structure is matched. Nothing is missing.**

---

## 2. So where does the L=12 gap come from?

That result contradicted the pair counts, which means one of my measurements
was mismatched. Chasing it to the specific window:

```
REAL  L=12:  8 qualifying classes,  53 pairs   sizes {2:2, 3:1, 4:3, 6:2}
SIM   L=12:  3.4 classes,           16.6 pairs sizes {2:1, 3:0.8, 4:1.2, 6:0.4}
```

**The corpus's five largest L=12 classes contribute 48 of its 53 pairs.** Two
classes with six instances give 15 pairs each; three with four instances give
six each.

> **The "10x isomorph-density gap" is eight classes at one window length, five
> of which carry 90% of the count. It is a high-multiplicity tail, not missing
> structure.**

Pair count is quadratic in instances, so a corpus that concentrates its sharing
into a few classes with six or seven instances will out-count a simulation that
spreads the same total sharing over more classes with two or three. That is
exactly what the size distributions show.

---

## 3. What this closes

**FR141's anomaly is fully resolved.** The sequence: apparent 10× gap (FR141),
mostly under-planting (FR142), remainder is the class-size tail (FR143). No
missing structure, no unexplained plaintext repetition, no model error.

**The alphabet bound stays withdrawn.** The pair-count statistic is dominated by
a handful of classes, so it was never a stable basis for bounding `k`. The
distinct-class count is better behaved but has a 1.31 ratio and ±25 spread —
far too coarse to separate `k = 60` from `k = 83`.

**Alphabet remains [56, 82] with nothing narrowing it.**

---

## 4. Self-correction

FR141 and FR142 both reported the gap as a *density* deficit and speculated
about missing shared structure or unseen plaintext repetition. **Both readings
were wrong.** The class counts were matched the whole time; I was comparing a
quadratic statistic across two distributions with different shapes and reading
the difference as absence.

**Standing rule, added:** *when a count is quadratic in group size, compare the
group distributions before concluding anything from the count.*

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Isomorph-density gap | mostly under-planting, residual unexplained (FR142) | **fully explained** — high-multiplicity tail at L=12 |
| "Missing short-scale structure" | live hypothesis (FR142) | **withdrawn** — distinct-class count matched at ratio 1.31 |
| Threshold-lowering test | nominated (FR142) | **retired** — would plant chance matches |
| Pair count as a statistic | used since FR137 | **unstable** — quadratic in class size; use distinct-class counts |
| Alphabet bound | withdrawn (FR141) | **stays withdrawn**; the method is too coarse in principle |

---

## 6. Model status

Unchanged. Repair C: 409 relations, 57 glyphs, 191-position reading, alphabet
[56, 82] unbounded within that range. Cumulative: 27.16 billion candidates,
zero survivors.

---

## 7. Horizon

**Crack 2 is closed and it was not a crack.** The alphabet cannot be bounded by
isomorph survival, and now the reason is understood rather than merely observed:
the statistic is dominated by a few high-multiplicity classes and cannot resolve
the effect being measured.

Of the six cracks listed, two are now sealed (triplet assignment, alphabet
bound), one was my own error (the 17-ratio claim), and three remain: the
plaintext measurements covering only 18.4%, the atlas redundancy tested on 12 of
195, and repair C being a 79x bet. **None is exploitable without more coverage,
and coverage needs anchors.**
