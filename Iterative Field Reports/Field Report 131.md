# Field Report 131 — THE ARTIFACTS WERE BUILT ON THE WRONG QUANTITY

*Major self-correction. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What went wrong

The model is

```
p[t] = A_block + v[t],      v[t] = Delta_g - d*t,
A_block = base_component - b_message
```

**Every artifact I have shipped was built from `v` alone. `A_block` was never
computed.** FR119's `CANDIDATE_READINGS.txt`, FR123's
`PLAINTEXT_STRUCTURE_C.txt`, FR129's consensus pairs, FR130's doubled-site
targets — all of them.

- **Within a block**, `p` and `v` differ by one constant, so the equality
  structure is identical. **Those results are sound.**
- **Across blocks**, each has its own `A_block`. Comparing `v` across blocks
  compares the wrong quantity.

**A second, compounding error:** when I finally did build the linking edges, I
used **all** alignment cells including dots. FR7's sound-rows doctrine says dot
cells are *variable interior* — the plaintext **differs** there. Using them as
co-plaintext edges is invalid.

---

## 1. How it surfaced

This cycle asked how much of the plaintext is repeated content and reported
**26 "novel" shared runs**, including a striking one: *all nine messages share
plaintext at positions 1–3.*

Checking it: **positions 1 and 2 carry glyph 66 and glyph 5 in every message.**
Identical ciphertext at identical `t` forces identical `v` — trivially, and
regardless of the bases. The "discovery" was that the same glyph is the same
glyph.

**This is the FR114 error in a new place** — there, knowing a plaintext token
gives `q` minus an unknown offset; here, `v` is `p` minus an unknown offset. I
diagnosed it correctly in FR114 and did not recognise it when I built on `v`
five cycles later.

---

## 2. The corrected numbers

Solving `A_block` by propagating `A_1 − A_2 = v[B] − v[A]` along **lettered
cells only**:

| edge source | edges | conflicts | largest group |
|---|---:|---:|---:|
| all cells (what I did) | 659 | **560** | 686 positions |
| **lettered cells only** | 397 | **0** | **191 positions** |

The 560 conflicts are the dot cells asserting co-plaintext where the doctrine
says the plaintext varies. With them removed the system is **perfectly
consistent** — and much smaller.

| pool | positions with determined glyph | **TRUE relative-plaintext group** | messages |
|---|---:|---:|---|
| repair A | 768 | **108 (10.4%)** | East 4, East 5, West 4 |
| repair C | 777 | **191 (18.4%)** | 7 of 9 |
| R2 (E4@51) | 767 | **192 (18.5%)** | 7 of 9 |

> **Claimed: 461 positions (44.5%) for repair A, 686 (66.2%) for repair C.
> Actual: 108 (10.4%) and 191 (18.4%).**

The earlier figures counted *positions holding a determined glyph* — which is a
real quantity, and is what FR46/FR54's "74.1% exposure" means — but it is **not
the same as positions whose plaintext is determined relative to one another**.
I conflated them.

---

## 3. What survives

**The model is untouched.** 384/409 relations, 56/57 glyphs, the component
structure, the repair ranking, the drift analysis, the two-reading fork, the
17 ratios — none of that used `A_block` and none of it is affected.

**Within-block results survive.** FR126's cross-block coincidence test used the
*correct* null (randomising block constants) and its withdrawal stands. FR129's
16 robust crib targets are all **within one message**; whether they survive
depends on whether both positions share a block, which is now checkable and was
not checked.

**What must be rebuilt:** every cross-block claim in FR119, FR123, FR129, FR130
— including the "unique structure" framing, the 98.76% agreement figure, and
the four doubled-letter sites.

**FR130's negative survives regardless**: it tested 46 informative placements
and found zero fits, at a chance expectation of 0.48. A shrunken artifact makes
that test smaller, not wrong.

---

## 4. The taxonomy, and the failure of the guard

Eleven catches now, and this is the second time the **same** error appeared:

```
FR114  a plaintext token gives q minus an unknown message offset
FR131  v is p minus an unknown block offset          <- same shape
```

The guard that should have caught it — *ask what the null is allowed to vary,
and check it is exactly the unknown quantity* — is stated in FR126 and I did
not apply it to my own artifact construction. **A rule applied only to
statistics and not to constructions is half a rule.**

**New standing check:** any artifact asserting a relation between two
positions must name the parameters that relation depends on, and confirm each
is either determined or gauged. `v` depends on `A_block`; that was never
stated.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| FR119 "461 positions, 44.5%" | shipped | **108 positions, 10.4%** |
| FR123 "686 positions, 66.2%" | shipped | **191 positions, 18.4%** |
| FR123 "unique structure" | claimed | **must be rebuilt** on `p`, not `v` |
| FR129 "98.76% agreement" | claimed | **must be recomputed** |
| Linking edges | all alignment cells | **lettered cells only** — dots are variable interior |
| A_block | never computed | **solvable and consistent** — 0 conflicts on lettered cells |
| "exposure" vs "relative-plaintext coverage" | conflated | **distinct**: 74.1% vs 18.4% |

---

## 6. Model status

Unchanged in every structural respect. **Relative-plaintext coverage: 191
positions (18.4%) under repair C**, 108 (10.4%) under repair A, across 7 of 9
messages. Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

1. **Rebuild the reading artifact on `p`.** 191 positions with zero conflicts
   is a smaller but *correct* object, and it is the first genuinely valid
   relative decryption the project has produced.
2. **Recheck FR129's 16 crib targets** — each needs both positions in one
   block, or an `A_block` link, to be meaningful.
3. **Re-audit FR122–FR130 against the new standing check.** The structural
   findings look safe; every positional claim needs the parameter list stated.
