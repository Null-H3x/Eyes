# Field Report 128 — THE WRONG OBJECTIVE FUNCTION: FR127's "BETTER REPAIR" WITHDRAWN

*Artifact: `REPAIR_RANKING.md`. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The question that caught it

FR127 announced a "better repair" — drop East 1@30 + East 1@40 — on the basis
of more relations (494 vs 409) and more coverage (697 vs 686 positions). Asked
**"what reason is there for dropping those?"**, the honest answer was: none.

**I ranked the repair space by relations and coverage. Those are optimisation
criteria, not evidential ones.** Maximising relations selects the repair making
the *strongest claim*, which is the definition of overfitting. It says nothing
about which repair is true.

This is the tenth catch of this shape in the series, and a **new variant**:
not a wrong null (FR42, FR126) nor a reused gauge (FR107) nor a circular
measurement (FR48), but **a wrong objective function.**

---

## 1. The correct criterion

Every repair asserts that the instances it discards are **chance pattern
matches**. That assertion has a price. A class asserting `k` equalities matches
a random window at ~83⁻ᵏ:

| class | L | instances | k | chance/window | expected chance instances |
|---|---:|---:|---:|---:|---:|
| #2+ | 33 | 2 | 7 | 3.7e-14 | 3.8e-11 |
| #C0, #C1, #S | 24–31 | 2 | 6 | 3.1e-12 | 3.2e-09 |
| #1, #2, **#F** | 18–30 | 3–4 | **5** | 2.5e-10 | **2.6e-07** |
| #3+ | 15 | 2 | 4 | 2.1e-08 | 2.2e-05 |
| **#M**, #2⁻, #3 | 9–25 | 3–6 | **3** | 1.7e-06 | **1.8e-03** |
| #M⁻, #4 | 8–14 | 3–7 | 2 | 1.5e-04 | 0.15 |

**`Cost = −log₁₀ P(all dropped instances are chance).`** Lower is better
supported.

---

## 2. The reversal

**East 1@30 is an #F instance — k = 5.** Dropping it asserts that a pattern
arising by chance roughly once in four million corpora is nevertheless a
coincidence. **East 1@68 is #M/#M⁻ at k = 3**; asserting *that* spurious is
about **7,000× more probable.**

| rank | cost | drops | rel | glyphs | eq | coverage |
|---:|---:|---|---:|---:|---:|---:|
| **1** | **5.8** | **East 1@68** | 409 | 57 | 1 | **686 (66.2%)** |
| 2 | 7.7 | East 4@51 | 417 | 56 | 5 | 683 (65.9%) |
| 3 | 9.6 | East 1@68 + West 2@18 | 409 | 57 | 1 | 621 (59.9%) |
| … | | | | | | |
| **32** | **15.4** | **East 1@30 + East 1@40** | 494 | 57 | 1 | 697 (67.3%) |

> **Repair C is rank 1 of 62 by evidential cost, and rank 3 by coverage.
> FR127's "best" is rank 32. It bought eleven extra positions by asserting
> something nearly ten orders of magnitude less likely.**

**FR127's headline is withdrawn.** Repair C is the best-supported repair in the
entire enumerated space, and not narrowly.

---

## 3. What survives from FR127

Three findings, all independent of the bad ranking:

1. **62 viable repairs give 32 distinct readings.** The ambiguity is real and
   FR123–125 did not state it.
2. **Bijectivity and T1 coverage are mutually exclusive** — 0 of 60 pairs
   achieve both. Structural, proven by exhaustion.
3. **`q[36] = q[68]` is forced in every high-coverage repair**, whichever
   instances are dropped. Glyph 36 is East 2's indicator.

And the 32 readings are now **ranked rather than equal**, with the top of the
ranking exactly where FR122–125 already were. The ambiguity is narrower in
practice than FR127 implied: the cheapest reading costs 5.8, the next 7.7, and
everything else ≥ 9.6.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| FR127's "better repair" | claimed | **withdrawn** — rank 32 of 62 |
| Repair ranking criterion | relations / coverage | **evidential cost**, −log₁₀ P(dropped instances are chance) |
| Repair C | best among singles | **best of all 62**, by a factor of ~7,000 over the runner-up class |
| The 32 readings | equally weighted | **ranked**; costs 5.8, 7.7, then ≥9.6 |
| Error taxonomy | wrong null, reused gauge, circular measurement | **+ wrong objective function** |

---

## 5. The lesson, stated for the doctrine

FR48 established the right move: **price what a hypothesis must claim.** It was
available, it is the same method, and I did not apply it — I reached for the
metric that was easiest to compute instead. **Any future comparison of models
or repairs must rank by what each must assert, never by how much each
determines.** A model that explains more by assuming more is not better
supported; it is worse.

---

## 6. Model status

**Repair A**: 384 relations, 56 glyphs, 0 equalities, 44.5%, 17 ratios,
bijective. **Repair C** (rank 1, cost 5.8): 409 relations, 57 glyphs, 1
homophone, 66.2%, drift forced, unique across drifts. 31 further readings at
higher cost. Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **`REPAIR_RANKING.md` should be folded into the acquisition spec** — an
   acquirer needs to know the reading is repair-conditional and which repair is
   cheapest.
2. **`q[36] = q[68]` remains the sharpest external test**: forced by every
   high-coverage repair, so one anchor on either glyph tests the whole
   non-bijective family at once — far better leverage than the eleven-anchor
   programme.
3. **Constructive work should resume from repair C**, which is where it was
   before FR127's detour, now with the ranking to justify it rather than
   accident.
