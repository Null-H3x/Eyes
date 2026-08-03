# Field Report 114 — INDICATORS ARE NOT ANCHORS, AND A FIFTEEN-TOKEN CRIB SOLVES THE DRIFT

*Instrument: indicator-pair census and planted crib simulation. July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. SELF-CORRECTION — I proposed a route that does not work

Last cycle I observed that **four of the nine indicator glyphs sit in component
1** (East 1: 50, East 3: 63, West 3: 34, East 4: 27), that all four triples
satisfy FR113's determinant criterion, and I described this as *"three to open,
one to test"* — a free shot at the acquisition programme's opening move.

**That was wrong.** An anchor, in the spec's sense, is a point of the
**alphabet**: `q[g] = known`. What an indicator hypothesis supplies is

```
q[ind_m] = p[m][0] + base_m + K_g[0] = L_m + b_m        with b_m UNKNOWN
```

Knowing a plaintext token does **not** give `q[g]`. It gives `q[g]` minus an
unknown per-message offset. **Four indicators are not four anchors.** They are
four equations each carrying its own new unknown, which is no constraint at all.

---

## 1. What survives, and it is one equation

An indicator *pair* is usable only if **both** conditions hold: the two
indicator glyphs lie in the same component (so the model determines their `q`
difference), **and** the two messages have a forced base difference (FR32's
seven). Census over all nine messages:

| pair | forced base diff? | indicators | usable? |
|---|---|---|---|
| **East 3 / West 3** | yes (w = 54) | 63, 34 — **both C1** | **YES** |
| East 1 / West 1 | yes | 50 (C1), 80 (C6) | no — different components |
| East 1 / East 2 | yes | 50, 36 — **36 undetermined** | no |
| West 1 / East 2 | yes | 80, 36 — undetermined | no |
| East 4 / West 4 | yes | 27, 77 — undetermined | no |
| East 4 / East 5 | yes | 27, 33 — undetermined | no |
| West 4 / East 5 | yes | 77, 33 — both undetermined | no |

**Exactly one usable pair.** Cross-triplet indicator pairs (E1/E3, E1/E4,
E3/E4) have no forced base difference, so each carries a free unknown.

One equation, against two unknowns after the scale gauge (the ratio and `d2`),
**leaves 17 candidates — precisely the two-anchor state of FR107. The indicator
route cannot resolve the drift.**

**FR44 was right and is now sharpened.** It concluded the label structure
"leaves no trace in the ciphertext and cannot be attacked from inside the
corpus". The reason is now exact: seven of the eight forced-base-difference
pairs have at least one *undetermined* indicator, and the eighth spans two
components.

---

## 2. The general principle this exposes

The correction generalises well beyond indicators, and it should have been
stated in the specification from the start:

> **No plaintext knowledge gives an anchor.** Knowing `p[m][t]` yields
> `q[c[m][t]] = p[m][t] + base_m + K_g[t]` — an *equation*, carrying the
> unknown `base_m` and the drift term. An **anchor** requires knowing the
> alphabet directly, `q[g] = v`, which is knowledge about `C`'s construction
> rather than about any message.

These are different kinds of external evidence, and the spec conflated them.
Anchors are strictly stronger per unit; cribs are far more plausible to obtain.

---

## 3. What a crib actually buys — measured

A **crib** is known plaintext over `L` consecutive positions of one message. It
contributes one equation per position whose glyph is in a component, against
`b_m` plus one base per component touched. Planted simulation over the full
valid space (1,394 `(d1,d2)` pairs), 40 trials per length:

| crib length | surviving `(d1,d2)` — median | min | max |
|---:|---:|---:|---:|
| 2 | 1394 | 16 | 1394 |
| 3–4 | 1394 | 1 | 1394 |
| 5–6 | **17** | 1 | 1394 |
| 8–10 | **1** | 1 | 1394 |
| 12 | **1** | 1 | 17 |
| **15** | **1** | **1** | **1** |
| 20 | 1 | 1 | 1 |

> **A crib of fifteen consecutive plaintext tokens, anywhere in any message,
> resolves the drift completely — every time.** Eight to ten usually suffices;
> below five, nothing.

The spread at lengths 8–12 is coverage: a crib landing among undetermined
glyphs contributes no equations, and one spanning many components adds an
unknown per component. Fifteen is where the corpus's 74.1% determination
guarantees enough equations regardless of placement.

---

## 4. Why this reframes acquisition

The programme has been specified as **eleven alphabet anchors**. It now has a
second, independent form:

| route | what is needed | plausibility |
|---|---|---|
| **anchors** | `q[g] = v` for 3 glyphs in one eligible component, plus 8 more | requires knowing `C`'s construction — nobody has ever offered a mechanism |
| **crib** | 15 consecutive plaintext tokens in one message | requires knowing part of the message — the classical cryptanalytic target |

**The crib route is the more realistic one**, and it was invisible while the
spec spoke only of anchors. It is also the route any external contributor —
Petri, or anyone who identifies the inner layer — would naturally supply.

Neither route is available today. But the target is now stated in a form that
someone outside the project could actually satisfy.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Indicators as anchors** | 4 in C1, "three to open, one to test" (last cycle) | **WRONG** — indicators give `q` minus an unknown offset |
| Usable indicator pairs | unexamined | **exactly 1** (East 3 / West 3); route yields one equation |
| Indicator/label hypothesis | untestable (FR44) | **confirmed and explained** — 7 of 8 forced pairs have an undetermined indicator |
| "Anchor" | a plaintext token matched to a glyph | **a point of the alphabet, `q[g] = v`** — plaintext knowledge is not this |
| Cribs | not in the specification | **the second acquisition route**; 15 tokens resolve the drift always, 8–10 usually |
| Acquisition framing | 11 alphabet anchors | **11 anchors OR one 15-token crib** |

---

## 6. Model status

Unchanged: 384 relations over 56 glyphs; injectivity clean at 17 ratios;
exposure 74.1%; components (25, 11, 7, 3, 2, 2, 2, 2, 2). Cumulative: 27.16
billion candidates, zero survivors.

---

## 7. Horizon

1. **Add the crib route to `ACQUISITION_SPEC.md`**, with the length curve and
   the anchor-versus-crib distinction stated explicitly. The spec currently
   asks for something almost nobody could supply and omits the thing they
   could.
2. **The indicator route is closed.** Do not reopen it: the census in §1 is
   exhaustive over all nine messages and the limitation is structural, not a
   matter of insufficient search.
3. **A note on this cycle's error.** I proposed the indicator route *in
   conversation*, outside the EYESPIRAL loop, and it did not survive its first
   CHALLENGE I. That is the loop working — but it is also an argument for
   running proposals through the loop before stating them as findings, which I
   did not do.
