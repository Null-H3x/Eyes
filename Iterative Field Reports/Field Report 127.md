# Field Report 127 — THE REPAIR SPACE IS THIRTY-TWO WIDE: FR123'S UNIQUENESS WAS THE WRONG UNIQUENESS

*Systematic repair enumeration. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Two reframings before the finding

**CHALLENGE I — linking is not the constraint.** FR126 nominated the 29
unlinked block groups as the next coverage target. Measuring first:

```
positions holding a determined glyph : 777 (75.0%)
largest linked group                 : 686 (66.2%)
lost to LINKING                      :  91
lost to UNDETERMINED GLYPHS          : 259 (25.0%)
```

**Linking is worth at most 91 positions. The ceiling is the 26 undetermined
glyphs**, and FR97 closed that internally. So the better question is which
repair determines the most — a space nobody had enumerated. FR25 examined
pairs and found A and B; FR122 found C by accident.

---

## 1. Systematic enumeration

**Single drops: only 4 of 43 atlas instances build at all**, and they reduce to
two distinct sites (each appears in two classes):

| drop | relations | glyphs | equalities | coverage |
|---|---:|---:|---:|---:|
| **East 1@68** (#M, #M⁻) | 409 | **57** | **1** | 686 (66.2%) |
| East 4@51 (#3, #3+) | 417 | 56 | 5 | 683 (65.9%) |

Repair C is optimal among singles — more glyphs, fewer equalities, more
coverage.

**Pairs keeping East 3@101: 60 build.** And they answer a question that had
never been posed:

```
pairs with ZERO forced equalities AND T1 linked : 0
```

> **Bijectivity and T1 coverage are mutually exclusive.** Keeping the only
> bridge to T1 *requires* accepting at least one homophone. That is a
> structural fact about the corpus, not a choice.

---

## 2. The finding, and it undercuts FR123

**62 viable repairs produce 32 DISTINCT readings.**

| positions | rel | glyphs | eq | T1 | repairs giving it | example |
|---:|---:|---:|---:|---|---:|---|
| **697** | **494** | 57 | 1 | Y | 1 | drop East 1@30 + East 1@40 |
| 689 | 467 | 56 | 5 | Y | 2 | East 5@35 + West 4@53 |
| **686** | 409 | 57 | 1 | Y | 13 | **repair C** (East 1@68) |
| 683 | 417 | 56 | 5 | Y | 16 | East 4@51 |
| 680 | 361 | 57 | 1 | Y | 1 | East 1@68 + West 1@34 |

**A better repair than C exists** — dropping East 1@30 + East 1@40 gives 494
relations and 697 positions at the same cost of one homophone `q[36] = q[68]`.
Audited: builds at all 82 drifts, stable partition [28,14,7,2,2,2,2] = 57
glyphs, single equality set, unique structure across drifts.

**But it DISAGREES with repair C.** On their 673 common positions the equality
structures differ, and neither is a superset of the other.

> **FR123 claimed repair C yields a "unique" structure. That is true across
> DRIFTS and false across REPAIRS.** The 17-way ratio ambiguity was not
> eliminated — it was traded for a 32-way repair ambiguity, and FR123 did not
> notice because it examined only one repair.

---

## 3. Correction to FR122–FR125

| claim | status |
|---|---|
| repair C: 409 rel, 57 glyphs, 1 equality, 686 positions | **confirmed** (FR124, re-confirmed here) |
| repair C's structure unique across drifts | **confirmed** |
| **"repair C gives ONE structure, not 17"** | **misleading** — one per drift, but **32 distinct readings across the repair space** |
| repair C optimal | **only among single drops**; a pair beats it on relations and coverage |
| FR25's fork is A vs B | **62 viable repairs exist**, giving 32 readings |
| linking is the coverage constraint | **wrong** — worth ≤91 positions; undetermined glyphs cost 259 |

The vocabulary results (FR121, FR125) are unaffected in substance — zero hits
is zero hits — but their framing as "tested against the structure" should read
"tested against **one of 32** candidate structures."

---

## 4. What actually survives

Three things, and they are worth separating from the wreckage:

1. **Bijectivity ⟺ no T1.** Proven by exhaustion over the pair space. Any
   reading covering all nine messages accepts at least one homophone.
2. **`q[36] = q[68]` is forced** in every high-coverage repair examined — the
   same homophone appears whichever instances are dropped. Glyph 36 is East 2's
   indicator.
3. **The repair space is enumerable and now enumerated.** 62 repairs, 32
   readings, each with relations, glyphs, equalities and coverage measured.
   That is a map where there was previously an assumption.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Repair space | A, B, AB, C | **62 viable repairs, 32 distinct readings** |
| "Unique structure" (FR123) | across drifts and repairs | **across drifts only** |
| Best repair | C | **East 1@30 + East 1@40** on relations and coverage; C best among singles |
| Bijectivity + T1 | untested | **impossible** — 0 of 60 pairs achieve both |
| Coverage ceiling | linking | **undetermined glyphs**: 777 determined positions is the hard cap |
| `q[36] = q[68]` | repair C artifact | **common to every high-coverage repair** |

---

## 6. Model status

**Repair A**: 384 relations, 56 glyphs, 0 equalities, 44.5%, 17 ratios,
bijective. **32 non-bijective readings** at 66–67% coverage, one homophone,
drift forced, mutually disagreeing. Cumulative: 27.16 billion candidates, zero
survivors.

---

## 7. Horizon

1. **Do not build further on a single repair.** FR123–FR125 did, and the
   artifacts inherit a 32-way ambiguity that was never stated. Any future
   reading artifact must either span the repair space or declare its choice.
2. **The 32 readings are a testable set**, exactly as the 17 ratios were. A
   crib satisfied by exactly one is decisive; `eyehypo.py` extends to this
   directly.
3. **`q[36] = q[68]` is the sharpest external test available.** It is forced by
   every high-coverage repair, and glyph 36 is a message indicator — so a single
   anchor on either glyph tests the entire non-bijective family at once.
