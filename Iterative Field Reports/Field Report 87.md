# Field Report 87 — PERIOD 13 IS CLEAN, AND A TWO-LAYER POOLING ARTIFACT

*Instrument: `eyephase` (built on `eyeperiod`). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — a sweep that stopped one short of the motivated case

The position-0 discussion sharpened a general question: **where does a result rest on
coverage that stopped short of the structurally motivated case?**

One gap is concrete. FR56 swept coset IoC for a periodic keystream component at
periods **2 through 12** and found nothing, concluding the progressive premise holds.
But the corpus's own row structure is **39 eyes = 13 trigrams per row** — the motivated
period is **13**, one past where the sweep stopped.

FR70 tested block *sums* at B = 13 and found nothing. Nobody tested *periodicity* there.

---

## 1. The gap is clean

Coset IoC at periods 13 through 30:

```
p=13 (row period)   z = +1.00
best over range     p=14 at z = +2.57,  max-statistic corrected P = 0.132
```

**No keystream period in 13–30.** FR56's conclusion extends past its original range,
and the progressive premise is now tested across periods 2–30 rather than 2–12.

---

## 2. A signal that was not there

The companion test — is position mod 13 informative? — returned **z = +6.60**, with the
maximum at **phase 5**, not at the universal header positions. That looked like real row
structure.

It is two stacked pooling artifacts.

| measurement | header included | header excluded (pos ≥ 24) |
|---|---:|---:|
| pooled across messages | **+7.66** | **+3.78** |
| within messages only | +2.65 | **+0.61** |
| pooled, near-duplicate partners removed | +3.16 | **−0.25** |

**Layer one: the shared header.** Excluding positions 0–23 takes the pooled figure from
+7.66 to +3.78.

**Layer two: the near-duplicate pairs.** East1/West1 agree at 44.4% and East4/East5 at
27.2%, at aligned positions. Pooling across messages counts that agreement as
within-phase coincidence, while the null — which shuffles *within* each message —
destroys it. Removing the two partners takes +3.78 to **−0.25**.

The within-message version, which never had either contaminant, sits at **+0.61**.

**Nothing survives. Clean negative.**

---

## 3. The rule this generalises to

Four pooling artifacts now: FR39 (near-duplicate contamination), FR45 (shared-prefix
pooling), FR84 (header trie pooling), FR87 (both at once). It is the project's most
persistent error and it has a precise statement:

> **This corpus contains two systematic sources of cross-message agreement — the
> stamped header and the two near-duplicate pairs. Any statistic that pools across
> messages inherits both, and any null that shuffles within messages reproduces
> neither. The gap between them is not signal.**

Both contaminants must be removed explicitly, and they are **independent**: excluding
the header does not remove the near-duplicates, as §2 shows directly. FR39 removed one
and FR45 removed the other; this is the first cycle to find them stacked in a single
statistic.

The practical guard, since "be careful about pooling" has demonstrably not worked four
times: **before running any pooled statistic, compute the within-message version
first.** If the pooled figure exceeds it substantially, the excess is cross-message
structure and needs accounting for before it can be called a finding.

---

## 4. What this cycle establishes

- **The progressive keystream premise is tested across periods 2–30**, up from 2–12.
  A4 and A2 both stand.
- **No row-boundary structure**, at period 13 or any phase of it.
- **A reusable diagnostic**: the within-message/pooled comparison isolates cross-message
  contamination in one step, and would have caught FR39, FR45 and FR84 immediately.

---

## 5. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits
(29.01 only under the now-demoted position-0 premise); inventory 82.5 CI [73.0, 93.7]
via v-channel, 72.8 via header trie; determinacy threshold 81.2, unresolvable by 51×.
**Progressive premise verified at periods 2–30.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Keystream periodicity | tested at periods 2–12 (FR56) | **2–30**; p=13 at z=+1.00, best p=14 corrected P=0.132 |
| Row-boundary structure | untested | **none** — phase signal is entirely pooling artifact |
| Position 0 as label | assumed | **[ASSUMED, untestable]** per the preceding analysis; distinctness is not evidence (P=0.638) |
| Residual | 29.01 bits | **33.59 bits** with the position-0 constraint demoted |
| Pooling errors | three occurrences | **four**, first instance of two contaminants stacked |
| Guard against pooling | "be careful" | **compute the within-message version first**, always |

---

## 7. Horizon

1. **Re-audit prior pooled statistics with the within-message diagnostic.** It is cheap
   and it would have caught three of the four known errors. Candidates: anything in the
   doctrine reported as a single figure over all nine messages.
2. **Acquire an anchor per component** (FR64 ordering, reverted from the glyph-76
   priority now that position 0 is demoted).
3. **The success criterion** (FR82 §7). Unchanged.
