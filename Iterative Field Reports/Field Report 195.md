# Field Report 195 — THE BASE VECTOR IS COMPLETE, EVERY SIMPLE LAW IS REFUTED, AND THE SIXTH DRIFT ROUTE CLOSES LIKE THE FIRST FIVE

*July 2026. Cycle: EYESPIRAL-C. Instrument: `eyelaw.py` (8/8 gate).
Executes FR194's L-1/L-2/L-3. Expectation framing per principal: finding >
breakthrough > solution by likelihood; this cycle landed in the first bucket,
with one suggestive residue and one durable capability restored.*

---

## 0. Negatives first

**The held-out value refuted the pattern's simplest law before anything else
ran.** FR194's feasibility check, done on the eight published base values,
surfaced a per-triplet structure whose most natural law — West offsets are
per-triplet constants — predicted `b[W2] = b[W3] = 23` (ladder variants 22/24).
The ninth value, recovered this cycle, is **39**. All three predictions
refuted. Logged as a genuine held-out score: the pattern was published (FR194
reply) before W2 was recovered.

**All thirteen pre-registered laws are refuted at both tiers.** No simple
corpus-internal law generates the bases or the indicator plaintexts, and the
drift-pinning tier died with them. FR166's assumption 3 — parked as "an
observation, not a test" for 28 cycles — is now retired by measurement.

---

## 1. The enabler: E-B fixed live, and the machinery runs

The nine missing files (seven-module `iso_relax` closure + `corpus.json` +
`isomorph_atlas.json`) were fetched from `null-h3x/eyes` and wired to the
loader's expected paths. **`eyeaudit.py` passes 11/11 from the raw corpus in
this environment** — every certified figure reproduces (384/56/0, components
[25,11,7,3,2,2,2,2,2], 74.1%, gauge ladder, both openings contradict).
`eyebase.py`'s own gates also pass, and corpus.json independently confirms
FR192's indicator values, all nine lengths, and the stamped-header uniformity
(`c[m][1]` identical across all nine — which excludes header-value laws from
the catalog on data rather than judgment).

`fetch_closure.sh` ships with this report so the archive self-heals and E6's
guard ("the audit must RUN") is enforced at packaging.

---

## 2. The ninth value, and the complete vector

`b[W2] − b[E1] = 39` comes from FR178's forced-difference column, which
validates against independently known values at both checkable rows
(E2−E1 = 77 ✓, E3−E1 = 52 ✓) and whose sign convention was the *fixed* side of
FR178's self-diagnosing error. Single-sourced, flagged for canonical
re-extraction on the extended builder (horizon item 1). Everything else is
double-sourced or closure-checked (`eyelaw.py` gate G6 reproduces all nine
published differences).

**The full per-message offset vector, drift-1 units, gauge `b[E1] = 0` —
published as a vector for the first time:**

```
         T1                    T2                    T3
E1   0    W1   0    E2  77  |  W2  39   E3  52   W3  23  |  E4  53   W4  24   E5  53
```

Structure visible in it (all values scale with the true drift `d`):

```
E1 = W1               E4 = E5                    two exact equalities
E3 − W3 = 29          E4 − W4 = 29               partner offset repeats, T2/T3
E4 − E3 = 1           W4 − W3 = 1                parallel +1 steps, T2 -> T3
E2 = 77, W2 = 39                                 outside every pattern
```

---

## 3. The sweep — thirteen laws, two tiers, all dead

Pre-registered catalog and thresholds are in `eyelaw.py`'s header; gates 8/8
(planted law found uniquely; 0/500 false hits on shuffled-`f`; planted `d=37`
recovered exactly; one corrupted value kills a law; statistic separates plant
from uniform; data reproduces the published record).

**Tier 1 — `b_m = ρ·f(m) + c`, 36 pairs (a hit is real at ~83⁻ᵏ):**

| law | verdict |
|---|---|
| canonical index / East-first index | REFUTED — 26 / 29 distinct ρ |
| message length | REFUTED — 27 distinct ρ |
| cumulative offset (continuous keystream) | REFUTED — 29 distinct ρ |
| indicator glyph value `c0` | REFUTED — 28 distinct ρ |
| triplet index / E-W flag / slot-in-triplet | REFUTED — zero-Δf pairs with nonzero Δb |

**Tier 2 — `b_true = f` exactly (a hit pins the drift):** length, cumulative,
`c0`, index — **all REFUTED**, each dying instantly on the forced equalities
(`E1=W1`, `E4=E5`) against differing `f`.

**Indicators, `p0 = ρ·g(m) + c`, 10 pairs:** `c0`, length, both index
orderings, and **the L-3 joint law `p0 ~ b`** — REFUTED, 8–10 distinct ρ each.
Tier-2 self-reference (`p0 = c0`, `p0 = length`) — REFUTED, 10 distinct `d`.

> **This was the sixth and last identified internal route to the drift, and it
> closes the way the other five did — by a specific named test, not fatigue.**
> FR191's ledger stands corrected upward by one: six routes, six deaths
> (FR30, FR36, FR53, invariant-core affine, keyword-720, and this sweep).

---

## 4. The residue — priced, suggestive, characterized

Generic structure statistics on the complete vector, against 10⁶ iid-uniform
9-vectors (statistic declared in the pre-registration block; the post-hoc
caveat — the pattern was noticed on 8 of 9 values first — travels with it):

```
S1  distinct folded diffs   D = 16 of 36    raw p = 1.34e-2   x2 Bonf = 2.7e-2   SUGGESTIVE
S2  zero diffs              Z = 2           raw p = 5.59e-2   x2 Bonf = 1.1e-1   NULL
```

Under the declared bands: **not established, not nothing.** What survives is
exactly the block in §2 — two forced equalities, a repeated partner offset of
`29d` across T2/T3, and matched `+1d` steps across the T2→T3 boundary, with E2
and W2 outside every candidate law. Standing constraint for any future
proposal: **a base-generation story must reproduce those six relations and
accommodate 77 and 39, or it is not a story about this corpus.** Per FR35's
rule, no piecewise law was fitted to the residue — with all nine values
consumed, fitting would be description, not test. The magnitudes `{29d, d}`
become interpretable the day anything pins `d`; until then the residue is an
observation with a price tag instead of a parked one.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| FR166 assumption 3 (±29 clustering) | "an observation, not a test", parked | **retired by measurement** — no simple law; residue priced at 2.7e-2, characterized in §2 |
| Internal drift routes | "all five dead" (FR191) | **six named, six dead** — magnitude-law sweep closed at both tiers |
| L-3 joint law (`p0 ~ b`) | untested (FR194) | **refuted** — 10 distinct ρ |
| The base vector | 36 diffs used as graph edges (FR178), never published as a vector | **complete 9-vector on record**, W2 = 39 (single-sourced, flagged) |
| Indicator self-reference | untested beyond numberings (FR192) | **refuted** (`p0 = c0`, `p0 = length`, both tiers) |
| E-B (archive cannot rebuild) | verified failing (FR194) | **fixed live** — closure fetched, `eyeaudit.py` 11/11; `fetch_closure.sh` ships |
| Continuous-keystream hypothesis | never explicitly tested | **refuted** (F4, both tiers) — messages are independently keyed, confirming the per-message reset |

---

## 6. Model status

Unchanged: 794 relations, 61 glyphs, 8 homophones, one reading, five fragments
= five components, 819 positions (79.1%), Quagmire II with a progressive key.
**Plus: the complete per-message offset vector `b` on record, every simple
generation law for it refuted, and the residual structure priced.** Cumulative:
27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **Canonically re-extract the 36 base differences** on the extended builder
   (repo-side) to double-source W2 = 39. One number, one run; everything in §3
   is robust to it except the exact W2 rows.
2. **§3.1 uniqueness certification** (FR194 priority 1) remains queued for the
   Threadripper — `eyemax` atlas-mandatory at the FR162 standard.
3. **Acquisition, with FR194's E-A correction applied:** two indicator values
   (not one), or the 8-token crib at East 3 105–112, or the `q[36]/q[68]`
   pair. The internal game is now closed at six-of-six routes; the residue in
   §4 is the one thing an external pin would retroactively explain for free.
4. **Do not fit the residue.** The next legitimate test of §4's structure is
   an anchored drift, not another statistic.
