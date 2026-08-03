# Field Report 29 — The Offset Structure, and One Fact That Survives the Drift

**Series note.** Twenty-ninth report of the EYESPIRAL series. FR28 re-derived the alphabet
exclusions on repaired evidence and left the T3 opening as the last contradiction. This
cycle gives the *offset* structure the same treatment, explains FR26's unexplained
asymmetry, and produces the series' first determination that does not depend on the
drift. Instrument `eyebase.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR9's base-equality matrix — which messages may share an offset
— is load-bearing for the whole series and was computed against the pool now known to
assert six falsehoods. Rebuilt under repair A, its **twelve prohibitions collapse to
one**: East 3 and West 3 may not share an offset; every other pair may. That explains T2's
triple failure, but **not T3's**, whose pairs are all permitted — so its failure is
genuinely three-way, exactly as FR28 found. The mechanism is now visible: the pool forces
base differences, and once any two T3 messages are merged the third is forced a specific
**nonzero** distance away (58, 54, 58 depending on the pair). T1 behaves oppositely —
merging E1 and W1 leaves E2's offset **free**, which is why T1's opening is accommodated
and T3's is not. That is FR26's asymmetry, explained. And two base differences are forced
outright, one of which is the cycle's headline: **base[W1] − base[E1] = 0 at every one of
the drifts tested** — the first drift-invariant determination in twenty-nine cycles, and
an independent confirmation of FR14's literal-run evidence (E1/W1 share a body run of
length 13, chance 5 × 10⁻²⁵) arrived at from the constraint side rather than the
statistical one. Two disjoint routes, one fact.

---

## 1. Why the matrix needed rebuilding

FR9 established which messages may share an offset, and that matrix has been quoted
throughout the series — it drove the FR9 gauge theorem, FR10's trilemma, FR11's offset
test and FR14's body-internal contradiction. It was computed on the unrepaired pool.
FR28 re-derived the alphabet exclusions for exactly this reason; the offset structure had
the same inheritance problem and had not been revisited.

## 2. B1–B2 — the matrix collapses

| | unrepaired pool (FR9) | repair A |
|---|---|---|
| forbidden within-triplet | E1/E2, W1/E2, E3/W3, E4/W4, E4/E5, W4/E5 | **E3/W3 only** |
| forbidden cross-triplet | T1 trio vs E3 and W3 (6 pairs) | **none** |

Triple merges — can a whole triplet share one offset?

| triplet | satisfiable drifts |
|---|---|
| T1 (E1, W1, E2) | **82/82** |
| T2 (W2, E3, W3) | 0/82 |
| T3 (E4, W4, E5) | 0/82 |

T2's failure follows immediately from the E3/W3 prohibition. **T3's does not** — every one
of its pairs is permitted, so nothing pairwise explains it.

## 3. B3 — forced base differences, and one that survives the drift

Two base differences are forced by the pool:

| drift | base[W1] − base[E1] | base[W3] − base[E3] |
|---|---|---|
| 1 | **0** | 54 |
| 2 | **0** | 25 |
| 3 | **0** | 79 |
| 7 | **0** | 46 |
| 17 | **0** | 5 |
| 41 | **0** | 56 |
| 82 | **0** | 29 |

**base[W1] − base[E1] = 0 at every drift.** Everything the series has determined until now
has been drift-conditional — FR26 found not one of its 223 relations survived a change of
drift. This one does, because zero is a fixed point of the drift's action on it.

It also matters *what* it says. FR14 established that E1 and W1 share an offset by a
completely different route: literal body runs of length 13 and 4, priced at 5 × 10⁻²⁵
against an empirical null of zero such runs among all 27 cross-triplet pairs. That was a
statistical argument outside the constraint machinery. This is a constraint-side proof of
the same fact. **Two disjoint methods, one conclusion** — which is the strongest form of
corroboration available in this project, and the standard FR14 itself set when it warned
that a result derived entirely inside one framework can be blamed on the framework.

base[W3] − base[E3] is also forced, but drift-dependent and nonzero at every drift — which
*is* the E3/W3 prohibition.

## 4. B4 — the T3 mechanism, and FR26's asymmetry explained

| merge imposed | consequence |
|---|---|
| base[E4] = base[W4] | base[E5] − base[E4] forced to **58** |
| base[E4] = base[E5] | base[W4] − base[E4] forced to **54** |
| base[W4] = base[E5] | base[E4] − base[W4] forced to **58** |
| **control:** base[E1] = base[W1] | base[E2] − base[E1] **FREE** |

In T3, merging any two messages forces the third a nonzero distance away, so the triple
is structurally blocked. In T1, the third message is *free*, so the triple is
accommodated. **That is precisely the asymmetry FR26 flagged and could not explain**: it
is not a property of the openings but of how tightly each triplet's messages are coupled
by the body evidence.

## 5. B5 — what removes the last contradiction

| configuration | satisfiable drifts |
|---|---|
| pool + evidence-forced E4/E5 merge, T3 opening not imposed | **82/82** |
| same, with the T3 opening imposed as shared plaintext | 0/82 |

Reading the T3 opening as **literal stamped material rather than encrypted shared
plaintext** removes the last contradiction entirely, leaving a fully consistent model.
That is a hypothesis that fits, not a proof that it holds — and it is worth noting what it
does *not* revive: FR14 showed the same reading does nothing for the body-internal
contradiction, which repair A resolves on other grounds.

## 6. Where the model stands

Everything the series has, with its conditionality:

- **Per-message bases, per-triplet keystreams** — established.
- **base[W1] = base[E1]** — **drift-invariant**, confirmed by two disjoint methods.
- **base[E4] = base[E5]** — forced by literal body runs (evidence-side), and admissible
  under repair A.
- **base[E3] ≠ base[W3]** — forced, the only surviving prohibition.
- **223 alphabet relations** in components of 19/7/7/3/3 — conditional on repair A and a
  fixed drift.
- **One contradiction**, dissolvable by reading T3's opening as stamped material.

## 7. Horizon

(1) **The E1/W1 result deserves extension**: it is drift-invariant because zero is a fixed
point, so the natural question is whether any *nonzero* relation is invariant under some
subgroup of drifts — a smaller ambiguity than 82-fold would be real progress.
(2) **Test the stamped-header hypothesis directly**: if T3's opening is literal material
rather than ciphertext of shared plaintext, its glyphs should behave differently from body
glyphs under some measurable statistic, and the T1/T3 asymmetry gives a built-in control.
(3) Standing: the 15 candidate glyphs want a non-isomorph constraint form; #2⁻'s
instance-level audit.

## 8. Reproduction

`eyebase.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate on a synthetic corpus with known offsets — no forced nonzero difference
inside a triplet whose offsets are truly equal, merging equal-offset messages stays
satisfiable, a forced zero difference stays zero across drifts, plus the baseline guard.
The full run reproduces B1's matrix, B2's triple merges, B3's forced differences with the
drift sweep, B4's mechanism with its T1 control, and B5. Failures carry prefix
`XD-MBYG04K-URS3LF`.
