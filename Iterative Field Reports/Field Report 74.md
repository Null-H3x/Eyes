# Field Report 74 — THE FOUR GROUPS DO NOT MERGE: 19.13 BITS REQUIRE CRIBS

*Instrument: `eyebridge4` (4/4 selftests, plant and null both corrected). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — is the base freedom even real?

FR73 priced the per-message bases at 19.13 bits. Before scanning, the obvious
question: could that freedom be an artifact of the stamped-header assumption?

If the openings were **encrypted** shared plaintext, then positions 1 and 2 carrying
identical glyphs across all nine messages would force `base_m + K_g[1]` constant,
linking every base and collapsing 19.13 bits to zero.

**It is not an artifact.** FR32 forces `base[E2] − base[E1] = 77`, nonzero. Universal
base equality is excluded by the constraint system directly, independently of A4. The
19.13 bits are a property of the cipher, not a cost of an assumption, and A4 is
corroborated rather than merely convenient.

---

## 1. Gate — two corrections before corpus contact

**The plant under-produced.** Placing only the *target* end of each cell failed,
because within a component only |C| of the 83 Δ values exist, so a randomly required
target usually does not. Rewritten to place **both** ends from the set of same-component
pairs with the right Δ difference: 30 cells planted, recovered exactly at
`n=30, D=7, w=31`.

**The null is higher than intuition.** I asserted random pairs would peak at ≤5.
Measured: **mean 5.6, maximum 9** over 20 random pairs. Chance agreement on this
statistic is substantial, and any threshold has to come from the null rather than from
judgement.

---

## 2. The scan

All 36 message pairs, every shift, counting cells that agree on a single drift-free
`w`. Identical-glyph cells excluded (FR31's filter — they give `w` trivially and carry
no alphabet information).

```
within-group peaks (positive control) : n=7   mean 11.0  max 17
cross-group peaks                     : n=29  mean  3.5  max  5
shuffled-corpus null                  : mean  3.4  95th pct 4  max 6  (1,080 pairs)
```

**Cross-group agreement is indistinguishable from shuffled noise** (3.5 vs 3.4).
Threshold set at the null's 99th percentile (5); nothing clears it.

**VERDICT: no cross-group bridge. The four message-base groups cannot be merged from
inside the corpus.**

Strongest within-group recoveries, all matching FR32's forced values:

| pair | peak | shift | w | FR32 forced |
|---|---:|---:|---:|---:|
| East 4 / East 5 | 17 | +1 | 0 | 0 |
| East 4 / West 4 | 15 | +3 | 54 | 54 |
| West 1 / East 2 | 13 | +5 | 77 | 77 |
| West 4 / East 5 | 12 | −1 | 29 | 29 |
| East 1 / East 2 | 10 | +5 | 77 | 77 |
| East 1 / West 1 | 7 | +30 | **0** | 0 |

---

## 3. SCOPE — the power limitation, stated plainly

**The scan recovers six of seven known bridges, not seven.**

`East 3 / West 3` is a *forced* relation (`w = 54`) and the scan finds peak **3** at
`w = 62` — at the null, and at the wrong value. That triplet has the weakest shared
structure in the corpus (7.8% agreement, against 44.4% and 27.2%).

So the negative is bounded: **a cross-group bridge as weak as E3/W3's would be
invisible to this instrument.** What is excluded is bridges of strength comparable to
the other six.

A second limitation, structural rather than statistical: the identical-glyph filter
removes exactly the near-duplicate cells that carry the strongest signal. That is why
East 1 / West 1, the most similar pair in the corpus, peaks at shift +30 rather than 0.
The filter is correct — identical glyphs give `w` without constraining the alphabet —
but it costs sensitivity on precisely the pairs where sharing is greatest.

---

## 4. What this settles

The internal route to the 19.13 bits is closed at the demonstrated power. Combined
with FR73's finding that **anchors constrain `q` and only cribs constrain `base_m`**,
the acquisition programme now has two distinct requirements that no single evidence
type satisfies:

| unknown | bits | evidence type | status |
|---|---:|---|---|
| alphabet `q` | 14.46 | anchors, 5 well-placed | route known, source unknown |
| message bases | 19.13 | **cribs**, 3 (one per group beyond gauge) | **route now known to be external** |

**West 2 remains the cheapest single target**: alone in its group, 102 glyphs, 9.8% of
the corpus, and one crib in it is worth 6.38 bits. It is also the message FR35 found
uncoupled by an unrelated method, so three independent lines now agree that West 2
sits apart from everything else.

---

## 5. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity
clean; exposure 74.1%; alphabet ambiguity 22,550 (14.46 bits); message-base ambiguity
571,787 (19.13 bits); **total 33.59 bits**; alphabet size proven in [56, 83].

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Base freedom as an A4 artifact | unexamined | **not an artifact** — excluded by FR32's nonzero forced difference |
| Cross-group message bridges | untested | **NONE**, cross-group peaks at shuffled-noise level |
| Scan power | assumed adequate | **6 of 7 known bridges recovered**; E3/W3-strength bridges invisible |
| Chance agreement on this statistic | assumed ≤5 | **mean 5.6, max 9** on random pairs |
| The 19.13 bits | route unknown | **external cribs only**; no internal route survives |
| West 2 | uncoupled (FR35), own group (FR73) | **third independent line** — no bridge to anything |

---

## 7. Horizon

1. **One crib in West 2.** 6.38 bits, cheapest single unit of progress available, and
   the only unknown that a single piece of external evidence fully resolves.
2. **The success criterion** (FR66, FR72, FR73). The description has now changed three
   times and is strictly worse each time: four mutually unscaled streams of
   mostly-hapax tokens with no separators. The decision should be made against this
   description.
3. **Count the MSB states on the glyph inventory** (FR69). Unchanged, still cheap.
4. **The calendar as an anchor source** (FR71). Still needs a candidate mapping — and
   note it would buy alphabet bits, not base bits.
