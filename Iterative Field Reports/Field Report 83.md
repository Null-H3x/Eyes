# Field Report 83 — THE HEADER TREE: A SIXTH CHANNEL, AND IT RECOVERS THE ODD MESSAGES

*Instrument: `eyeprefix` (corpus-only, no skeleton). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — structure described but never analysed

FR82 quantified the completion of the internal programme. Having claimed completion
twice before and been wrong twice, the honest move is to look for structure never
examined rather than re-test what is closed.

One item qualifies. FR44 described the opening prefix tree qualitatively — *"positions
1..2 give 1 distinct, 1..6 give 4, 1..20 give 5"* — and used it as a supporting remark
for the stamped-header reading. **Its topology has never been extracted.**

That matters because FR76 found T2's grouping evidence is header-driven. If the header
is stamped metadata, its branching structure records **how the author organised the
messages**, which is information of a kind the ciphertext channels cannot supply.

---

## 1. The tree

Positions 1 and 2 are universal (66, 5). Splits occur at positions 3, 6, 10 and 21.

```
root (66, 5)
 |-- 48,62,13 ------------> East1, West1, East2        == T1 EXACTLY
 \-- 49,75,54
      |-- 69 ------------->  West2
      |-- 23 ------------->  West3
      \-- 2,60,29,40
           |-- 78 -------->  East3
           \-- 2 --------->  East4, West4, East5       == T3 EXACTLY
```

---

## 2. It recovers what coincidence could not

| claim | header | coincidence | isomorph |
|---|---|---|---|
| T1 = {E1, W1, E2} as a unit | **YES** | E2 silent (FR76) | yes, class #M |
| T3 = {E4, W4, E5} as a unit | **YES** | W4 silent (FR76) | yes, class #2 |
| T2 = {W2, E3, W3} as a unit | **NO** | no, z = +0.07 | no known within-T2 class |

**The header groups T1 and T3 exactly, including the odd messages.** East 2 and West 4
are the two messages FR76 found coincidence-silent — attested only by the atlas, which
I could not audit. The header attests them independently, from a completely different
kind of evidence.

That resolves FR76's open question the right way round. The odd messages *are* in their
triplets; aligned coincidence simply cannot see them because it requires shared
plaintext at the same index, which they do not have.

**And T2 fails again.** The header splits West 2 and West 3 off as singletons at
position 6. That is a **sixth independent channel** finding no internal structure in
T2, after FR35's free-w scan, FR74's bridge scan, FR75's coincidence, FR76's grouping
re-derivation, and FR77's isomorphs.

---

## 3. The anomaly

**East 3 shares nine header positions with East 4, West 4 and East 5**, diverging only
at position 10 (78 versus 2). It sits on **T3's branch**, not with West 2 and West 3.

FR44 noted the E3/E4 identity at positions 1–9 and retired it as a candidate test,
correctly, because both the stamped and encrypted readings predict it. What FR44 did
not do is read the **tree**: E3 is not merely similar to E4, it is nested inside T3's
subtree and separated from its own triplet-mates at an earlier branch point.

Two readings, and I cannot choose between them:

- **The header is content taxonomy, not keystream grouping.** Under A4 the openings are
  stamped literal material, so the tree records how the author *catalogued* the
  messages, which need not match how he *keyed* them. E3 could be thematically with T3
  and cryptographically with T2.
- **The triplet assignment is wrong for East 3.** Six channels find no within-T2
  structure, and the one channel that does group messages puts E3 elsewhere.

The second is testable in principle — E3 in depth with T3 would show coincidence — and
FR76 measured exactly that: E3/E4 at z = +0.59, E3/E5 at +0.90. **Nothing.** So E3 is
not in depth with T3 either, which leaves the first reading and leaves E3 grouped with
nothing at all.

---

## 4. What is actually gained

**A sixth channel on T2**, and the first one that is not derived from the skeleton.

**Independent attestation of E2 and W4**, which had rested entirely on atlas classes I
could not inspect. That closes FR76's horizon item 1 without needing the atlas spans.

**A structural fact about the corpus**: the messages form a four-way taxonomy
(T1 | W2 | W3 | E3+T3) that does not coincide with the triplets. Whatever the header
encodes, it is not the keystream grouping.

**Nothing that reduces 33.59 bits.** The header is stamped, so it carries no keystream
or alphabet information. This is orientation, not progress against the residual — and
FR82's account of why the residual is irreducible stands untouched.

---

## 5. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits;
inventory 82.5, CI [73.0, 93.7]; determinacy threshold 81.2, unresolvable by 51×.
**Header tree extracted: T1 and T3 recovered as units, T2 split three ways, East 3
nested in T3's subtree.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 6. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Header prefix tree | described qualitatively (FR44) | **topology extracted**; splits at positions 3, 6, 10, 21 |
| E2 and W4 membership | atlas-only, unauditable | **independently attested** by the header |
| T2 internal structure | unattested in five channels | **six** |
| East 3's placement | member of T2 | **nested in T3's subtree**; in depth with neither |
| Message taxonomy | assumed = triplets | **four-way, and not the triplets** |

---

## 7. Horizon

1. **The header may encode message order.** Splits at positions 3, 6, 10, 21 with
   distinct values per branch is the shape of a structured index. If the branch values
   encode ordinals, that bears directly on H4's consecutive-label premise — the one
   assumption the project cannot test. Worth a cycle.
2. **Acquire glyph 76** (FR78) — West 2's indicator, dual payoff.
3. **The success criterion** (FR82 §7): *"is it worth acquiring external evidence to
   find out?"*
