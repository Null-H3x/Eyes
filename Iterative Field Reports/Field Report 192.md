# Field Report 192 — THE INDICATOR CRIB: THE PLAINTEXT IS DETERMINED, AND IT IS NOT A MESSAGE NUMBER

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Which cribs are even possible

**Dead on arrival:** word and phrase cribs, since the plaintext is not language
at any granularity (FR172/173/181); and the stamped headers, which are literal
glyphs carrying no encrypted plaintext to guess (FR165).

**Live and self-generated:** the **message indicators**. Position 0 of each
message is a distinct glyph — all nine differ — and if it encodes the message's
own identity that is nine cribs at once.

```
East 1  50    West 1  80    East 2  36
West 2  76    East 3  63    West 3  34
East 4  27    West 4  77    East 5  33
```

FR114 tested a version of this and found *"only 1 usable indicator pair."* That
was before **all 36 base differences were known** (FR178). Re-run.

---

## 1. The constraint is much stronger than FR114's

With every base difference forced, an indicator crib has **no free parameters**:

```
q[IND_m] - q[IND_m'] = (s_m - s_m') + (b_m - b_m')
```

Six of the nine indicators are determined, giving **ten testable pairs**:

```
q[36] - q[50] = 57   (E2 vs E1)  base diff 77
q[63] - q[50] = 23   (E3 vs E1)  base diff 52
q[34] - q[50] = 53   (W3 vs E1)  base diff 23
q[27] - q[50] = 76   (E4 vs E1)  base diff 53
q[63] - q[36] = 49   (E3 vs E2)  base diff 58
...
```

---

## 2. Every numbering hypothesis fails — but the system is consistent

```
hypothesis                            pairs tested  consistent
message index 0..8                              10           0
message index 1..9                              10           0
East 1-5 then West 1-4                          10           0
reverse 8..0                                    10           0
```

**Zero of ten, for every ordering.** But the ten equations are **mutually
consistent** — `s[E3]−s[E1] = 54` and `s[E3]−s[E2] = 74` and `s[E2]−s[E1] = 63`
close correctly (54 − 63 = 74 mod 83).

> **The model does not merely fail to confirm a numbering. It DETERMINES the
> indicator plaintext differences outright — and they are not a numbering.**

At drift 1: `E1=0, E2=63, E3=54, W3=30, E4=23`.

---

## 3. And that gives a drift test FR36 does not reach

Those values **scale with the drift**, so each `d` predicts a different
indicator sequence. A drift yielding a *structured* sequence would be evidence —
and this is magnitude-sensitive, so the scale-invariance results do not apply.

```
  d  consecutive  span  implied indicator values
 37            1    31  {E1:0, E2:7,  E3:6,  W3:31, E4:21}
 45            1    39  {E1:0, E2:13, E3:23, W3:22, E4:39}
 65            1    41  {E1:0, E2:28, E3:24, W3:41, E4:1}
 ...
 18            0    82  {E1:0, E2:55, E3:59, W3:42, E4:82}
```

**No drift produces a numbering.** The best is `d = 37` with one consecutive
pair and a span of 31, where a message-numbering crib needs a span of ~8 with
all values consecutive. **Null.**

---

## 4. What survives, and it is worth having

**The indicator plaintext is recovered up to the drift and one constant.** Five
of the nine messages have their opening symbol determined relative to each
other:

```
E1 = 0,  E2 = 63,  E3 = 54,  W3 = 30,  E4 = 23     (at drift 1)
```

That is **five plaintext values in a known relationship** — the closest thing to
a crib this project has produced, generated internally rather than acquired.

It is not yet usable: without the drift these are relative, and without an
external pin nothing anchors them. **But if one indicator's true value is ever
learned, four more follow immediately.**

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Indicator crib | 1 usable pair (FR114) | **10 testable pairs**, all base differences now forced |
| Message-numbering hypothesis | untested at scale | **refuted** for every ordering and every drift |
| Indicator plaintext | unknown | **determined relative**, `E1=0, E2=63, E3=54, W3=30, E4=23` at drift 1 |
| Drift from indicator structure | untried | **null** — no drift yields a numbering |
| Crib leverage | none | **five linked values**; one external pin propagates to all five |

---

## 6. Model status

Unchanged: 794 relations, 61 glyphs, one reading, five fragments, 819 positions
(79.1%). **Plus: five indicator plaintext values determined relative to one
another.** Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

**The indicator set is now the highest-value acquisition target**, ahead of the
6-anchor programme on cost-effectiveness: a single known indicator value yields
five plaintext positions *and* pins the drift, because the five differences are
known and one absolute value fixes the scale.

That is a better ask than "fifteen consecutive tokens" and it is a smaller one —
**one symbol, at a position anyone examining the messages would look at first.**
