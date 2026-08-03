# Field Report 91 — PETRI'S MNEMONICA FILE FOUND, AND WHAT HIS TOOL ACTUALLY DOES

*Instrument: `eyemnem` (archival + sweep + periodicity). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. The lead

The author is a card magician with published cut and card-trick modules. Doctrine has
carried "deep familiarity with secret permutations (Tamariz Mnemonica trainer)" as a
prior since the FG era, but **the actual artifact was never located**.

It is public. `github.com/gummikana` holds 29 repositories, several card-related:
`card-creator`, `CardCreator`, `CardBackGenerator`, `ColdWar_CardGame`, `NoMoreMeat`,
`NoMoreMoney`, `MonteCarlo_NoMoreMoney`, `CombinatorialsAbstractGame`, and
**`MemoBinTester`**.

---

## 1. The artifact, verified

`MemoBinTester/workdir/` contains `mnemonica.txt`, `mnemonica_orig.txt` (byte-identical)
and `mnemonica_test.txt`. The stack is written in Finnish suit notation — `ri` risti
(clubs), `he` hertta (hearts), `ru` ruutu (diamonds), `pa` pata (spades):

```
ri4 he2 ru7 ri3 he4 ru6 pa1 he5 pa9 pa2 he12 ru3 ri12 he8 ...
```

Checked against the published Tamariz order — 4C, 2H, 7D, 3C, 4H, 6D, AS, 5H, 9S, 2S,
QH, 3D, QC, 8H — **all 52 match.** This is the genuine Mnemonica stack, written down by
the author himself.

**The highest-provenance ordering candidate the project has ever had.**

---

## 2. What the tool actually does — and why it matters

```cpp
int GetAsNum( const std::vector<bool>& memo_deck, int p0, int p1, int p2 )
{
    p0 %= size; p1 %= size; p2 %= size;
    return (memo_deck[p0] ? 1:0) | (memo_deck[p1] ? 2:0) | (memo_deck[p2] ? 4:0);
}
```

`FindHelpers()` converts Mnemonica to a red/black bit sequence, then searches **all
triples of offsets** `(i,j,k)` such that reading those three positions across **eight
consecutive cuts** yields eight **distinct** 3-bit values, reporting any triple with
zero duplicates.

That is a **de Bruijn-style locator**: determine the cut position from three cards.

**The architecture is the eye messages'.** A cyclic sequence, read at three offsets,
combined positionally into a value, with the values required distinct. Substitute
5-valued elements for binary and three positions give 0–124 — of which 83 are used,
which is the eye trigram space exactly.

This is the clearest window into the author's design vocabulary the project has
obtained, and it was sitting in a public repo.

---

## 3. The prediction, and its failure

The architecture makes a hard prediction: **values read off a cyclic deck of size P
make the output stream periodic with period P.** Periodicity has been tested at 2–12
(FR56) and 13–30 (FR87). Never at deck sizes.

Coset IoC at periods 31–90:

```
p = 52 (deck size)     z = -0.01
p = 51, 53             z = -0.42, +0.47
p = 83 (alphabet)      z = -0.23
best in range: p = 79  z = +2.21,  max-statistic corrected P = 0.744
```

**Nothing.** Combined with FR56 and FR87, **the corpus has no periodic component at any
period from 2 to 90.**

---

## 4. Direct sweeps, also null

**Mnemonica as an alphabet.** 52 is below the proven floor of 56, so it cannot be `C`
directly, but forty lifts were swept: suit-major and rank-major canonical decks,
reversed, rank-sequence and suit-sequence orderings, embeddings at every offset 0–31,
and keyed-prefix forms — each against all 6,806 affine pre-compositions (which include
all 83 **cuts**) in both directions. **544,480 candidates, zero survivors.**

**Cut signatures** (FR90). A cut is `[A|B]` written as `[B|A]`, which against an uncut
sibling gives two shifts with a clean positional boundary. The detector recovers a
planted cut correctly and stays silent on unrelated pairs and pure shifts. Across all
36 message pairs, every sustained run sits at shift 0 — the header and near-duplicate
alignments. **No cut signature.**

**Faro shuffles** (FR90). Out-faro and in-faro on 83 cards both have order **82**, so
no small number of faros restores the deck. On 52 cards eight out-faros do, which is
why magicians use them — **the trick does not work at this deck size**, and the author
would know that immediately. 204 faro powers and mixed false-shuffle sequences,
2,776,848 candidates, zero survivors.

---

## 5. What survives from the lead

**The design-vocabulary insight.** `HasDuplicates` and `HowManyDuplicates` show the
author explicitly **searches for injective readouts** — configurations where a
positional combination yields distinct values. That is the same property the project
enforces as injectivity and packing. It is a genuine window into how he thinks, and it
corroborates the model's shape rather than any particular key.

**A verified artifact.** Mnemonica is now confirmed present, in the author's hand, and
excluded as a direct source of `C` under every lift tried.

**Unexamined repos.** `card-creator`, `CardCreator`, `CardBackGenerator`, the three
`NoMore*` games, `ColdWar_CardGame`, `CombinatorialsAbstractGame`,
`MonteCarlo_NoMoreMoney`. These are card *game* projects rather than stack tools, so
lower prior, but none has been read.

---

## 6. Model status

384 relations over 56 glyphs; injectivity clean; exposure 74.1%; residual 33.59 bits;
inventory 82.5 CI [73.0, 93.7]; determinacy threshold 81.2, unresolvable by 51×;
**no periodic component at any period 2–90**; no cut signature in any message pair.

**Cumulative sweep total: 1.37 billion candidates, zero survivors.**

---

## 7. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Mnemonica prior | carried since FG era, artifact never located | **located and verified** — `gummikana/MemoBinTester` |
| Mnemonica as `C` | untested | **EXCLUDED** across 40 lifts, 544,480 candidates |
| Periodicity | tested 2–30 | **2–90**; p=52 at z=−0.01 |
| Cut hypothesis | never tested | **no signature** in any of 36 pairs |
| Faro construction | never tested | **excluded**; also order-82 on 83 cards, so the trick fails at this size |
| Author's design vocabulary | inferred from solved puzzles (FR70) | **direct evidence** — he searches for injective positional readouts |

---

## 8. Horizon

1. **Read the remaining card repos.** Low prior, cheap, and `CardBackGenerator` in
   particular could contain a glyph or symbol generator.
2. **Acquire an anchor per component** (FR64 ordering). Unchanged, and now with every
   generator family the author is known to favour excluded.
3. **The success criterion** (FR82 §7). Unchanged.
