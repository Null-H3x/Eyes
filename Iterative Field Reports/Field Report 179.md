# Field Report 179 — THE CIPHER IS A QUAGMIRE II WITH A PROGRESSIVE KEY

*Artifact: `CIPHER_FAMILY.md`. July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Placement

```
straight plaintext alphabet + MIXED ciphertext alphabet + PROGRESSIVE shift, mod 83
```

**Quagmire II** is straight-plaintext, mixed-ciphertext, cycleword key.
**Trithemius** is straight-both, progressive key. Ours is the hybrid: **Quagmire
II with a progressive key**, at modulus 83.

Not a novel construction — two classical ones combined with an enlarged
alphabet. That also explains why the community's Alberti and n-time-pad
candidates failed: neither has a *linear* positional law.

---

## 1. The standard attack chain, and why each step dies

| step | standard method | here |
|---|---|---|
| 1 | Kasiski / IoC to find the period | **inapplicable** — period is 83 for every drift (prime modulus) |
| 2 | isolate columns, solve monoalphabetically | **impossible** — messages are 1.19–1.65 periods long, so every column has 1–2 members |
| 3 | cribs | **the fallback**, and what our acquisition spec already specifies |

> **Within a message this cipher is effectively a one-time pad.** The key
> repeats at most once, over 289 of 1,036 positions.

That is the structural explanation for seven years of failed within-message
attacks — and it means the community's IoC effort was hunting a period that does
not exist.

---

## 2. A new channel, tested and empty

`d·(t+83) ≡ d·t (mod 83)`, so `c[t] == c[t+83]` **iff** `p[t] == p[t+83]` —
co-plaintext readable off the raw ciphertext, drift-independent, model-free.

```
pairs available : 289      matches : 3      expected by chance : 3.5
```

At chance, and adding them changes nothing. **Sound arithmetic, empty channel.**

---

## 3. What it confirms

The exploitable structure is **entirely cross-message** — shared passages and
forced base differences. The literature says so independently: with columns of
size 2 there is nothing else. **The model's cross-message approach was not a
choice but the only door in the building.**

---

## 4. Doctrine changes

| item | prior | now |
|---|---|---|
| Family | ad hoc description | **Quagmire II + progressive key** |
| Why IoC fails | uniform plaintext (FR173) | **also no period exists** |
| Within-message attacks | seven null results | **near-one-time-pad**, structurally explained |
| Period-83 channel | unknown | **valid, drift-independent, empty at 3/289** |
| Crib requirement | 15 tokens | **matches published Quagmire guidance** |

---

## 5. Model status

Unchanged: one reading, five fragments, 819 positions (79.1%), 794 relations,
61 glyphs, all nine messages in the largest fragment. Cumulative: 27.16 billion
candidates, zero survivors.

---

## 6. Horizon

1. **`stblake/polyalphabetic`** is a published hill-climber for Quagmire I–IV
   with backtracking and simulated annealing. It is the right *shape* of tool —
   but it scores with English n-grams, and FR173 showed our token distribution
   is uniform. **The machinery transfers; the fitness function does not.**
2. **Item 2 next**: Fragment 2, now 222 positions.
3. The family placement should go to the community — it names what they are
   attacking and explains why two of their three candidates were never viable.
