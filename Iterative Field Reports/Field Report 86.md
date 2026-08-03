# Field Report 86 — T3 RECOVERED AS A TRIPLE; T2 UNCHANGED

*Instrument: `eyegroup2` (per-pair cutoffs). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — is the per-pair cutoff fair?

FR85 showed the shared header is not a uniform 24 (T1 24, T3 20, T2 5), and flagged
FR76's grouping re-derivation as likely affected since it used the uniform figure.

The correct fix looked unfair at first: comparing each pair **only from the first
position where they differ** removes exactly the positions where they agree, which
seems to penalise pairs with long headers.

It is not unfair. **Stamped agreement is not depth evidence.** If two messages share 24
literal positions, those positions say nothing about whether they share a keystream.
Removing them is the correct treatment, and a pair with a long header simply has less
usable evidence — which is a fact about the corpus, not a bias in the test.

---

## 1. Result

Per-pair cutoffs, all 36 pairs, threshold from a max-over-36 null (95th pct = 3.90):

| A | B | cutoff | obs | z | | |
|---|---|---:|---:|---:|---|---|
| East 1 | West 1 | 25 | 20 | **+17.35** | within T1 | **EDGE** |
| East 4 | East 5 | 21 | 11 | **+8.56** | within T3 | **EDGE** |
| **West 4** | **East 5** | 21 | 6 | **+4.35** | within T3 | **EDGE — new** |
| East 2 | East 4 | 3 | 4 | +2.01 | cross | |
| East 1 | East 2 | 25 | 3 | +1.88 | within T1 | |
| West 1 | East 2 | 25 | 3 | +1.76 | within T1 | |
| West 2 | West 3 | 6 | 3 | +1.72 | within T2 | |

**Grouping:** `{East 1, West 1}`, **`{East 4, West 4, East 5}`**, and four singletons —
East 2, West 2, East 3, West 3.

FR76's uniform-24 grouping was `{E1,W1}`, `{E4,E5}` and five singletons.

---

## 2. What changed

**T3 is now recovered as a complete triple by coincidence alone.** West 4 was at
+3.61 under FR76's threshold of 4.12 and is at +4.35 under this one of 3.90 — it
crosses on both counts. FR76's headline conclusion, *"body evidence supports pairs,
not triplets"*, is **corrected for T3**.

**T1 is not.** East 2 sits at +1.88 and +1.76 and remains separate.

**T2 is unchanged.** Best within-T2 pair is West2/West3 at +1.72, less than half the
threshold. The correction that rescued West 4 does nothing for T2.

---

## 3. The asymmetry between the two odd messages

Both East 2 and West 4 are "odd messages" — the third member of their triplet, absent
from the near-duplicate pair. Both are attested by the atlas (classes #M and #2) and by
the header tree (FR83). But they behave oppositely under coincidence:

| | coincidence | isomorphs (FR77) | header (FR83) |
|---|---|---|---|
| **West 4** | **+4.35, visible** | 5 with E4, 3 with E5 | in T3's leaf |
| **East 2** | +1.88, invisible | **28 with W1, 16 with E1 — largest in corpus** | in T1's leaf |

**East 2 is the most isomorph-rich message in the corpus and the least
coincidence-visible.** That is not a contradiction, and FR77 explained why: aligned
coincidence needs shared plaintext *at the same index*, while a non-literal isomorph
needs only shared repeat *structure*, which survives offsets and different plaintext.

East 2 shares structure with T1 at an offset; West 4 shares plaintext with East 5 in
place. Different relationships, both real, and each visible to exactly one instrument.

---

## 4. Where T2 now stands

| channel | verdict | affected by the cutoff correction? |
|---|---|---|
| FR35 free-w scan | nothing | no |
| FR74 bridge scan | nothing | no |
| FR75 coincidence | **+2.88, marginal** | yes — weakened from "nothing" |
| **FR76/FR86 grouping** | **nothing, best +1.72** | **yes — rechecked, unchanged** |
| FR77 non-literal isomorphs | nothing | no |
| FR83 header tree | splits T2 three ways | no |

**Five channels clean, one marginal.** FR85 flagged FR76 as possibly compromised; it
has now been rechecked and is not. The T2 result is firmer than FR85 left it.

---

## 5. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits;
inventory 82.5 CI [73.0, 93.7] via v-channel, 72.8 via header trie; determinacy
threshold 81.2, unresolvable by 51×. **Coincidence grouping: {E1,W1}, {E4,W4,E5}, four
singletons.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| FR76's "pairs not triplets" | published | **corrected for T3** — recovered as a complete triple |
| West 4's membership | atlas and header only | **coincidence-attested**, z = +4.35 |
| East 2's membership | atlas and header only | **still coincidence-invisible**; isomorph-attested instead |
| Cutoff convention | uniform 24 | **per-pair, from first differing position** |
| T2 after recheck | one channel possibly compromised (FR85) | **rechecked, unchanged** — five clean, one marginal |

---

## 7. Horizon

1. **Settle the header-length convention** (FR85 §3). It moves T2's coincidence margin
   by nearly 3σ and is the last unresolved methodological choice.
2. **Acquire glyph 76** (FR78) — West 2's indicator, dual payoff, and West 2 is now the
   only message unattested in every channel.
3. **The success criterion** (FR82 §7). Unchanged.
