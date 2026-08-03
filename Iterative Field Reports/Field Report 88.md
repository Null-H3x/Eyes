# Field Report 88 — THE FOUNDATIONAL DISCRIMINATOR SURVIVES THE FULL DIAGNOSTIC

*Instrument: `eyeiso2` (FR87's diagnostic applied to FR77). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — the highest-exposure pooled statistic

FR87 established the guard: **this corpus has two systematic sources of cross-message
agreement — the stamped header and the two near-duplicate pairs — and any pooled
statistic inherits both while any within-message null reproduces neither.**

The obvious retroactive target is **FR77's isomorph abundance**, because it is the
project's foundational discriminator (it excludes the entire ciphertext-feedback
family) and because it counts window pairs **from different messages**. FR77 measured
the near-duplicate contribution and found it small, but **never excluded the header** —
and messages share 20 to 24 identical header positions.

If the abundance were header-driven, the exclusion of ciphertext feedback would fall.

---

## 1. Header contamination is negligible

| L | non-literal pairs | both ends in header | share |
|---:|---:|---:|---:|
| 12 | 80 | **0** | 0% |
| 13 | 92 | **0** | 0% |
| 14 | 113 | 4 | 4% |
| 15 | 134 | 7 | 5% |
| 16 | 144 | 10 | 7% |

**Zero at the shortest lengths, 7% at the longest.**

The reason is worth recording, because it was luck rather than design: FR77 required
**at least two repeated positions** per window, to exclude the trivial all-distinct
pattern that matches everything. Header windows are mostly all-distinct — the stamped
prefix has few internal repeats — so **the min-repeat filter incidentally excluded them.**

FR77 was protected by a filter installed for an unrelated reason.

---

## 2. The result strengthens under exclusion

Header excluded (windows starting at position ≥ 24):

| L | literal | non-literal | null | z | near-dup share |
|---:|---:|---:|---:|---:|---:|
| 12 | 2 | 80 | 2.78 | **+22.90** | 22% |
| 13 | 1 | 92 | 2.61 | **+30.82** | 23% |
| 14 | 0 | 107 | 2.94 | **+30.73** | 22% |
| 15 | 0 | 125 | 2.68 | **+39.20** | 22% |
| 16 | 0 | 132 | 2.72 | **+46.44** | 22% |

The z values **rise** (FR77 reported +17.70 to +38.31) because excluding the header
lowers the null more than the observed count.

**Literal isomorphs vanish entirely at L ≥ 14.** The abundance is purely non-literal,
which is the discriminating kind.

---

## 3. Both contaminants removed

Header excluded **and** both near-duplicate partners dropped, leaving six messages:

| L | non-literal | null | z |
|---:|---:|---:|---:|
| 12 | 22 | 1.02 | **+12.18** |
| 14 | 25 | 1.21 | **+12.21** |
| 16 | 26 | 0.89 | **+15.44** |

**Twenty-two long non-literal isomorphs among six ordinary messages, against a null of
one.** That is the irreducible core of the discriminator, and it is strong.

**FR77 survives the full diagnostic. Ciphertext-value feedback remains excluded.**

---

## 4. The diagnostic is not only a way to kill results

Worth stating, because the last several cycles have been corrections. This is the first
retroactive application of FR87's guard, and it returns a **confirmation**.

That matters for calibration. The guard caught FR39, FR45, FR84 and FR87 as artifacts;
applied to the single most load-bearing pooled statistic in the project, it finds the
statistic clean. The tool discriminates rather than merely deflates, which is what
gives its earlier negatives their force.

It also gives the discriminator a cleaner statement than doctrine carries:

> Long non-literal isomorphs are abundant in this corpus **at z ≥ +12 among messages
> that share neither a header nor a near-duplicate relationship**. Ciphertext-value
> feedback crushes such isomorphs; the corpus does not.

---

## 5. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits;
inventory 82.5 CI [73.0, 93.7] via v-channel, 72.8 via header trie; determinacy
threshold 81.2, unresolvable by 51×; progressive premise verified at periods 2–30.
**Isomorph discriminator confirmed at z ≥ +12 with both contaminants removed.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Isomorph abundance | z = +17.7 to +38.3, header never excluded | **z = +22.9 to +46.4 header-excluded; +12.2 to +15.4 with near-dups also removed** |
| Header contamination | unmeasured | **0–7%**, incidentally filtered by the min-repeat rule |
| Literal isomorphs | 2–4 at every length | **zero at L ≥ 14** after header exclusion |
| The discriminator's statement | qualitative | **quantified on contaminant-free messages** |
| FR87's diagnostic | four artifacts caught | **first confirmation** — it discriminates, not just deflates |

---

## 7. Horizon

1. **Continue the retroactive audit.** Remaining pooled statistics that have not had the
   diagnostic: the effective-inventory estimates (partly done — FR80 excluded passages
   by shift, FR82 added the parameter-free within-message channel) and FR54's
   undetermined-glyph rarity result.
2. **Acquire an anchor per component** (FR64 ordering).
3. **The success criterion** (FR82 §7). Unchanged.
