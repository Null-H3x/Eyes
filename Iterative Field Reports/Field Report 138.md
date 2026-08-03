# Field Report 138 — THE FIVE WORKING ASSUMPTIONS, TWO OF THEM TESTED

*Artifact: `WORKING_ASSUMPTIONS.md`. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What was done

Efforts 1–3 document positions already settled by evidence. **Efforts 4 and 5
were testable and had never been measured**, and one of them corrects standing
doctrine.

---

## 1. EFFORT 4 — the dot doctrine is over-conservative by 63%

Dot cells are excluded from every build, so testing them is out-of-sample. If a
dot cell carried co-plaintext, its `q`-difference would equal the alignment's
lettered `w`; chance of matching is 1/83.

```
measurable dot cells with a determined w : 70
   MATCH the lettered w : 44
   expected by chance   : 0.84      z = +47
```

**63% of testable dot cells carry co-plaintext.** FR7's doctrine — *dot cells
are variable interior, the plaintext differs there* — is **wrong about most of
them**.

**But the masking should be kept**, because nothing recoverable is lost:

```
512 dot cells:  233 both glyphs determined  -> redundant, add no relations
                227 one glyph undetermined  -> would recruit, UNTESTABLE
                 52 both undetermined       -> would recruit two, UNTESTABLE
```

All 44 matches come from the 233 redundant cells. The 279 informative ones
cannot be tested for matching **because the model does not determine their
`q`-difference — which is precisely why those glyphs are undetermined.**

FR35's warning holds: a cell that fails to contradict has not been shown to
belong. Greedy recovery would repeat that error.

---

## 2. EFFORT 5 — isomorph survival favours a large alphabet

Heavy homophony destroys isomorphs. Simulating a progressive cipher at
alphabet size `k` against the corpus's 53 / 73 / 93 long isomorph pairs:

```
  k=83  18.2  58.5  144.8      k=60   6.5  12.5   25.8
  k=80  18.2  72.8  107.8      k=56   1.8   6.2   18.2
  k=75  30.8  60.0  117.5      k=50   0.5   1.0    4.5
  k=65  24.2  57.5   93.8      k=30   0.0   0.8    1.0
```

**Below k ≈ 60 the counts collapse an order of magnitude.** At the proven floor
k = 56 the simulation gives 1.8 / 6.2 / 18.2 against 53 / 73 / 93 observed.

**The alphabet is probably ≥ 60, plausibly 70–82.** Weak — the simulation
plants an arbitrary shared head and assigns homophones randomly, so counts are
indicative not calibrated — but it is the **first evidence of any kind that
narrows [56, 82] from below**, and it comes from a mechanism (isomorph
destruction) independent of everything used to derive the floor.

---

## 3. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Dot cells** | variable interior (FR7) | **63% carry co-plaintext**, z = +47 out-of-sample |
| Dot masking | correct | **over-conservative but correct to keep** — nothing recoverable is lost |
| Alphabet range | [56, 82], no internal narrowing possible | **probably ≥60**, plausibly 70–82, on isomorph survival |
| Progressive form | best-supported hypothesis | **established** — sole tested rival refuted (FR137) |
| Repair C | rank 1 of 62 | **adopted** as the working reading |
| `q[36]=q[68]` | forced in high-coverage repairs | **adopted**; alphabet ≤ 82 follows |

---

## 4. Model status

Working position: repair C, one homophone, progressive keystream, dot masking
retained, alphabet 60–82. 409 relations over 57 glyphs; 191-position relative
reading; drift a single parameter. Cumulative: 27.16 billion candidates, zero
survivors.

---

## 5. Horizon

1. **The overdispersion thread is the last unexploited statistic.** Glyph
   frequency is not uniform — chi² = 150.4 on 82 df, **z = +5.34**, variance
   1.86× multinomial. Probably the shared passages, but unverified, and it is
   the only signal in the corpus nobody has chased.
2. **Effort 5 deserves a calibrated version** if the alphabet size matters
   enough — the current simulation is indicative, and a properly calibrated one
   could turn "probably ≥60" into a real bound.
3. **Acquisition unchanged**: one anchor on glyph 36 or 68 adjudicates the
   entire compound position at once.
