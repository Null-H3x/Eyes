# Field Report 137 — PLAINTEXT AUTOKEY IS REFUTED: IT COLLAPSES THE ALPHABET TO ONE SYMBOL

*Instrument: `eyeauto.py` (3/3 gate). July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Why FR118 could not settle this

FR118 identified plaintext autokey — Pyry's own demonstration cipher — as a
live rival, showed the isomorph skeleton **cannot discriminate it** from the
progressive model, and left it as the project's biggest untested question. But
it modelled autokey as *"a free constant per alignment"*, which determines
nothing by construction. The comparison was rigged before it started.

A **specific** autokey has real content.

---

## 1. The derivation

Pyry's cipher rotates by the previous plaintext character: `K[t+1] = K[t] + p[t]`.

```
q[c[t]] = p[t] + b + K[t]
K[t+1]  = K[t] + (q[c[t]] - b - K[t]) = q[c[t]] - b
K[t]    = q[c[t-1]] - b
=>  p[t] = q[c[t]] - q[c[t-1]]
```

**The base cancels entirely.** The plaintext is the difference of consecutive
alphabet values — no per-message offset, no drift.

A shared passage asserting `p_A[s1+i] = p_B[s2+i]` therefore gives

```
q[c1[s1+i]] - q[c1[s1+i-1]] = q[c2[s2+i]] - q[c2[s2+i-1]]
```

**linear in `q`**, exactly as the progressive constraint is, but a *different*
condition on the same evidence. Both models can now be built on the same pool
and compared — which is what FR118 wanted and could not do.

---

## 2. The result

On the repaired pool (67 pairs), 478 autokey constraint rows:

| | relations | glyphs | **equalities** |
|---|---:|---:|---:|
| progressive | 384 | 56 | **0** |
| autokey | 2628 | 73 | **2628** |

`C(73, 2) = 2628` **exactly.**

> **The simple plaintext autokey forces ALL 73 reached glyphs to share ONE
> alphabet value.**

Verified directly: every pair among the first twenty checks as `redundant` at
difference zero. The solution is total collapse.

That is not "a worse fit" — it is **refutation**. Under this model every glyph
decodes to the same plaintext token, so the 83 distinct ciphertext values carry
no information and the isomorphs the model was invoked to explain could not
arise at all.

---

## 3. The out-of-sample score is vacuous, and that matters

```
progressive  85/85 held-out pairs predicted  (100%)
autokey      96/96 held-out pairs predicted  (100%)
```

Autokey **scores higher**. Taken at face value it wins.

**It is vacuous.** Every prediction succeeds because every pair is asserted
equal. **A model that says "everything is the same" predicts perfectly and
explains nothing.**

This is the FR130 error class — *counting a condition as a success* — appearing
in the discriminating test itself, and it would have inverted the verdict. The
degeneracy check is what caught it, and it was only run because `2628 = C(73,2)`
is a suspiciously exact number.

**Standing rule, added:** an out-of-sample score must be reported alongside the
model's determination structure. A perfect score from a degenerate model is a
red flag, not a result.

---

## 4. What this settles

**FR118's rival is eliminated.** The progressive form is no longer "better
supported than its one tested rival" — the rival is refuted by the same
evidence the progressive model survives.

Scope, stated honestly: this refutes `K[t+1] = K[t] + p[t]`, the simplest and
most natural plaintext autokey, and the one Pyry's demonstration uses. A
*general* autokey `K[t+1] = K[t] + g(p[t])` for some non-identity `g` is not
tested and would need its own derivation. But the collapse is severe and
structural, and any `g` yielding a similar telescoping produces it.

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| **Plaintext autokey** | live rival, untested (FR118) | **REFUTED** — collapses the alphabet to one symbol |
| FR118's "free constant per alignment" model | the tested form | **rigged** — determined nothing by construction |
| Progressive form | better supported than its rival | **its only tested rival is eliminated** |
| Out-of-sample scores | the discriminator (FR38) | **must be read with the determination structure**; a degenerate model scores 100% |
| Error taxonomy | +counting a condition as success (FR130) | **same error can invert a discriminating test** |

---

## 6. Model status

Unchanged and better founded. Repair A: 384 relations, 56 glyphs, 74.1%
exposure. Repair C: 409/57/1, 191-position reading. **The progressive
keystream now stands without a surviving rival.** Cumulative: 27.16 billion
candidates, zero survivors.

---

## 7. Horizon

**Items 1 and 2 are both closed. The mathematics is exhausted.**

- the atlas is correct, incomplete, and its incompleteness changes nothing (FR136)
- plaintext autokey is refuted (FR137)
- alphabet bounds [56, 82] cannot be narrowed internally (FR135)
- the plaintext has no structure across seven independent lines
- acquisition is unchanged: 11 anchors, 15 crib tokens, or one anchor on
  glyph 36/68

**What remains is educated assumption, and it should be labelled as such.**
