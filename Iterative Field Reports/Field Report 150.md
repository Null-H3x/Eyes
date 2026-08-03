# Field Report 150 — THREE CRACKS TESTED: TWO CLOSE, ONE OPENS WIDE

*July 2026. Cycle: EYESPIRAL-C.*

---

## CRACK A — does the class enumeration iterate? **CLOSED**

The 19 informative classes were found against **repair A's** skeleton. A richer
skeleton could make more of the remaining 176 informative. Re-running against
the extended skeleton:

```
newly INFORMATIVE : 0
still redundant   : 128
contradictory     : 48
```

**The enumeration has converged.** The 19 are the complete set; no iteration is
needed.

---

## CRACK B — are the repairs still needed? **CLOSED, with a finding**

```
full pool + 19 classes : CONTRADICTORY  -- a repair is still required
drop East 1@68 only    : 794 rel, 61 glyphs, 8 eq
drop East 3@101 only   : CONTRADICTORY
```

Dropping East 1@68 alone reproduces the extended skeleton **exactly**.

> **East 3@101 is now inert.** Keeping or dropping it changes nothing, because
> the new bridges supersede the one it provided. The instance that FR25's
> repair fork, FR47, FR48, FR109–111 and FR122 were all organised around **no
> longer matters.**

The extended skeleton is properly described as **repair C plus 19 classes**.

---

## CRACK C — the 48 contradictory classes. **OPEN, and the widest yet**

k-distribution: `{2: 15, 3: 29, 4: 4}` — these are **not** weak. Forty of the
48 have surprise ≥ 1.70, the level of #M⁻, an atlas member the model relies on.

**Fifteen are explained.** FR29/FR33 read the T1 opening (1–24) and T3 opening
(1–20) as **stamped headers** rather than encrypted shared plaintext, so a class
overlapping an opening *must* contradict. The model predicts those.

**Thirty-three are not:**

```
surprise   L  k inst  instances
    3.59  18  3    6  E1@32,E1@60,W1@32,W1@62,E2@37,E2@72
    3.58  16  3    6  E1@34,E1@62,W1@34,W1@64,E2@39,E2@74
    3.30  20  3    3  E1@58,W1@60,E2@70
```

**Thirty of the 33 body contradictions carry surprise ≥ 1.70.** The strongest
run at 3.59 — comparable to #M (3.55) and #2⁻ (3.45), both atlas members.

> **Thirty well-attested isomorph classes in the message bodies contradict the
> model.** They are not chance: at k=3 the expected chance instance count is
> 0.002 corpus-wide, and several have six instances.

---

## What this means

Three readings, and I cannot yet separate them:

1. **They are genuine and the model is wrong somewhere** — the most serious
   possibility, and it would be localised, since 794 relations survive.
2. **The stamped-header doctrine extends further than FR29/FR33 established.**
   Every strong body contradiction sits in East 1 / West 1 / East 2 — the T1
   triplet whose opening is already read as literal. If literal material runs
   past position 24, these resolve exactly as the opening ones do.
3. **Repair A's discarded instances were the wrong ones.** These classes overlap
   the region around East 1@60–68 and West 1@62–70, which is precisely where
   the repair fork has always fought.

Reading 2 is the cheapest to test and would explain all thirty at once.

---

## Doctrine changes

| item | prior status | status now |
|---|---|---|
| Class enumeration | one pass | **converged** — 0 newly informative on iteration |
| East 3@101 | the sole T1 bridge, load-bearing since FR25 | **INERT** — keep or drop, nothing changes |
| Extended skeleton | "repair A + 19" | **"repair C + 19"** — same result, fewer assumptions |
| The 48 contradictions | unexamined | **15 predicted (openings), 33 not, 30 of those strong** |
| Model completeness | assumed | **30 well-attested body classes contradict it** |

---

## Model status

Extended skeleton unchanged in content: 794 relations, 61 glyphs, 8 homophones,
79.1% exposure, 435-position reading, 0 conflicts, 6 anchors. **But it now has a
known tension it did not have an hour ago.** Cumulative: 27.16 billion
candidates, zero survivors.

---

## Horizon

1. **Test whether the stamped-header region extends past position 24 in T1.**
   All 30 strong body contradictions live in East 1 / West 1 / East 2. If
   literal material runs further than FR29/FR33 assumed, every one resolves.
   This is the cheapest test and the highest payoff.
2. **If it does not, the model is wrong somewhere localised**, and these 30
   classes say where to look.
3. **Artifact rebuild remains pending** — and should now wait until this is
   settled.
