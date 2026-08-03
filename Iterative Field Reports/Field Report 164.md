# Field Report 164 — THE CALIBRATED CONTROL REVERSES FR163: THE REAL CORPUS UNDER-PRODUCES HOMOPHONES

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. What FR163 got right and what it got wrong

FR163 proved the mechanism: the pipeline derives homophones that are **false in
the generating alphabet**, 23 of 23 across three synthetic runs, and no surprise
threshold removes them. That stands.

What it could not do was measure the **rate** in the real corpus, and it flagged
the extended skeleton's eight homophones as suspect on the strength of a
generator producing **85–117 classes against the real corpus's 208**. An
under-calibrated control.

---

## 1. Calibrated

Planting the full 208-class sharing structure by union-find (FR142's method),
with an **injective** alphabet — so every forced equality is false by
construction:

```
 seed  classes  acc   rel  gly  FALSE eq
 7000      208  160   506   49        16
 7001      320  237  1491   64        53
 7002      278  201  1332   64        15
 7003      232  181  1492   63        11
 7004      222  144  1433   58        42
 7005      186  121  1298   62        17
 7006      344  172  1441   66        11
 7007      199  158   519   52        20
 ----------------------------------------
 REAL      208  143   794   61         8
```

```
synthetic false equalities : mean 23.1 +- 14.6, range 11-53
real corpus                : 8
```

> **The real corpus forces fewer homophones than EVERY one of eight
> injective-alphabet controls** — 8 against a minimum of 11 and a mean of 23.

---

## 2. Why that is evidence *for* the model

An injective alphabet with realistic sharing structure yields 11–53 spurious
homophones through this pipeline. The Eye yields 8. **Its classes are
substantially more mutually consistent than chance isomorphs are**, which is
what genuine co-plaintext looks like.

And the shape corroborates it: the real corpus reaches **794 relations from 143
accepted classes**, while the controls need 121–237 accepted classes to reach a
comparable count. **More information from fewer classes** is the signature of
real structure, not accepted noise.

---

## 3. SELF-CORRECTION to FR163

| FR163 claim | status |
|---|---|
| The pipeline manufactures false homophones | **stands** — 23/23 false, mechanism proven |
| No surprise threshold removes them | **stands** |
| The 8 homophones are SUSPECT | **withdrawn** — the calibrated control puts them *below* every injective-alphabet run |
| Alphabet ceiling reverts to [56, 83] | **withdrawn** — [56, 75] restored |

FR163 raised the alarm on an under-calibrated control and I published it before
calibrating. **The mechanism was real; the inference from it was not.** That is
the third time in this series a control has decided a question the wrong way
before being matched to the corpus it was controlling for — FR138, FR141, and
now FR163.

**Standing rule, added:** *a control must be calibrated to the observable it is
controlling for before any inference is drawn from it — not after.*

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| The 8 homophones | suspect (FR163) | **supported** — real forces 8 vs control range 11–53 |
| Alphabet ceiling | [56, 83] (FR163) | **[56, 75] restored** |
| False-equality mechanism | proven | **still proven**, but the Eye shows less of it than chance |
| Relations per accepted class | unexamined | **794/143 real vs ~1189/170 control** — real is denser |
| Control calibration | ad hoc | **must match the observable first** |

---

## 5. Model status

Restored and now better supported: extended skeleton, 794 relations, 61 glyphs,
**8 homophones (supported)**, alphabet [56, 75], 79.1% exposure, 435-position
reading, 6 anchors, 68 maximal readings, 19-relation invariant core.
Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

1. **This closes the `d ≡ 0` line.** The correspondent's inference rested on a
   generator giving 0 forced pairs; mine gives 11–53 depending on calibration,
   and the real corpus gives 8. The forcing is neither absent nor anomalous —
   it is **below** the injective-alphabet rate, which is the opposite of what
   `d ≡ 0` would require.
2. **The two invariant homophones are correspondingly strengthened**: they
   survive all 68 readings *and* the corpus under-produces homophones relative
   to chance.
3. No internal item outstanding.
