# Field Report 115 — THE ENUMERATION ATTACK IS DEAD, AND ITS POWER WINDOW IS EXACTLY WHAT WAS ALREADY EXCLUDED

*Instrument: `eyeattack.py` (4/4 gate, power calibrated before corpus contact). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. SELF-CORRECTION — my search-space figure was the wrong space

I quoted the residual space in conversation as **8.8 × 10¹⁰ = 2^36.4** and
called it enumerable. That figure is correct **for the space of 56-glyph
readings `q`** — `(d1, d2)` times packing-valid component bases — and it is
genuinely enumerable.

**It is not the attack space.** Scoring by plaintext statistics requires

```
p[m][t] = q[c[m][t]] - b_m - d_g*t
```

and the per-message offsets `b_m` are further unknowns. FR32 forces seven base
differences, linking T1's three messages, T3's three, and East 3/West 3 —
leaving **four free `b_m`** (T1: 1, T2: 2 since West 2 floats, T3: 1). So the
plaintext space is

```
8.8e10  x  83^4  ~  4.2e18  =  2^62      NOT enumerable
```

I should have distinguished the reading space from the attack space and did not.

---

## 1. The one channel that survives, and why it is new

Within a single message and a single component, `b_m` cancels from differences:

```
p[t] - p[t'] = (alpha_t - alpha_t')*d1 + (beta_t - beta_t')*d2 - d_g*(t - t')
```

— dependent on `(d1, d2)` **alone**: not on component bases, not on `b_m`. That
reduces the attack to **1,394 candidates**, trivially cheap.

**This channel is new under two drifts.** FR30 proved these coincidences are
drift-*independent* — but under one drift, where the difference is
`d*(v_t − v_t')` and `d` cancels because it is invertible. With two drifts it
does not cancel. **The channel FR30 closed reopens**, and the gate confirms it
varies: 13 distinct counts across the 17 ratios.

Usable sample: **8,227 within-block pairs** across 72 blocks — over four times
FR30's 1,947, which excluded circular positions.

---

## 2. The decisive measurement: signal against spread

The scorer's discrimination is the size of the plaintext signal relative to the
spread of implied counts across candidates. Both are measurable without
touching the answer.

```
implied coincidence count over the 1,394 candidates:
    mean 117.8   sd 12.05   min 98   max 139
    uniform expectation (npairs/83) = 99.1
```

| plaintext inventory | signal (excess coincidences) | signal / spread |
|---:|---:|---:|
| **79** | 5.0 | **0.42** |
| 70 | 18.4 | 1.53 |
| **60** | 38.0 | **3.15** |
| 50 | 65.4 | 5.43 |
| 40 | 106.6 | 8.84 |

Selecting one candidate from 1,394 requires **10.4 bits**. At inventory 79 the
statistic supplies a signal 0.42 times its own noise — **410 of the 1,394
candidates lie within one standard deviation of the maximum.**

---

## 3. The verdict, and it is structural

> **The attack becomes viable at inventory ≈ 60 or below (signal/spread ≥ 3).
> FR36 and FR39 already excluded inventory below ~60 — at 3.3 sigma, by two
> independent mechanisms.**
>
> **The attack's power window and the excluded range are complementary. There
> is no overlap.** The attack works exactly where the plaintext cannot be, and
> fails exactly where it might be.

This is not a power shortfall to be fixed with more compute or a better
estimator. It is a structural coincidence between what the corpus permits and
what the statistic can see, and it kills the approach outright. **[R2] the
corpus was not scored; the calibration decided it.**

FR39's central estimate (effective alphabet 88.7, above 83) already pointed at
flat. This cycle shows that even if FR39 were wrong within its own confidence
band — anywhere in 60–83 — the enumeration attack still could not exploit it.

---

## 4. An artifact logged, not claimed

The implied counts average **117.8 against a uniform expectation of 99.1** — an
18.7 excess. This is **not** evidence of sub-uniform plaintext: it is present at
*every* candidate, including wrong ones, so it is a property of the skeleton's
block geometry rather than of any reading. Logged under the FR41/FR42
discipline, which the series has now applied seven times.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Residual space "2^36, enumerable" | stated in conversation | **reading space only**; the plaintext space is 2^62 |
| Free parameters | (d1,d2) + component bases | **plus four free `b_m`** (T1:1, T2:2, T3:1) |
| FR30's drift-independence | general | **a one-drift result**; the channel reopens under two drifts |
| Within-block channel | closed (FR30) | **open but powerless**: 8,227 pairs, signal/spread 0.42 at k=79 |
| Enumeration attack | proposed, ~20–30% odds | **DEAD** — power window complementary to the excluded inventory range |
| Mean coincidence excess 117.8 vs 99.1 | unexamined | **geometry artifact**, present at all candidates |

---

## 6. Model status

Unchanged. 384 relations over 56 glyphs; injectivity clean at 17 ratios;
exposure 74.1%; components (25, 11, 7, 3, 2, 2, 2, 2, 2). Reading space
2^36.4; plaintext space 2^62. Cumulative: 27.16 billion candidates, zero
survivors.

---

## 7. Horizon

1. **Do not attempt statistical attacks on the drift.** This cycle closes the
   last one with a structural argument rather than a measurement, which means
   variants will fail for the same reason. Any future attack must supply
   *external* information, not extract more from the corpus.
2. **The reading space being 2^36 is still worth carrying** — it is a genuine
   measure of how far the analysis got, and it means that **a single external
   crib or anchor set collapses the problem completely** rather than merely
   narrowing it. FR114's fifteen-token crib remains the operative target.
3. **The analysis programme is closed.** Every internal route — structural,
   statistical, generative, and now enumerative — has been exhausted with a
   stated reason. What remains is acquisition.
