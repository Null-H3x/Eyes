# Field Report 82 — THE CORPUS CANNOT DETERMINE WHETHER IT DETERMINES ITS OWN KEY

*Instrument: `eyeinv2` (within-message channel plus profile likelihood). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — tighten the number everything depends on

FR81 made the inventory estimate the most consequential figure in the project: the
determinacy threshold sits at **81.2**, and FR80's estimate was 82.1 with CI
[75.9, 89.4] — straddling it. Two routes to tighten without new evidence: add the
**within-message channel**, and replace the crude interval with a **profile-likelihood
CI**.

The within-message channel deserves emphasis. Coincidence there is `v[t] = v[t′]`
within a single (message, component) block — **drift-free and base-free**. It requires
no `w`, no sign convention, and no base assignment, which makes it **immune to every
error found in FR78, FR79 and FR80.**

---

## 1. Three estimates, one of them parameter-free

| channel | free parameters | pairs | inventory |
|---|---|---:|---:|
| cross-message | `w`, sign, bases | 12,314 | 82.1 |
| **within-message** | **none** | 8,058 | **83.1** |
| combined | — | 20,372 | **82.5** |

The parameter-free channel independently returns **83.1** — essentially exact
uniformity over the 83-symbol space. Three routes with different failure modes cluster
at 82–83.

```
combined MLE                   82.5
profile-likelihood 95% CI      [73.0, 93.7]
```

---

## 2. SELF-CORRECTION — FR80's interval was too narrow

FR80 reported CI [75.9, 89.4] using `n/(H ± √H)`, and concluded **inventory > 76**.
That interval is not a likelihood interval; the profile version on a *larger* sample is
**wider**: [73.0, 93.7].

**The bound is inventory > 73, not > 76.** FR80's claim to have tightened FR39's ">60"
survives, but by less than stated. Adding data widened the honest interval, which is
the correct behaviour when the previous interval was understated.

---

## 3. THE HEADLINE — the threshold is unresolvable from this corpus

The question FR81 leaves open is whether the true inventory sits above or below 81.2.
Separating those two hypotheses at 3σ requires:

```
required sample                     1,520,154 coincidence pairs
corpus can supply, 46 glyphs           20,372
corpus can supply, full 56 glyphs     ~29,743
                          shortfall        51x
```

Scaling does not help: at 4× the sample the separation is z = 0.69, at 20× it is
z = 1.55.

> **The corpus cannot determine whether it determines its own key.**

FR81 established that at the point estimate the corpus sits at 48% of its unicity
distance, with the caveat that the CI straddles the threshold. **That caveat is
irreducible.** No further internal analysis — not the full skeleton, not better
exclusion, not a better estimator — can resolve it, because the corpus is 51× too
short to distinguish the two sides.

---

## 4. What this establishes

**FR81's verdict is final as an internal matter.** The point estimate says the
ciphertext contains insufficient redundancy to determine the key; the uncertainty on
that verdict cannot be reduced from inside. Both the answer and the confidence in the
answer are now fixed.

**External evidence is needed twice over.** Not only to solve the cipher, but to
establish whether solving it was ever possible. That is an unusual position and worth
stating plainly: acquiring anchors and cribs would resolve the determinacy question as
a side effect of resolving the cipher.

**The bound that does hold.** Inventory ≥ 73 at 95%, and ≤ 65 excluded at z > 4. So
the plaintext uses at least 88% of the available 83-symbol space at near-uniform
frequency. Every small-alphabet hypothesis — English 26, Finnish 29, any syllabary —
remains excluded by an enormous margin.

**What it does not establish.** Whether the plaintext is meaningless or is a
well-encrypted inner layer. FR66 flagged that these look identical; FR82 adds that
they will *continue* to look identical at any sample this corpus can supply. That
distinction is not merely undetermined, it is **undeterminable** from the ciphertext.

---

## 5. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity clean;
exposure 74.1%; residual key entropy 33.59 bits; **plaintext inventory 82.5, profile CI
[73.0, 93.7], on 20,372 pairs across two independent channels**; determinacy threshold
81.2, unresolvable by a factor of 51.

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Inventory estimate | 82.1, CI [75.9, 89.4] (FR80) | **82.5, profile CI [73.0, 93.7]** on 20,372 pairs |
| FR80's bound | inventory > 76 | **> 73** — the crude interval was too narrow |
| Within-message channel | measured once, weakly (FR30) | **parameter-free corroboration at 83.1** |
| FR81's threshold uncertainty | open, awaiting a tighter estimate | **irreducible** — 51× shortfall |
| "Meaningless vs encrypted" | undetermined (FR66) | **undeterminable** from the ciphertext at any achievable sample |
| Internal programme | converging | **complete**, with the completeness now quantified |

---

## 7. Horizon

The internal programme is finished, and this time the claim is quantified rather than
impressionistic. Three cycles ago I would have said the same thing and been wrong
twice; the difference is that FR81 and FR82 give a number for why.

1. **Acquire glyph 76** (FR78) — West 2's indicator, dual payoff, ~2.3 bits plus an
   alphabet anchor against a floor of 17.
2. **Five anchors and three cribs.** FR73/FR74 established anchors buy the alphabet and
   only cribs buy the bases. FR81 established the floor. The programme is fully
   specified and entirely external.
3. **The success criterion**, restated once more. The decision is no longer *"is the
   output worth having?"* nor even *"is it recoverable?"* but **"is it worth acquiring
   external evidence to find out?"** — because that is the only question the corpus
   leaves open.
