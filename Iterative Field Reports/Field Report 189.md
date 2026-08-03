# Field Report 189 — RETRACTION: FIVE CYCLES RESTED ON CONFLATING THE PLAINTEXT ALPHABET WITH q's IMAGE

*July 2026. Cycle: EYESPIRAL-C. The largest retraction in the series.*

---

## 0. The observation that exposed it

Checking whether the standing model's alphabet cap was consistent with the IC, I
found what looked like a decisive internal contradiction — and then found the
number that dissolves it:

```
largest fragment: 491 positions
  distinct GLYPHS       : 37
  distinct PLAINTEXT VALUES: 83
```

**Thirty-seven glyphs producing eighty-three plaintext values.** That is not a
contradiction. It is the cipher working exactly as designed:

```
p[t] = q[c[t]] - base - d*t
```

The same glyph at different positions yields different plaintext, because the
shift moves. A handful of glyphs across hundreds of positions produce all 83
values.

---

## 1. The error

Let `u = p + base + d·t`, so `q[c] = u` and `c = C[u]`.

- merges (`q[a] = q[b]`) reduce `|image(q)|` to `83 − m`
- `u` must lie in `image(q)`
- **but `p = u − shift(t)`, and the shift varies with position**

> **The plaintext alphabet is NOT `q`'s image.** The merges constrain which
> `(p, position)` **pairs** are possible — not how many distinct plaintext
> symbols exist.

I treated them as the same object.

---

## 2. What this retracts

| report | claim | status |
|---|---|---|
| FR185 | "8 homophones ⇒ C's image is 75 ⇒ plaintext drawn from 75 symbols" | **WITHDRAWN** |
| FR185 | "the 8 homophones are disfavoured at −2.7σ" | **WITHDRAWN** |
| FR186 | "the plaintext implies ~4 merges, the model forces 8" | **WITHDRAWN** |
| FR187 | "the low-homophone model matches the IC prediction" | **WITHDRAWN** |
| FR188 | "the IC prices merge counts by likelihood" | **WITHDRAWN** |
| FR189 | "the model uses more plaintext values than its alphabet permits" | **WITHDRAWN** |

**All six rest on the same conflation.** Five consecutive cycles built on it, and
each internal check I ran — replication, bias, pricing, likelihood — tested the
*arithmetic* while leaving the *premise* unexamined.

---

## 3. What survives, and it is not nothing

**The IC measurement is untouched.** It is a property of the recovered plaintext
and was computed correctly:

```
pooled IC   = 0.01268 over 146,766 pairs
1/IC        = 78.9
bias check  : +0.01 to +0.06 at n=491 -- essentially unbiased
```

> **The plaintext uses ≈ 79 effective symbols.** That stands, and it remains the
> first narrowing of any plaintext parameter in eighty reports.

What does **not** survive is the inference from that number to the homophone
count. The plaintext's effective symbol count says nothing about how many glyph
pairs share a `u`-value.

**FR188's verdict — "the standing model wins" — was right by accident. There was
never a contest.**

---

## 4. The methodological lesson

Four malformed statistics were caught during this line (FR183's null, FR184's
tautology, FR186's attribution, FR188's rejection cost) and each catch increased
my confidence in the framework doing the catching. **The framework itself was
wrong.**

Checking arithmetic repeatedly is not the same as checking the premise, and a
run of successful self-corrections is not evidence that the foundation is sound.
If anything it is a warning: the errors kept being *findable*, which meant I kept
looking in the same place.

**Standing rule, added:** *when several consecutive cycles all refine one
quantity, stop and re-derive what that quantity means from the model definition
before continuing.*

---

## 5. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Plaintext alphabet = `83 − merges` | assumed since FR185 | **FALSE** — plaintext is not confined to `q`'s image |
| Alphabet `[78, 82]` | a bound on `C`'s image | **an estimate of the plaintext's effective symbol count** |
| The 8 homophones | challenged then defended | **never challenged** — the challenge was ill-formed |
| `1/IC` | biased? | **essentially unbiased**, +0.01 to +0.06 at n=491 |
| FR188's verdict | a considered ruling | **vacuous** |

---

## 6. Model status

Unchanged, and unchallenged: 794 relations, 61 glyphs, 8 homophones, one
reading, five fragments, 819 positions (79.1%). **Plus: the plaintext uses ≈79
effective symbols.** Cumulative: 27.16 billion candidates, zero survivors.

---

## 7. Horizon

The IC line produced **one durable result** — the plaintext's effective symbol
count — and five cycles of scaffolding around a false premise. The result is
worth keeping and the scaffolding should be struck.

What the ≈79 figure actually constrains is the **plaintext**, not the cipher:
it says the source uses nearly the full ring evenly, which is FR173's uniformity
finding restated with a number attached. It does not bear on `C`, the merges, or
the drift.
