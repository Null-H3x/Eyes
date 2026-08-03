# Field Report 104 — INJECTIVITY DISCRIMINATES THE DRIFT RATIO: 17 OF 82

*Instruments: `eyescale.py` (7/7 gate, voided by its own pre-registration),*
*then the restored canonical machinery (`eyeaudit.py`, 11/11). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — two of FR103's three horizon items were not live

**Item 2 (audit the pool for the #M⁻ failure mode) is already answered** by
FR103's own leave-one-out table: dropping #M⁻ alone gives zero forced-equal
pairs across the remaining alignments, so every other class is jointly
consistent. Re-running would re-derive a published table. *Retired on
inspection — ninth horizon item to die this way.*

**Item 3 (search for a T1 cross-triplet alignment)** has the highest payoff and
the lowest prior: FR31, FR34 and FR35 each closed the internal-passage search,
FR35 scanning every message pair with free w. Re-running is re-covering swept
ground, and "the answer would be valuable" is not a new reason. *Deferred, not
retired.*

**Item 1 selected**, and sharpened: component structure and the Δ *ratios* come
from drift-free relations, so the drift enters only as **scale**. The question
is not "how many drifts" but **how many independent scales acquisition must
buy** — which is what FR54 priced without knowing it.

---

## 1. SELF-CORRECTION — my pre-registration voided my own first answer

`eyescale.py` built the two-drift system from `corpus.json` + `atlas.json`,
compared one-drift against two-drift anchor yield, and produced a tidy
"+1 anchor" answer.

**R2 fired.** The pre-registered check — *the one-drift configuration must
reproduce FR54's headline (2 anchors → 25 glyphs) or the run is void* —
returned **2 glyphs, not 25**. The comparison was discarded unpublished.

Diagnosis, by progressive relaxation: even with the drift **and all nine bases**
pinned, one anchor determined exactly one glyph and nothing propagated. The
cause is coverage:

```
atlas instance-pair pool, lettered cells : 39 alignments, 299 cells
distinct glyphs touched                  : 49  (41 in the skeleton)
skeleton glyphs NEVER touched            :  5  (including glyphs 0 and 1)
distinct skeleton glyph-pairs related    : 64
skeleton's actual relation count         : 384
```

**The skeleton cannot be reconstructed from `corpus.json` + `atlas.json`
alone.** It rests on the sound-rows machinery, the strict tier, and the FR32/33
passage — 83 pool pairs, 67 after repair A, against my 39.

---

## 2. The environment could not reproduce its own model — now it can

FR46 performed an end-to-end reproduction audit and passed 11/11, so the
machinery existed. It was **absent from the Iterative-3 archive**: `eyeaudit.py`
imports a chain reaching `iso_relax`, which was never exported.

Seven modules fetched from `null-h3x/eyes` (`eyeforward/`, `noita_eye_core/`):
`iso_relax`, `plantlab`, `pyry_gate`, `support_min`, `isomorph`,
`chain_models`, `chain_extract`. With the corpus and atlas placed where the
loader expects them, **`eyeaudit.py` now passes 11/11 in this environment**:

```
baseline guard 22/19/16 · sound pool 83 · repair A 83->67 · E4/E5 merge admissible
determined relations 384 · injectivity 0 · glyphs 56 · components [25,11,7,3,2,2,2,2,2]
exposure 74.1% · gauge ladder (0,0,82) · both openings contradict
```

**Operational finding worth carrying:** the archive shipped 96 reports and ~90
instruments but not the dependency closure needed to rebuild the skeleton. Any
future environment reconstitution must verify `eyeaudit.py` runs, not merely
that files are present.

---

## 3. The result: injectivity constrains the ratio

With the canonical machinery, the drift enters exactly once per pool pair as
`rhs = drift * (p2 - p1)`. Parameterising it per triplet group — `d1` for
T1-internal pairs, `d2` for everything else — and rebuilding:

**Component structure is ratio-invariant.** At every tested `(d1, d2)`, equal or
not: 384 relations, 56 glyphs, components [25, 11, 7, 3, 2, 2, 2, 2, 2], zero
contradictions. FR54's per-component yield is therefore **unchanged** by the
two-drift model.

**But injectivity is not ratio-invariant.** Scanning all 82 ratios with `d2 = 1`
fixed by the scale gauge:

| outcome | count |
|---|---:|
| contradictory | 0 |
| consistent but **injectivity fails** | **65** |
| clean | **17** |

```
surviving ratios d1/d2 : 1, 8, 9, 15, 22, 28, 35, 40, 48, 51, 53, 55,
                         74, 76, 77, 78, 82
```

**Equality (ratio 1) survives**, as it must. Sixteen unequal ratios survive with
it, including 82 ≡ −1.

**Why this is new.** FR53's P1 proves packing is invariant under scaling and
therefore carries **zero drift information** — permanently. That proof is about
a **single global scale**: multiplying everything by `d` preserves disjointness.
A **ratio between two independent scales is not a global scaling**, so P1 does
not cover it, and injectivity becomes informative exactly where it was proved
useless before. **This is the first new internal constraint on the drift the
series has found since FR27, and it exists only because the model became a
two-parameter family.**

---

## 4. What acquisition now costs

The two-drift model is far cheaper than FR103 feared:

- **FR54's ordering stands.** Components are identical at every surviving ratio,
  so the per-component anchor yield — 2 anchors in component 1 → 25 glyphs /
  31.2%, then one per component → 56 glyphs / 74.1% — is unaffected.
- **The extra cost is a 1-of-17 ambiguity, not 1-of-82.** After the FR54
  programme, an unresolved ratio leaves **seventeen** candidate readings of the
  corpus — trivially enumerable, and checkable against any further evidence.
- **One anchor in the other drift group collapses it.** A pin whose evidence
  sits in T1 and one whose evidence sits in T2/T3 fix both scales.

So FR103's "one more independent anchor than FR54 priced" is correct in form and
mild in size: **the programme is FR54's plus one cross-group anchor, or FR54's
plus a seventeen-way enumeration.**

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Drift ratio `d1/d2`** | unconstrained, 82 values (FR103) | **17 of 82** survive injectivity; equality among them |
| **FR53 P1 scope** | "packing carries zero drift information, permanently" | **true for a single global scale only**; a ratio between two scales is discriminated by injectivity |
| Component structure | derived at one drift | **ratio-invariant** — identical at every tested `(d1,d2)` |
| FR54 anchor ordering | conditional on equality (FR103) | **stands**; extra cost is one cross-group anchor or a 17-way enumeration |
| Archive reproducibility | assumed | **was broken** — `iso_relax` chain absent; now restored, `eyeaudit.py` 11/11 |
| Pool reconstructibility | implicitly from corpus+atlas | **impossible** — 5 skeleton glyphs untouched, 64 pairs vs 384 relations |

---

## 6. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; components
[25, 11, 7, 3, 2, 2, 2, 2, 2]; alphabet [56, 83] floor 56. **Drift: two
parameters, ratio narrowed to 17 candidates.** Cumulative: 27.16 billion
candidates, zero survivors.

---

## 7. Horizon

1. **Characterise the 17 surviving ratios.** They are not obviously structured
   (not closed under negation or inversion). If they share an arithmetic
   property, that is a further constraint; if they do not, the enumeration
   stands at 17 and should be carried as such.
2. **Re-run FR54's ordering on the canonical machinery under two drifts**, now
   that the environment can. This cycle established the components are
   ratio-invariant, so the ordering should survive intact — but it was priced
   under one drift and deserves the direct check rather than the inference.
3. **The deferred T1 bridge search** (FR103 item 3) is worth more after this
   cycle, not less: it would collapse 17 ratios to 1. It remains swept ground,
   so it needs a genuinely new search method rather than a re-run.
