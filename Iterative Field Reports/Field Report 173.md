# Field Report 173 — UNIFORM, NOT ZIPF: LANGUAGE IS REFUTED AT EVERY GRANULARITY

*July 2026. Cycle: EYESPIRAL-C.*

---

## 0. The test that decides whether the reopening is worth anything

FR172 found the eye plaintext has an 83-token inventory, refuting letters and
suggesting a larger unit — syllables or words. Before running any word-level
vocabulary work, one measurement decides whether that route can exist.

**Natural language is Zipf-distributed at every granularity.** Letters,
syllables and words all show heavy skew. If the token distribution is flat, no
unit size rescues the language hypothesis.

```
435 tokens, 82 types

observed counts (top 15) : [11,11,11,10,10,10,9,9,9,9,9,9,8,8,8]
observed counts (bottom) : [3,3,3,2,2,1,1,1,1,1]

UNIFORM prediction  : mean 5.3, sd 2.3, top ~11
observed            : mean 5.3, sd 2.5, top 11
chi-square vs uniform: 93.4 on 81 df    z = +0.97

ZIPF prediction (natural-language words, s=1):
   top-15 expected : [87,44,29,22,17,15,12,11,10,9,8,7,7,6,6]
   top type would be ~87 tokens (20.0%)
   observed top type: 11 tokens (2.5%)
```

> **The distribution is indistinguishable from uniform (z = +0.97) and nowhere
> near Zipf. The observed top type is 2.5% where language predicts 20%.**

---

## 1. What this closes

**The granularity reopening does not rescue the language hypothesis.** It
explains why letter-level tests had no power — wrong unit — but word-level and
syllable-level tests are **refuted before being run**, on distribution alone.

This is model-independent in the way that matters: the distribution *is* the
equality-class size profile, which is what the model determines most robustly
(794 relations, zero contradictions, 100% mutual prediction against a 2.8%
control). It does not depend on the drift (scale-invariant) or the bases
(a shift).

**And it refutes the Emerald Tablet hypothesis by the same argument.** The
Emerald Tablet is a text — Latin or English, either way Zipf-distributed at
every unit size. It cannot produce a flat 83-type profile. The same goes for any
proposed plaintext that is prose in any language.

---

## 2. What a flat 83-type distribution actually is

```
random or already-encrypted data     -- uniform by construction
an enumeration / index / key         -- each value used about equally
a controlled inventory used evenly   -- e.g. a shuffled deck
```

**A uniform distribution is what a well-encrypted layer looks like.** The most
economical reading of everything since FR39 is that `p` is not plaintext at all
but a **second cipher layer** — which is consistent with FR137's finding that
the community's own autokey demonstration was worth testing, and with the seven
null results, and with this one.

**The honest caveat**: uniformity is also what a *wrong model* would recover.
The model's support is strong, but "the inner layer is encrypted again" and
"the outer model is subtly wrong" both predict exactly this and are not
separated by any measurement available here.

---

## 3. Doctrine changes

| item | prior status | status now |
|---|---|---|
| Word/syllable granularity | promising reopening (FR172) | **refuted** — distribution is uniform, not Zipf |
| Language hypothesis | letter-level only | **refuted at EVERY granularity** |
| Emerald Tablet as plaintext | untested candidate | **refuted** — prose is Zipf at every unit size |
| "The plaintext is featureless" | seven null results | **it is UNIFORM**, which is a positive characterisation |
| Most economical reading | unstated | **the inner layer is a second cipher, or not text** |

---

## 4. Model status

Unchanged: 794 relations, 61 glyphs, 79.1% exposure, 435-position reading, 68
maximal readings, two invariant cores, stamped header forced. **Plaintext
inventory 83, distribution uniform, language refuted at all granularities.**
Cumulative: 27.16 billion candidates, zero survivors.

---

## 5. Horizon

1. **Do not run word-level or syllable-level vocabulary work.** It is refuted
   in advance and would cost cycles to confirm a known negative.
2. **The Emerald Tablet directory can still be read for other reasons** —
   provenance, asset lists, community findings — but not as a plaintext
   candidate.
3. **If the inner layer is a second cipher, the outer solution is the whole
   prize**, and FR101's success criterion was right to scope it that way. The
   remaining unknowns are 68 readings × 82 drifts × 83⁴ bases, and nothing
   internal will reduce them further.
