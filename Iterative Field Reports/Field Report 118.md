# Field Report 118 — THE MODEL HAS A RIVAL, AND THE SKELETON CANNOT SEE IT

*Instrument: `eyerival.py` (4/4 gate). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. The gap this closes

Every report since FR38 has cited the same headline evidence: remove an entire
isomorph class, rebuild, and the model predicts its own held-out cells **41/41**
against a 1.5% chance rate, with a planted-spurious class scoring **0/23**. I
have repeatedly qualified it with the same caveat — *"tested against nulls, not
against rivals"* — and never acted on it.

The rival was in the community documentation the whole time. **Pyry's own
demonstration of isomorphs uses an Alberti cipher whose rings rotate by an
amount depending on the previous plaintext character** — a plaintext autokey.
Measured against the corpus:

```
isomorph pairs      L=12   L=14   L=16
real corpus           53     73     93
progressive            0     48    138
plaintext autokey     35     65    181
ciphertext feedback    1      3      5
```

**Plaintext autokey produces long isomorphs as readily as the progressive
model.** The argument that kills ciphertext feedback — FR-era doctrine's
"ciphertext-value feedback crushes long isomorphs" — does not touch it.

---

## 1. CHALLENGE I — the skeleton is model-agnostic, by proof

Autokey: `K[t] = K[0] + Σ p[j]`. For two instances of a **shared** passage the
plaintext inside is identical, so the accumulated key advances identically:

```
K1[s1+i] - K2[s2+i]  =  K1[s1] - K2[s2]   = constant in i
```

The progressive model gives `d·(s1−s2)` — also constant in `i`.

> **Both models predict exactly the same thing across a shared passage.
> All 384 relations are model-agnostic. The isomorph evidence cannot
> discriminate them, and never could.**

That is why a hundred cycles never separated them: the discriminating question
was never asked, and the evidence everyone was looking at is blind to it.

**Where they differ is what the constant IS:**

| model | offset for an alignment |
|---|---|
| progressive | `base_diff + d·(s1−s2)` — **affine in the shift, one slope for the whole corpus** |
| autokey | `base_diff + (K1[s1] − K2[s2])` — depends on plaintext accumulated *before* each instance; unrelated across alignments |

---

## 2. Head to head

Both built on the same repaired pool:

| | relations | glyphs | contradictions |
|---|---:|---:|---:|
| **progressive** (one drift) | **384** | 56 | 0 |
| **autokey** (free offset per alignment) | **0** | 49 | 0 |

**Autokey determines nothing.** Every one of the 384 relations is a consequence
of the progressive assumption, not of the corpus. Under autokey the isomorph
evidence constrains the alphabet not at all — each alignment's offset absorbs
whatever it needs.

This cuts both ways and the report is about both edges.

---

## 3. What the progressive model risks, and wins

Alignment structure of the 67 repaired pool pairs:

```
message pairs with >=1 alignment  : 14
message pairs with >=2 alignments :  8
alignments beyond the first       : 53
   of those, at a DIFFERENT shift :  7
```

Alignments of one pair at the *same* shift predict the same offset trivially.
**Only the 7 at different shifts test the affine law.** Each is a free
prediction the progressive model could fail and autokey structurally cannot.

All seven hold, with zero contradictions. Fitting the single drift consumes one
of them, leaving **six free tests**: odds under a model that does not predict
them, `83⁻⁶ ≈ 1.2 × 10⁻¹¹`.

**That is genuine, non-circular evidence for the progressive form** — the first
in the series that discriminates against a specific alternative rather than
against noise.

---

## 4. The asymmetry that cuts the other way

Applying each model to the **unrepaired** 83-pair pool:

| | unrepaired pool |
|---|---|
| **progressive** | **CONTRADICTORY at every drift** — must discard East 3@101 and East 1@68 |
| **autokey** | **0 contradictions. No repair needed.** |

> **The progressive model buys its 384 relations by discarding two
> well-supported isomorph instances. Autokey explains the entire corpus as it
> stands, and determines nothing.**

This is the classic fit-versus-complexity trade, and it reframes FR25's repair
fork completely. **The fork is not a defect in the pool — it is the price of
the progressive assumption.** FR109 reopened it and FR110 found it unsupported;
FR118 shows *why* it exists at all. Under autokey there is no fork, because
there is nothing to repair.

---

## 5. The verdict, stated carefully

**Neither model is refuted, and the choice is a judgement about what evidence
is worth.**

- **For progressive:** six free predictions at `1.2 × 10⁻¹¹`, and 384 relations
  covering 74.1% of the corpus.
- **For autokey:** it needs no repair, discards nothing, and is the cipher the
  community's own demonstration uses.
- **Against autokey:** it explains the corpus by explaining nothing — zero
  determined relations. A model that fits everything and predicts nothing is
  weak in the way that matters.
- **Against progressive:** its entire content rests on an assumption the
  isomorph evidence cannot test, and it must discard evidence to survive.

**I judge progressive better supported** — six independent predictions at
1e-11 outweigh the cost of two discarded instances, and FR56/FR91's exclusion
of periodicity plus FR102's exclusion of polynomial and exponential bends
constrain the keystream in ways autokey does not accommodate naturally. **But
this is now a judgement between two live models, not a settled fact**, and
every downstream figure inherits that.

---

## 6. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Plaintext autokey** | never considered | **live rival**; produces long isomorphs like the corpus |
| "Ciphertext feedback excluded" | read as excluding key-feedback generally | **excludes ciphertext feedback only**; plaintext autokey untouched |
| The 384 relations | corpus evidence | **consequences of the progressive assumption**; autokey determines 0 |
| Isomorph evidence | the model's foundation | **model-agnostic by proof**; cannot discriminate progressive from autokey |
| Discriminating evidence | none identified | **7 different-shift alignments**, 6 free after fitting the drift, `83⁻⁶` |
| FR25's repair fork | a defect in the pool | **the price of the progressive assumption**; autokey needs no repair |
| Model status | supported | **better supported than its one tested rival**, not established |

---

## 7. Model status

Unchanged in content: 384 relations over 56 glyphs; injectivity clean at 17
ratios; exposure 74.1%. Changed in standing: **conditional on the progressive
form, which is now known to have a live alternative that the corpus's isomorph
evidence cannot rule out.** Cumulative: 27.16 billion candidates, zero
survivors.

---

## 8. Horizon

1. **Fit autokey properly and compare out-of-sample.** This cycle gave autokey
   the weakest possible form — a free constant per alignment. A *specific*
   autokey (cumulative plaintext sum, or `K[t] = K[t−1] + p[t−1]`) makes real
   predictions and could be run through FR38's held-out class test head to head
   with progressive. That is the honest version of this comparison and it is
   internally executable.
2. **The 7 different-shift alignments deserve individual scrutiny.** They now
   carry the entire discriminating weight between two models, and no cycle has
   ever audited them individually the way FR15 audited the classes.
3. **A crib settles it.** Progressive and autokey predict different plaintexts
   from the same ciphertext; fifteen tokens would separate them immediately,
   as they separate everything else.
