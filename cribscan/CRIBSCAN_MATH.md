# Cribscan — Mathematical Findings

*The math behind `passread.py` and the Triplet-3 passage attack. Every result
here is reproducible; the ones that live in code are gated by
`python3 passread.py --selftest`. Where a claim is a hypothesis, it says so.*

This document is deliberately narrow. It does **not** restate the whole solve
(see `STATE_OF_THE_SOLVE.md`); it derives the specific structure `passread.py`
exploits and reports what it does and does not buy us — including one earlier
over-claim of mine, retracted below with the test that caught it.

---

## 1. The model, and what a shared passage forces

The leading model is the **linear class**

```
c_m[t] = C[(σ · p_m[t] + base_m + drift · t) mod N]        N = 83 (prime)
```

with σ ∈ {+1, −1}, drift ∈ {+1, 0, −1}, `C` a fixed mixed alphabet (permutation
of ℤ₈₃), and `q = C⁻¹` the value→position map. `model_power` (repo) proves the
same-plaintext isomorph evidence pins this **class** — `{pmp (σ+,drift+1),
pure, beaufort (σ−)}` are mutually indistinguishable at the isomorph level — not
`pmp` uniquely. Everything below therefore sweeps drift × sign.

Take a passage that occurs as the **same plaintext** `P[0…L−1]` at instances
`(m, s_m)`. Writing `q` on both sides and setting `B_m := base_m + drift·s_m`:

```
q[c_m[s_m + i]]  =  σ·P[i] + B_m + drift·i          (†)
```

Three consequences, each of which `passread.py` computes.

### 1a. Cross-instance offsets are constant (the isomorph identity)

Subtract (†) at the same `i` for two instances:

```
q[c_{m}[s_m+i]] − q[c_{m'}[s_{m'}+i]]  =  B_m − B_{m'}   =: Δ_{m,m'}   (constant in i)
```

Independent of `i`, the alphabet, and `P`. This is why aligned positions across
instances give **isomorphic-but-not-identical** ciphertext (same repeat pattern,
values shifted by `Δ`) — the model-free fingerprint the corpus is full of.

### 1b. The passage is a 3-shift monoalphabetic cryptogram

Define `D[i] := (σ·P[i] + drift·i) mod N`. Then (†) reads
`c_m[s_m+i] = C[D[i] + B_m]`: **one sequence `D`, imaged through the single
alphabet `C`, with a per-instance additive shift `B_m`.** Recovering the whole
passage is exactly a monoalphabetic-cryptogram problem in `D` with three related
keys — the sense in which "recover `q` and the corpus collapses to a shared
cryptogram" is literally true.

### 1c. The equality structure is a language-independent crib

Within one instance, `c_m[s_m+i] = c_m[s_m+j]` ⟺ `D[i] = D[j]` ⟺ (unwinding)
`σ·(P[i]−P[j]) = drift·(j−i)`. So the ciphertext coincidences hand us a set of
**forced plaintext relations** with no alphabet needed. For the real Triplet-3
passage (§3) these are the positions `{1,11}`, `{2,9}`, `{4,12}` — a candidate
plaintext must repeat a letter across each group. That is a real, if modest,
filter on guesses before any language model is consulted.

---

## 2. The consistency test and its degrees of freedom

Stack (†) over all occurrences as a linear system over GF(83) with unknowns
`q[·]` (one per distinct ciphertext symbol in the passage), `P[0…L−1]`, and
`B_0…B_{M−1}`. Two facts fall out of its rank:

- **Consistency** (no pivot in the augmented column) means the instances *can*
  be a single same-plaintext set under the class — a necessary condition, and
  the honest limit of what a passage-level test proves. It does **not** rank
  `pmp` over `autokey`/`alberti`: `model_power` Finding 0 shows a repeated word's
  skeleton is invariant to the chaining history, so all these families preserve
  planted-repeat skeletons. Passage consistency is a same-plaintext certificate,
  full stop; the family exclusions are earned upstream on clean anchors.

- **Degrees of freedom** `= unknowns − rank`. Two of these are always gauge:
  1. `P[i] += a` (all i) with `q[·] += σa` — shift the plaintext, absorb in `C`;
  2. `B_m += b` (all m) with `q[·] += b` — shift all bases, absorb in `C`.
  Both feed `q` only through the single net constant `σa + b`, so **`q` is pinned
  up to exactly one additive rotation**, never more, from the passage's internal
  structure. The remaining dof beyond the gauge count genuinely free plaintext
  positions (singletons with no equality partner).

`passread.py --selftest` plants pmp/pure/beaufort corpora and asserts the system
is consistent with the correct equality classes; it plants deliberately
misaligned windows and asserts contradiction-or-no-shared-classes.

---

## 3. The real Triplet-3 result (measured)

Instances `East 4@50, West 4@52, East 5@51`, `L = 30`:

```
drift=±1,0 · sign=±1 :  rank 79 / 81  ·  dof 2  ·  48 distinct symbols  ·  CONSISTENT (all six)
relative-plaintext equality classes : {1,11}  {2,9}  {4,12}
```

Consistent under the **entire** linear class — a genuine same-plaintext triple,
model-free-given-the-class. dof 2 is exactly the two gauges of §2, so the passage
pins its `q`-fragment up to one rotation. This is the sharpest fully-determined
relative-plaintext object in Triplet 3, and — unlike the refrain — the existing
crib tooling never targeted it.

### 3a. Retraction: "48 sound ordered pins" was a solver artifact

I initially read the `48` distinct symbols as **48 sound ordered pins** that
would blow past `support_min`'s ~22-pin floor. That was wrong, and I caught it
by doing what the house style demands — running the instrument on a plant with a
**known-distinct** alphabet. My hand-rolled gauge-export returned `1` pin on
that plant (truth: 47). The extractor was buggy; the "48 pins" on the real
corpus was the same bug, not a finding.

The correct statement is the humble one, and it agrees with `iso_relax`: the
passage **links** its symbols tightly but does not by itself **order** them past
the standing wall (linked-not-ordered, distinct/linked ratio collapse). The
certified sound-pin count for this passage is whatever `iso_relax`'s
gauge-invariance export yields when pointed at the Triplet-3 structure — a run
worth doing, but **not** a number I will assert from my own solver. `passread.py`
therefore reports the *linkage* (48 symbols, dof 2) and leaves the *ordering*
claim to the validated tool.

### 3b. What the passage IS good for: a second, cross-validating crib target

A **correct** plaintext guess placed at known positions is a different animal
from an isomorph pin — it **orders** every symbol it covers (pins `q` absolutely
up to the one rotation of §2, because position is known). `passread.py`'s
`place_crib` does this deterministically: with the base-0 gauge, instance-0
positions read out exactly, and decrypt needs no rotation search. Selftest
confirms a correct crib recovers the planted passage and a wrong crib is
rejected (contradiction or misread).

The strategic value is **coverage** and **cross-validation**, both measured:

```
Triplet-3 dof-1 passage :  48 / 83 distinct symbols
Refrain (T1) region     :  59 / 83
T3 ∪ refrain            :  72 / 83   (87%)
T3 ∩ refrain            :  35 symbols shared
T3 ∪ refrain ∪ T1-open  :  75 / 83   (90%)
symbols in none         :  {27, 28, 35, 39, 51, 52, 74, 76}   (8 of 83)
```

Two implications:

1. **Two correct cribs cover ~87–90% of the alphabet.** A correct crib orders
   the symbols it covers, so a correct refrain guess **plus** a correct
   Triplet-3 guess would pin 72 symbols in order — comfortably past
   `support_min`'s convergence band (100% recovery by 40 ordered pins) — and the
   corpus would decrypt. The bottleneck is still *guessing correctly*; what
   changes is that there are now **two independent, disjoint-ish levers**, not
   one.

2. **The 35-symbol overlap makes joint placement sharp.** A correct pair of
   guesses must agree on all 35 shared symbols; a wrong guess on either side
   breaks that agreement. So *joint* crib placement across the two targets, with
   an overlap-consistency gate, is materially sharper than the repo's
   single-target `crib_fit` — it adds 35 hard equality checks that a
   phrase-alone attack does not have. This is the concrete way past the
   "pattern-mode crib is 98% permissive" trap: the permissiveness came from
   scoring one target's letter-pattern; overlap consistency across two committed
   targets is not permissive.

---

## 4. What this does and does not change

**Does not change.** The wall is still the wall. Isomorphs link but do not order;
the structured-alphabet corner is excluded (~9M hypotheses, `alphabet_sweep`);
the PRNG corner is moot (offline-authored, `binary_provenance`); reading requires
either an external glyph→char anchor or a correct crib. `passread.py` invents no
new alphabet ordering and I claim none.

**Does change.** The attack surface for the *correct-crib* route is now two
cross-validating targets instead of one, with 87–90% joint alphabet coverage and
35 symbols of mutual constraint — and the Triplet-3 target, previously
un-attacked, is instrumented with a deterministic, plant-validated reader. The
next concrete moves are: (i) run `iso_relax` against the Triplet-3 and
cross-triplet (`W2/E4/W4`) structures to get a *certified* sound-pin count and,
if it lifts the floor, hand it to `support_min`; (ii) drive `place_crib` from a
salakieli / noita-lexicon candidate list under an overlap-consistency gate with
the refrain; (iii) fold the pyry_gate micro-fingerprints (zero adjacent doubles
z ≈ −3.7, distance-4 excess 2.24×) into a per-(language × structured-E) rate
filter to prune crib candidates before scoring.

---

## 5. Reproduce

```bash
python3 passread.py --selftest                       # gate (structure + crib, plant-validated)
python3 passread.py --passage t3-dof1 --L 30         # real-corpus structure (all drift/sign)
python3 passread.py --passage t3-dof1 --L 30 \
        --crib "<candidate>" --offset 0              # place a crib, report coverage + verdict
```

Corpus auto-discovers `noita_eye_core/corpus.json` (or the trigram CSV). The
`--crib` mechanism is illustrative until a correct guess is found; on a wrong
guess it reports 48-symbol coverage and reads gibberish, as it should.
