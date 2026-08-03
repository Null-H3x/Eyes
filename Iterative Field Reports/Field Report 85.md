# Field Report 85 — THE HEADER IS NOT A FIXED 24: T2's VERDICT DEPENDS ON THE CUTOFF

*Instrument: `eyediverge` (corpus-only). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the ordinal hypothesis dies on inspection

FR83 left the header-ordinal test unrun: *"splits at positions 3, 6, 10, 21 with
distinct values per branch is the shape of a structured index."*

It fails structurally, before any statistics. If the header encoded a per-message
ordinal, every message would separate from every other. **It does not**: at position 21
East 1, West 1 and East 2 all carry value 29. The header's finest resolution is
**groups, not messages**, and position 0 is the only per-message distinguisher.

Tested anyway for completeness — pairs of branch values within 2 of each other,
against 20,000 random assignments:

```
observed 3   null mean 1.65 sd 1.19   z = +1.13   P = 0.212
```

**Clean negative.** The branch values do not encode ordinals.

---

## 1. The divergence profile

Shared-prefix length, stopping at first difference:

| | shared positions |
|---|---:|
| T1 pairs — E1/W1, E1/E2, W1/E2 | **24** |
| T3 pairs — E4/W4, E4/E5, W4/E5 | **20** |
| **T2 pairs — W2/E3, W2/W3, E3/W3** | **5** |
| **East 3 / T3 members** | **9** |
| everything else | 2 |

Two facts fall out. **East 3 shares more header with T3 (9) than with its own
triplet-mates (5)** — FR83's anomaly, now quantified. And the header tracks the base
groups (within 19.6, across 3.6) slightly better than the triplets (16.3 / 3.4).

---

## 2. SELF-CORRECTION — FR75 used the wrong cutoff for T2

FR75 measured "body" as positions ≥ 24 **uniformly across all triplets**, and concluded
T2's depth signal was **entirely** the shared header (z = +0.07). But T2's messages
diverge after position 5. On that reading, the uniform cutoff discarded **19 positions
of genuine body**.

Recomputed with group-correct cutoffs:

| triplet | cutoff 24 (FR75) | group-correct cutoff | |
|---|---:|---:|---|
| T1 | +13.48 | +13.48 (24) | unchanged |
| **T2** | **+0.03** | **+2.88 (5)** | **materially different** |
| T3 | +7.59 | **+9.35 (20)** | strengthened |

T2 pairwise at cutoff 5: W2/W3 **+2.66**, E3/W3 +1.60, W2/E3 +0.78.

**FR75's claim that T2's depth is *entirely* header was an artifact of the uniform
cutoff.** It is not entirely header; it is marginal.

---

## 3. The ambiguity, stated honestly

Which cutoff is right turns on what "header" means, and I cannot settle it:

- **Shared-prefix reading**: the header is the stamped block messages hold in common,
  ending where they diverge. T2's is 5 positions. Then z = +2.88.
- **Fixed-block reading**: the header is 24 positions for every message, with
  *branching content* — which is what FR44's prefix tree describes. Then z = +0.03.

The prefix tree itself favours the fixed-block reading, since it branches rather than
terminating. But under that reading T2's messages carry 19 positions of
message-specific stamped material, which is a strange thing for a header to do.

**What survives either way: T2 does not clear the +3 threshold.** The conclusion is
robust to the convention; only the margin moves, and it moves from "literally nothing"
to "marginal". That distinction matters for how firmly the six-channel result should
be stated.

---

## 4. Restating the T2 position

FR83 recorded six independent channels finding no internal structure in T2. That count
needs qualifying:

| channel | verdict on T2 | affected by this cycle? |
|---|---|---|
| FR35 free-w scan | nothing | no |
| FR74 bridge scan | nothing | no |
| FR75 coincidence | **+0.03 → +2.88** | **yes — weakened to marginal** |
| FR76 grouping re-derivation | nothing | uses the same cutoff; likely also weakened |
| FR77 non-literal isomorphs | nothing | no — cutoff-independent |
| FR83 header tree | splits T2 three ways | no |

**Four channels remain unaffected; one weakens to marginal; one inherits the same
issue.** The conclusion stands but is less overwhelming than FR83 stated it.

---

## 5. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits;
inventory 82.5 CI [73.0, 93.7] via v-channel, 72.8 via header trie; determinacy
threshold 81.2, unresolvable by 51×. **Header lengths per group: T1 24, T3 20, T2 5.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Header-ordinal hypothesis | untested (FR83) | **REJECTED** — resolves groups not messages; P = 0.212 |
| Header length | uniform 24 assumed throughout | **T1 24, T3 20, T2 5** — not uniform |
| FR75's "T2 depth is entirely header" | published | **overstated** — z = +2.88 at the group-correct cutoff |
| T2's depth verdict | z = +0.07, nothing | **+0.03 to +2.88** depending on convention; below threshold either way |
| T3's depth | +7.59 | **+9.35** at the correct cutoff |
| East 3's header affinity | noted (FR83) | **quantified** — 9 with T3, 5 with its own triplet |
| Six channels on T2 | all clean | **four clean, one marginal, one inherits the cutoff issue** |

---

## 7. Horizon

1. **Re-run FR76's grouping re-derivation with group-correct cutoffs.** It used the
   uniform 24 and is the one remaining result likely affected.
2. **Settle the header-length convention.** Shared-prefix versus fixed-block changes
   T2's margin by nearly 3σ. The prefix tree favours fixed-block; the 19 positions of
   message-specific stamped material argue against it.
3. **Acquire glyph 76** (FR78). Unchanged.
4. **The success criterion** (FR82 §7). Unchanged.
