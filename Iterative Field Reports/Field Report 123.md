# Field Report 123 — THE REPAIR-C STRUCTURE IS UNIQUE: 686 POSITIONS, ONE READING

*Artifact: `PLAINTEXT_STRUCTURE_C.txt`. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The build

FR122 found repair C — discard East 1@68 only, keep East 3@101 as the sole
bridge linking T1 — buying 20.8 points of coverage for one homophone pair.
This builds its readings.

---

## 1. The result: not 17 candidates, ONE structure

Under repair C the keystream has a **single** drift, because the bridge that
buys the coverage is a T1↔T2 straddling pair and forces `d1 = d2`. So

```
p[t] = A_block + d*(Delta_g - t) = A_block + d*v[t]
p[t] = p[t']  <=>  d*v[t] = d*v[t']  <=>  v[t] = v[t']      (d invertible)
```

**The plaintext equality structure is drift-independent.** Verified identical
at drifts 1, 2, 3, 5, 7, 11, 31, 41, 82.

| | repair A | **repair C** |
|---|---|---|
| candidate readings | 17 | **1** |
| positions | 461 | **686** |
| corpus coverage | 44.5% | **66.2%** |
| messages | 6 | **all 9** |
| relations | 384 | **409** |
| glyphs | 56 | **57** |
| forced equalities | 0 | 1 — `q[36] = q[68]` |

Per-message coverage: East 1 63%, West 1 75%, East 2 67%, West 2 58%,
East 3 66%, West 3 52%, East 4 70%, West 4 75%, East 5 72%.

83 distinct plaintext values, 3,058 equal-pairs.

> **Repair C converts a 17-way ambiguity over 44.5% of the corpus into a single
> determinate structure over 66.2%.** The drift's 82 values remain unknown but
> no longer matter for the equality structure — only for the absolute values.

---

## 2. The artifact shows structure on inspection

```
East 1   abcdef....g.hi.jk..l..mno..pqgrste..uvw.fhxyzAABcqj.k....C.DzwdEFgGHI...
West 1   .bcdef....g.hiQjk..l..mno..R.grstSTDqvw.fhxyzAABcqUVm.W.X.YsZcOeTM.i0jfhxyzA1Bco
```

Two things are visible without any analysis:

- **The E1~W1 shared passage** — `bcdef....g.hi?jk..l..mno..` identical in both,
  the near-duplicate structure appearing directly as identical plaintext.
- **A passage repeating INSIDE West 1** — `fhxyzAAB` at ~position 40 and
  `fhxyzA1Bco` again at ~70. That is #M⁻'s West 1@40 / West 1@70 pair, and it
  is the first time a repeated passage has been visible as plaintext rather
  than inferred from ciphertext patterns.
- **`dd` in East 1 at ~87** — a doubled plaintext value, the shape FR121's
  Finnish vocabulary was hunting for.

---

## 3. What it buys for hypothesis testing

Word-crib power, measured across FR121's fifteen k≥3 candidates:

```
MEAN POWER   repair A 6.3%   ->   repair C 8.4%   (1.3x)
```

Honest: **less than the 5× I projected in FR121.** That projection assumed
coverage alone drives power; it does not. Power depends on *contiguity*, and
repair C adds positions that are still fragmented. The gain is real but modest.

The larger gain is elsewhere: **hypotheses can now be tested against ONE
structure instead of seventeen**, so a hit is decisive rather than
discriminating, and **T1's three messages become testable at all** — they were
entirely dark.

---

## 4. What is being assumed

Repair C is **not** established. It rests on:

- **East 1@68 is spurious.** Supported by arithmetic weight (it carries five of
  the six forced equalities to East 3@101's one), by FR2's structural anomaly,
  and by FR27's embeddedness — though FR110 showed the last is atlas nesting
  and worth nothing.
- **`C` is not strictly bijective.** One homophone pair is accepted. This
  contradicts the standing model and gives up the 17-ratio narrowing, since
  every one of those rejections was an injectivity failure.
- **A single drift.** Forced by the bridge, which resolves FR102's open
  question in the direction of equality.

**Repair A and repair C are alternatives, not refinements of one another.**
A recovered drift ratio ≠ 1 refutes repair C outright.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Candidate readings | 17 (repair A) | **1** under repair C — structure is drift-independent |
| Best coverage | 44.5%, six messages | **66.2%, all nine** |
| T1 readability | dark | **62–75% per message** |
| Word-crib power | 6.3% | 8.4% (1.3×, not the 5× projected) |
| Shared passages | inferred from ciphertext patterns | **visible directly as plaintext** |
| Drift equality | open (FR102) | **forced** under repair C |

---

## 6. Model status

Two live models. **Repair A**: 384 relations, 56 glyphs, 17 ratios, 44.5%
linked coverage, bijective. **Repair C**: 409 relations, 57 glyphs, one drift,
66.2% linked coverage, one homophone. Both conditional on the progressive form
(FR118). Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon (constructive)

1. **Re-run the vocabulary batch against the repair-C structure.** One target
   instead of seventeen, T1 now testable, and a hit would be decisive. Directly
   executable and the obvious next build.
2. **The visible West 1 internal repeat is a crib target.** A passage occurring
   twice in one message at known offsets constrains the plaintext at both, and
   any word hypothesis placed at one is automatically tested at the other.
3. **Repair A vs repair C is now decidable by acquisition** — a ratio ≠ 1
   refutes C, a ratio of 1 refutes neither but favours it. The acquisition spec
   should record this alongside the existing fork test.
