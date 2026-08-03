# Field Report 78 — H4 IS MIRRORED: FR43's CENTRAL FINDING WITHDRAWN

*Instrument: `eyesign` (derivation plus empirical verification against FR74). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the only pre-motivated prior may be pointing backwards

The previous cycle derived the indicator constraint and got a drift coefficient of
**24·drift** for the East 3 / West 3 pair. FR43 records **82·drift** (= −drift). That
is a sign-convention difference on `w`, and I flagged it without resolving it.

It has to be resolved, because **H4 is the only pre-motivated prior this project
has.** It has been carried since FR43, used in FR44's retirement of H1, quoted in
FR53, FR64 and FR69, and is the one admissible constraint FR64 allowed for ranking the
22,550. If its drift set is the mirror of the truth, everything downstream points the
wrong way.

---

## 1. Derivation

```
same passage      p1[t] = p2[t+D]
                  q[c1[t]]   = p1[t]   + base_1 + drift*t
                  q[c2[t+D]] = p2[t+D] + base_2 + drift*(t+D)
subtract          q[c2] - q[c1] = (base_2 - base_1) + drift*D
in-component      q[c2] - q[c1] = drift*(Delta_c2 - Delta_c1)

=>  w := (Delta_c2 - Delta_c1 - D) = (base_2 - base_1) / drift
```

---

## 2. Empirical verification

FR74's bridge scan was built to detect cross-group bridges. It also, incidentally,
**recovered six of FR32's seven forced values independently** — and those six fix the
convention:

| scan | value | FR32 | value | |
|---|---:|---|---:|---|
| w(East 1 → West 1) | 0 | base[W1] − base[E1] | 0 | match |
| w(East 1 → East 2) | 77 | base[E2] − base[E1] | 77 | match |
| w(West 1 → East 2) | 77 | base[E2] − base[W1] | 77 | match |
| w(East 4 → East 5) | 0 | base[E5] − base[E4] | 0 | match |
| w(East 4 → West 4) | 54 | base[W4] − base[E4] | 54 | match |
| w(West 4 → East 5) | 29 | base[E5] − base[W4] | 29 | match |

**Six of six.** The convention is `w(m1→m2) = (base_2 − base_1)/drift`, confirmed by
an instrument built for an unrelated purpose.

---

## 3. The correction

Applying the confirmed convention to the indicator constraint:

```
label_E3 - label_W3 = (q[E3] - q[W3]) - (base_E3 - base_W3)
                    = drift*(31 - 61) + drift*54
                    = drift*24
```

FR43 reports `drift*82`. **FR43 used the opposite sign for `w`.**

| | drift set |
|---|---|
| H4 as published (FR43) | 1, 2, 3, 4, 5, 6, 7, 8, 75, 76, 77, 78, 79, 80, 81, 82 |
| **H4 corrected** | **7, 14, 17, 21, 24, 28, 31, 38, 45, 52, 55, 59, 62, 66, 69, 76** |
| overlap | 7, 76 |

Sixteen values either way, so **the bit value is unchanged at 2.36**. What changes is
*which* sixteen — and the two sets overlap in only two places.

---

## 4. WHAT THIS WITHDRAWS

FR43's headline was that H1 and H4 **cannot both be true**:

> *"H1 requires drift 31, which is NOT among them. → THE TWO HYPOTHESES ARE
> INCOMPATIBLE: at most one can hold... at least one of the project's two structural
> readings is wrong. First result of its kind in the series."*

**31 is in the corrected set.** The incompatibility does not exist, and FR43's central
finding is **withdrawn**.

What replaces it is the other branch FR43 itself anticipated: *"two hypotheses either
agreeing on one drift... or disagreeing."* They agree. But the agreement is worth
much less than FR43 priced the alternative at. H4 admits 16 of 82 drifts, so a random
H1 prediction lands inside it with probability **16/82 ≈ 0.195**. A one-in-five
coincidence is not evidence; FR43's "1-in-83" figure assumed H4 named a single value.

**FR44's retirement of H1 is unaffected.** It rested on the coherence argument — H1's
glyphs sit at terminal positions of opening blocks, which under the stamped-header
reading carry no plaintext token, so H1's claim has no referent. That argument stands
independently. What needs restating is FR44's *framing*, which presented itself as
resolving FR43's conflict. There was no conflict to resolve.

---

## 5. What is unaffected

- **The indicator base constraint** from the previous cycle. It uses
  `|label difference| ≤ 8`, which is symmetric, so the 4.58-bit saving and the
  identification of glyph 76 as a dual-payoff target both stand.
- **H4's bit value**, 2.36, unchanged.
- **Everything not keyed to specific drift values.** FR53's packing verification used
  drifts 1, 2, 3, 5, 7, 17, 31, 41, 82 as samples, not as H4 members.

---

## 6. Methodological note

This correction was possible only because FR74's instrument, built to hunt
cross-group bridges, **incidentally reproduced six published values it was not
designed to check.** Those six were the entire basis for resolving the sign.

Worth recording as a design preference: instruments that recompute known quantities
along the way are more valuable than instruments that assume them, even when the
recomputation is not the point. FR74 could have taken FR32's values as given and
scanned only for new ones; it would have been faster and this error would still be
in the doctrine.

---

## 7. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity clean;
exposure 74.1%; alphabet 14.46 bits; message bases 19.13 bits (14.55 under the
indicator constraint); alphabet size in [56, 83]. **H4 corrected; FR43's
incompatibility finding withdrawn.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 8. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| `w` sign convention | ambiguous across reports | **`w(m1→m2) = (base_2 − base_1)/drift`**, 6/6 empirical confirmation |
| H4 drift set | {1..8, 75..82} | **{7,14,17,21,24,28,31,38,45,52,55,59,62,66,69,76}** |
| H1 vs H4 | incompatible (FR43) | **compatible** — 31 is in the corrected set |
| FR43's central finding | "at least one structural reading is wrong" | **WITHDRAWN** |
| H1/H4 agreement | would be 1-in-83 (FR43) | **1-in-5** (16 of 82) — not evidence |
| FR44's retirement of H1 | rested partly on the conflict | **stands** on the coherence argument; framing restated |

---

## 9. Horizon

1. **Re-check anything else keyed to H4's specific values.** The bit value is
   unchanged, but any analysis that used the *members* rather than the count needs
   redoing against the corrected set.
2. **Acquire glyph 76** (previous cycle). West 2's indicator, undetermined, and the
   only glyph in the corpus with dual payoff — alphabet anchor plus base constraint.
3. **Audit the atlas for within-T2 classes** (FR76, FR77). Five channels now find
   nothing.
4. **The success criterion** (FR66, FR72, FR73). Unchanged.
