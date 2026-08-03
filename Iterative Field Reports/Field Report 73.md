# Field Report 73 — THE ACQUISITION COST WAS UNDERSTATED BY 19 BITS, AND ANCHORS CANNOT PAY IT

*Instrument: `eyebase2` (gauge audit on the per-message bases). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — two figures the whole series has quoted

Since FR63 this project has carried two numbers as settled:

- the deliverable is **768 plaintext values**
- the acquisition cost is **14.46 bits**

Both concern the **alphabet**. Neither accounts for the **per-message bases**, and the
plaintext cannot be produced without them:

```
p[m][t] = q[c[t]] − base_m − drift·t
```

FR32 forced **seven base differences**. Seven differences over nine messages do not
determine nine values. That gap has been sitting in plain sight since FR32 and has
never been priced.

---

## 1. What the seven forced differences actually leave free

Running union-find over FR32's differences:

| group | messages | glyphs | share of corpus |
|---|---|---:|---:|
| 1 | East 1, West 1, East 2 | 320 | 30.9% |
| 2 | **West 2** (isolated) | 102 | 9.8% |
| 3 | East 3, West 3 | 261 | 25.2% |
| 4 | East 4, West 4, East 5 | 353 | 34.1% |

**Four connected groups, therefore four free base parameters.** West 2's isolation is
the same uncoupling FR35 found by a different route.

### 1.1 Gauge audit

| transformation | effect |
|---|---|
| `q → q + r`, `base_m → base_m + r` (all m) | p unchanged — **gauge, already consumed** by fixing `base_C1 = 0` in the 22,550 enumeration |
| `p → p + s`, `base_m → base_m − s` (all m) | ciphertext unchanged — **gauge, not yet consumed**, since a global relabelling of an unknown token stream is unobservable |

So one of the four is absorbed. **Three physically free base parameters.**

---

## 2. The corrected cost

```
alphabet      (drift x component bases, gauge-fixed) :     22,550  = 14.46 bits
message bases (3 free, 83 each)                      :    571,787  = 19.13 bits
TOTAL                                                : 1.289e+10  = 33.59 bits
```

**Quoted since FR63: 14.46 bits. Actual: 33.59 bits.** The understatement is 19.13
bits, a factor of 571,787 in candidates, and it is larger than the figure it corrects.

---

## 3. THE PART THAT MATTERS: anchors cannot pay it

An **anchor** is a (glyph, value) correspondence. It constrains `q`. It says nothing
whatever about `base_m`.

Only a **crib** — a known plaintext token at a known position in a known message —
constrains a message base.

**The entire acquisition programme targets `q` alone.** FR54's ordering, FR64's
arithmetic ("five anchors, one per component, gives a unique alphabet"), FR71's
calendar-as-anchor-source: every one buys alphabet bits and none buys base bits.

Restated correctly:

> Five anchors, one per component, determine the **alphabet uniquely** and leave
> **571,787 possible plaintexts**, in four groups whose token scales are mutually
> unrelatable.

FR64's claim that five anchors reduce 22,550 to 1 is arithmetically right and was
described as though it delivered the plaintext. It delivers the alphabet.

---

## 4. What survives untouched

**FR66's deliverable artifact is unaffected**, and this is worth stating because it
is the object the success criterion turns on. The 462 / 76 / 7 class-size profile was
computed **within (message, component) blocks**, where plaintext coincidence is
`v[t] = v[t′]` — drift-free *and* base-free. So the repeat-structure result, and the
"sits on the alphabet-83 line" conclusion, stand exactly as published.

Likewise FR72's delimiter exclusion, computed on the same channel.

**What changes is the description of the endgame.** Recovering `C` does not yield one
token stream. It yields **four**, each internally consistent, each on its own scale,
with no way to relate a token in East 1 to a token in East 4.

---

## 5. Where the missing bits could come from

Three parameters, 83 values each. Sources that would constrain them:

- **A crib.** Any known plaintext token at a known position fixes its group's base
  outright. One crib per group, three cribs total.
- **Cross-group isomorphs.** If any certified isomorph spans two message groups, it
  forces a base difference and merges them. FR34 established that cross-component
  bridges are made of dot cells; whether the same holds for cross-**group** message
  bridges has not been separately checked and is the natural internal test.
- **W2's isolation is the cheapest target.** It is one group entirely by itself,
  carrying 9.8% of the corpus. Any relation linking West 2 to another message removes
  one free parameter, 6.38 bits, for free.

---

## 6. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 74.1%; **alphabet ambiguity 22,550 (14.46 bits); message-base
ambiguity 571,787 (19.13 bits); total 33.59 bits**; alphabet size proven in [56, 83].

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Acquisition cost | 14.46 bits | **33.59 bits** — understated by 19.13 |
| "Five anchors → unique" (FR64) | read as delivering the plaintext | delivers the **alphabet**; 571,787 plaintexts remain |
| Anchors vs cribs | not distinguished | **anchors buy `q`, only cribs buy `base_m`** |
| The deliverable | one token stream of 768 values | **four streams**, mutually unrelatable in scale |
| FR66 artifact, FR72 delimiter bound | — | **unaffected** — computed base-free |
| West 2 | uncoupled (FR35) | **also its own message-base group**, 6.38 bits on its own |

---

## 8. Horizon

1. **Test for cross-group message bridges.** Internal, cheap, and the only route to
   removing base parameters without external evidence. West 2 first: it is isolated,
   worth 6.38 bits, and its uncoupling has been observed but never attacked directly
   as a base-linkage question.
2. **Re-scope the acquisition programme around cribs, not just anchors.** Three cribs,
   one per group beyond the gauge, are worth more than the sixth through tenth anchors.
3. **The success criterion** (FR66, FR72). The description has changed again and the
   decision should be made against the current one: four mutually unscaled streams of
   mostly-hapax tokens with no separators.
