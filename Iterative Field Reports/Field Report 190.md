# Field Report 190 — CONTAINMENT AUDIT: THE CONFLATION IS LIMITED TO FR185–189, AND FR170 CAUGHT IT FIRST

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. Applying the new rule

FR189's standing rule: *when several consecutive cycles refine one quantity,
re-derive what that quantity means from the model definition.* The first
application is to ask **how far the conflation spread.**

Every standing claim that mentions an alphabet size or symbol count, checked
against what it actually measures:

| claim | measures | verdict |
|---|---|---|
| FR97/FR135 `[56, 82]` | `\|image(q)\|` — how many `u`-values the 83 glyphs cover | **correct** — derived from merge exclusion on `q`, never from plaintext |
| FR127 bijectivity ⟺ no T1 | `q`'s injectivity | **correct** |
| FR146 8 homophones, ceiling 75 | `\|image(q)\| = 83 − 8` | **correct as stated**; only the plaintext inference was wrong |
| FR172 "the eyes are not letters" | 82 distinct **plaintext** values | **correct** — `p` is the plaintext, a direct count |
| FR173 inventory ≈83, uniform | distinct `p` values and their distribution | **correct** |
| FR181 the source is flat | isomorphs forbid any flattening transform | **correct** — no alphabet-size step in the argument |

> **The conflation is contained to FR185–FR189. Every other alphabet claim is
> about `|image(q)|` and is correctly derived.**

---

## 1. The uncomfortable part

**FR170 already made this exact distinction:**

> *"`[56, 75]` was never the token inventory; it is the image size of the glyph
> map `q = C⁻¹`. Two different quantities have been called 'the alphabet' since
> FR97."*

FR185 re-conflated them **fifteen reports later.**

The correction was in the record and I lost it. That is a **documentation
failure as much as a reasoning one** — a distinction stated once in a field
report does not survive contact with later cycles.

---

## 2. The remedy

The distinction is now a **banner on the four primary documents** —
`CURRENT_STATE.md`, `CIPHER_FORMULA.md`, `WORKING_ASSUMPTIONS.md`,
`INVARIANT_CORE.md` — rather than a paragraph in one report:

```
| term                | meaning                                    | value    |
| glyph-map image     | distinct u-values the 83 glyphs cover;      | 83 - m   |
|   |image(q)|        | reduced by each forced merge                | = 75     |
| plaintext inventory | distinct symbols the author wrote            | ~83      |
|                     | effective count (pooled IC over 146,766 pairs)| ~79      |
```

with the reason attached: `p = u − base − d·t`, the shift varies, so **one glyph
produces many plaintext values** — the largest fragment has 37 distinct glyphs
and 83 distinct plaintext values.

---

## 3. What the surviving IC result actually says

`1/IC = 78.9` is the **effective** plaintext symbol count — the inverse Simpson
index of the recovered `p`. Against a full inventory of ~83, an effective count
of ~79 means the distribution is **slightly** less than perfectly even.

That is FR173's uniformity finding with a number attached, and it constrains the
**plaintext** only. It bears on neither `C`, the merges, nor the drift — which is
precisely what FR185–188 got wrong.

---

## 4. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Scope of the conflation | unknown | **FR185–189 only**; six other claims audited clean |
| FR170's distinction | one paragraph, one report | **banner on four primary documents** |
| `1/IC = 78.9` | "the alphabet" | **the plaintext's effective symbol count** |
| Terminology discipline | implicit | **a distinction stated once does not survive; it must be structural** |

---

## 5. Model status

Unchanged: 794 relations, 61 glyphs, 8 homophones, one reading, five fragments,
819 positions (79.1%), `|image(q)| ≤ 75`, plaintext inventory ≈83 with ≈79
effective. Cumulative: 27.16 billion candidates, zero survivors.

---

## 6. Horizon

**The retraction is contained and the documents are repaired.** What the episode
cost was five cycles; what it bought was a structural fix to a distinction that
had already failed once silently.

Remaining work is where it was before the IC detour:

1. **The glyph-ordering question** (FR180) — still the only route that could pin
   the drift internally, still blocked on the trigram-to-value table.
2. **Fragment 2's own analysis** — 222 positions, six messages, never examined
   beyond its IC.
3. **Acquisition** — 6 anchors, or the `q[36]`/`q[68]` pair.
