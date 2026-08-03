# Field Report 75 — T2'S DEPTH IS HEADER-ONLY: THE TRIPLET PREMISE IS NOT UNIFORM

*Instrument: `eyetriplet` (3/3 selftests, separation demonstrated within one corpus). July 2026.*
*Cycle: EYESPIRAL. Negatives and self-corrections first.*

---

## 0. CHALLENGE I — a premise verified pooled, never decomposed

FR65 audited the per-triplet keystream premise and reported **within z = +12.47,
cross z = +1.26**. That was computed **pooled across all three triplets**, and it has
never been decomposed.

Two prior observations should have prompted this earlier. **West 2 is uncoupled** —
FR35 by free-w scan, FR73 by base-group connectivity, FR74 by bridge scan, three
independent methods. And **East 3 / West 3 is the weakest pair in the corpus** at 7.8%
agreement against 44.4% and 27.2%, and was the one forced relation FR74's scan failed
to recover.

Both anomalies sit in **T2**. A pooled statistic can carry a failing member.

---

## 1. Result

Aligned coincidence per triplet, against a within-message unigram-preserving null
(3,000 draws):

| triplet | all positions | **body (pos ≥ 24)** |
|---|---:|---:|
| T1 — East1+West1+East2 | +44.07 | **+13.86** |
| **T2 — West2+East3+West3** | **+9.17** | **+0.07** |
| T3 — East4+West4+East5 | +35.29 | **+7.42** |

**T2's apparent depth is entirely the shared header.** With the opening included it
reads z = +9.17; on body positions it is **+0.07** — 3 coincidences against a null of
2.9, indistinguishable from noise.

Pairwise on body positions:

| pair | rate | z | |
|---|---:|---:|---|
| East 1 / West 1 | 0.2800 | **+18.36** | strong |
| East 4 / East 5 | 0.1222 | **+8.71** | strong |
| West 4 / East 5 | 0.0556 | **+3.67** | strong |
| East 1 / East 2 | 0.0533 | +2.77 | marginal |
| West 1 / East 2 | 0.0506 | +2.66 | marginal |
| East 4 / West 4 | 0.0211 | +0.63 | nothing |
| West 2 / West 3 | 0.0256 | +1.11 | nothing |
| East 3 / West 3 | 0.0100 | −0.05 | nothing |
| West 2 / East 3 | 0.0000 | −0.95 | nothing |

**Only three of nine within-triplet pairs show body-level sharing above threshold.**
All three of T2's pairs show none.

---

## 2. What this does and does not establish

**Stated carefully, because the distinction matters.**

The statistic measures **shared plaintext at aligned positions**, not keystream
sharing as such. Two messages could share a keystream perfectly and carry entirely
different plaintext, in which case coincidence sits at chance and this test sees
nothing. So **T2 is not shown to lack a shared keystream.**

What *is* shown is sharper than that, and worse for the premise:

> This coincidence statistic **is** the evidence the doctrine used to establish
> per-triplet keystreams (scoreboard: *"only within-triplet pairs are in depth, cross
> z = −0.5, within z = 14.6"*). On body positions, T2 supplies **none of it**.

T2's entire contribution to that figure comes from the shared opening. And by A4 —
adopted in FR29, used in FR33 and FR44 — **the openings are stamped literal material,
not encrypted.** Stamped glyphs carry no keystream information whatever. So the only
evidence placing W2, E3 and W3 in a common keystream is evidence that, under the
project's own reading, cannot bear on keystreams at all.

**The per-triplet premise is well supported for T1 and T3, and unsupported for T2.**

---

## 3. Consequences

**A. The triplet count may be wrong.** If T2 is not a keystream group, the corpus has
two depth groups plus three loose messages, not three triplets. Nothing in the
skeleton depends on T2's grouping directly — the 384 relations come from certified
isomorphs, and FR49 showed T2 contributes almost nothing to them — but the depth model
does.

**B. FR32's forced `base[W3] − base[E3] = 54` now has thin support.** FR74's scan
failed to recover it (peak 3, wrong value). This cycle finds no body sharing for that
pair. The relation survives in the constraint system but has no independent passage or
coincidence evidence behind it. It should be flagged, not withdrawn.

**C. T1 and T3 are also less uniform than "within z = 14.6" implies.** Within T1, only
E1/W1 clears threshold; E2's linkage is marginal at +2.77 and +2.66. Within T3, E4/W4
shows +0.63 — nothing — and the triplet is held together by E4/E5 and W4/E5. The
doctrine's odd-message-out structure (E2, W4) is visible here as *weak linkage* rather
than as difference in kind.

**D. It does not change the bit accounting.** T2's messages already sit in separate
base groups (W2 alone, E3+W3 together) per FR73, so the 19.13 bits are unaffected. If
E3/W3's forced difference were withdrawn they would split further, **raising** the cost
to 25.5 bits.

---

## 4. Model status

384 relations over 56 glyphs; components 25/11/7/3 plus five pairs; injectivity clean;
exposure 74.1%; alphabet ambiguity 14.46 bits; message-base ambiguity 19.13 bits; total
33.59 bits; alphabet size proven in [56, 83]. **Per-triplet keystream premise now
supported for T1 and T3 only.**

**Cumulative sweep total: 193.6 million candidates, zero survivors.**

---

## 5. Doctrine changes

| Item | Prior status | Status now |
|---|---|---|
| Per-triplet keystream premise | [MEASURED], pooled z = +12.47 | **T1 +13.86, T3 +7.42, T2 +0.07** — unsupported for T2 |
| T2's depth evidence | assumed comparable to T1/T3 | **header-only**, and the header is stamped (A4) |
| Within-triplet uniformity | implied by pooled figure | **3 of 9 pairs** clear threshold on body positions |
| `base[W3] − base[E3] = 54` | forced (FR32) | **flagged** — no passage (FR74) or coincidence (FR75) support |
| E4/W4 linkage | member of T3 | z = +0.63 on body — T3 is held by E4/E5 and W4/E5 |
| Bit accounting | 33.59 bits | unchanged; would **rise to 25.5** base-bits if E3/W3 is withdrawn |

---

## 6. Horizon

1. **Re-derive the triplet assignment from body evidence alone.** The current grouping
   was established on a statistic that includes the stamped header. Redone on body
   positions, the natural grouping may be two depth groups plus loose messages. This is
   internal, cheap, and now clearly warranted.
2. **Audit what else was measured with the header included.** FR65 flagged that the
   "body agree" column in the keyspace ledger is computed over full messages. This
   cycle shows that choice can invert a verdict, not merely shift a number.
3. **One crib in West 2** (FR74). Unchanged, still the cheapest external unit.
4. **The success criterion** (FR66, FR72, FR73). Unchanged, still prior to everything.
