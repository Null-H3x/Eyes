# Field Report 79 — A SIGN ERROR IN THE FOUNDATION, AND THE CONCLUSION SURVIVES IT

*Instrument: `eyesign2` (built on `eyegeom`). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — where else does the convention appear?

FR78 established `w(m1→m2) = (base_2 − base_1)/drift` with 6/6 empirical confirmation,
and found FR43 had used the opposite sign. The obvious follow-up: **where else?**

It appears in FR39. Doctrine records its coincidence condition as *"drift·(v−v′) =
base_m1 − base_m2 = drift·w, hence v − v′ = w."* Deriving from the confirmed
convention:

```
p1[t] = base_C - base_1 + drift*v1[t]
p2[t'] = base_C - base_2 + drift*v2[t']
coincidence  =>  drift*(v1 - v2) = base_1 - base_2 = -drift*w

              v1 - v2 = -w        NOT  +w
```

**FR39's stated condition has the opposite sign.** And FR39 is the foundation of the
"inventory > 60" result driving FR46, FR57, FR66 and FR72. My own FR57 re-audit
inherited the same convention.

---

## 1. The sign is confirmed, and the error is real

Scanning all 83 residues for each message pair:

| pair | w | −w | peak at | count at +w | count at −w | flat |
|---|---:|---:|---:|---:|---:|---:|
| West 1 / East 2 | 77 | 6 | **6** | 17 | **58** | 24.6 |
| East 4 / West 4 | 54 | 29 | **29** | 21 | **50** | 21.9 |
| West 4 / East 5 | 29 | 54 | **54** | 21 | **38** | 22.1 |
| East 3 / West 3 | 54 | 29 | 72 | 25 | 25 | 25.4 |

**Every peak sits at −w.** Under the geometry-preserving null (FR42's within-block
permutation, 1,500 draws):

```
+w  (FR39 convention)      obs 112   null 113.1   z = -0.10
-w  (confirmed convention) obs 203   null 118.5   z = +7.89
```

The +w figure reproduces FR39's published z = −0.56. **FR39 measured at a residue
where nothing lives.**

Corroboration that the sign is right, not merely different: the dominant shifts of the
−w coincidences are **+5, +5, +3, −1** for E1/E2, W1/E2, E4/W4, W4/E5 — matching
FR32's independently discovered passage shifts exactly.

---

## 2. And the conclusion survives anyway

At this point the effective alphabet reads **46.7** against the published 84.6, which
would overturn the entire pessimistic endgame. It does not, and the check that
settles it is FR40's own criterion: is the excess **shared passages** or **diffuse
inventory**?

Excluding position pairs whose shift lies at or near a known FR32 passage shift:

| exclusion | pairs | hits | null | z | effective alphabet |
|---|---:|---:|---:|---:|---:|
| none | 9,476 | 203 | 118.8 | **+7.96** | 46.7 |
| ±1 | 9,053 | 96 | 102.9 | **−0.69** | **94.3** |
| ±2 | 8,832 | 93 | 99.1 | −0.64 | 95.0 |
| ±3 | 8,681 | 93 | 97.6 | −0.46 | 93.3 |
| ±5 | 8,298 | 91 | 93.3 | −0.22 | 91.2 |

**The entire excess is shared passages.** One position of exclusion collapses z from
+7.96 to −0.69, and it stays there.

**FR39's conclusion stands, and strengthens.** The diffuse inventory estimate is
**91–95**, above the published 84.6 rather than below it. Small scattered alphabets
remain excluded; the plaintext is if anything flatter than doctrine records.

---

## 3. What is actually corrected

**FR39 was right for the wrong reason.** It measured at +w, found flat, and concluded
a large inventory. The correct residue is −w, where the passages are loud — and
removing the passages returns flat again. The published conclusion is correct; the
route to it was not.

**FR40's positive control was structurally incapable of catching this.** It validated
the channel on the near-duplicate pairs East1/West1 and East4/East5 — **both of which
have w = 0**, where +w and −w are identical. A control chosen from the pairs where the
sign is invisible cannot detect a sign error. That is a specific and repeatable
design failure: *a positive control must exercise the parameter it is meant to
validate.*

**The corrected channel is more useful than the old one.** At −w it detects shared
passages at z = +7.9 and locates their shifts correctly. FR39 discarded the
near-duplicate pairs to avoid passage contamination; with the sign fixed, passages can
be **identified and excluded by shift** rather than by discarding whole message pairs.
That recovers two message pairs' worth of data for future inventory estimates.

---

## 4. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity clean;
exposure 74.1%; alphabet 14.46 bits; message bases 19.13 bits (14.55 under the
indicator constraint); alphabet size in [56, 83]. **Plaintext effective inventory
91–95 after passage exclusion, up from 84.6.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 5. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| FR39 coincidence condition | `v − v′ = +w` | **`v − v′ = −w`** — sign corrected |
| FR39's flat result | evidence of large inventory | **measured at an empty residue**; correct by accident |
| Effective inventory | 84.6, CI [77.3, 93.4] | **91–95** after shift-based passage exclusion |
| Small scattered alphabets | excluded at 3.3σ | **still excluded**, and more firmly |
| FR40's positive control | validated the channel | **blind to the sign** — both control pairs have w = 0 |
| Passage handling | exclude whole message pairs | **exclude by shift**, recovering two pairs of data |

---

## 6. Methodological note

Two cycles running, a sign convention has been the error. FR78 found it in FR43 and
withdrew a headline finding. FR79 found it in FR39 and the headline survived.

The difference is instructive. FR43's conclusion **depended on which sixteen drifts H4
named**, so the sign propagated straight into the result. FR39's conclusion depended
only on whether a residue was **flat**, and both residues are flat once passages are
removed — so the error was invisible in the output.

**An error that does not change the answer is still an error**, and it left the
channel unable to see the passages it was measuring around. That is why this was worth
a cycle even though nothing was overturned.

---

## 7. Horizon

1. **Re-estimate the inventory using all seven message pairs** with shift-based passage
   exclusion rather than pair-level discarding. FR39 threw away the two near-duplicate
   pairs; they are now usable and they are the largest.
2. **Audit remaining uses of `w`** for sign. Two of three checked so far contained the
   error.
3. **Acquire glyph 76** (FR78) — West 2's indicator, dual payoff.
4. **The success criterion** (FR66, FR72, FR73). Unchanged, and §2 makes the deliverable
   marginally worse: inventory 91–95 rather than 84.6.
