# Field Report 11 — Where the Keystream Cancels

**Series note.** Eleventh report of the iterative series. This cycle takes up FR10's
horizon item 1 — discriminate premises (i) and (iii) — finds that FR10's *nominated*
discriminator does not work, corrects FR10's pricing of the trilemma in the process,
and reaches the discrimination by a different route that touches none of the
constraint machinery. Instrument `eyeoffset.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR10 proposed comparing what gets certified under the two
surviving readings. It does not discriminate: both certify the same ten symbols, and
under the Gromark reading **all fifty-one solution symbols collapse to a single
value** — the certification is vacuous, and adding the openings changes nothing. That
forces a correction to FR10: the reading that resolves the opening/body contradiction
is the free-per-shift-constant regime, i.e. the scoreboard's PERMISSIVE corner, and
it buys consistency by destroying every determination the project has. Premise (iii)
is not "cheapest" in the form tested. The discrimination instead arrives from a
statistic that never touches the solver. Because a literal same-position comparison
between two messages of one triplet **cancels the keystream exactly**, agreement
depends only on whether the plaintext difference equals the offset gap — so equal
offsets make literal agreement equal plaintext agreement, while distinct offsets
force it to chance no matter how much text the two messages share. Cross-triplet
pairs supply the empirical baseline (×1.11 of 1/83). Against it, **East 4 / East 5
agree at 9.2× baseline, p = 3.5 × 10⁻⁸, clearing a pre-registered Bonferroni bar** —
and E4/E5 is one of the six pairs that per-message progressive *forbids* from sharing
an offset. Progressive is now contradicted from outside the machinery that first
contradicted it.

---

## 1. Corrections and negatives first

**FR10's nominated discriminator fails, and I am reporting that before the result
that worked.** FR10 predicted that under premise (iii) the openings become plaintext,
so within-triplet shared offsets would show up as extra certification. They do not.
Under Gromark rows the openings are exact Δ = 0 pairs whose rows constrain only the
base variables, not symbols, so they add nothing; and the free per-(triplet, p1, p2)
constants absorb so much that the solution degenerates — 51 symbols, **one** distinct
value. Certified count is 10 in both readings, but under Gromark all ten values
collide, pin-grade 0. A reading that fits by absorbing rather than determining cannot
be compared to one that determines.

**Which corrects FR10's trilemma pricing.** FR10 called premise (iii) the cheapest to
drop. On the evidence here, the specific model that resolves the contradiction — free
constants per shift — is exactly the PERMISSIVE regime the scoreboard already flags,
and adopting it costs the entire pin inventory. The honest restatement: *general-K in
its unconstrained form resolves the contradiction and certifies nothing.* A genuinely
constrained Gromark (an actual primer-generated recurrence, where the shift constants
are not free but determined) is **untested here** and is the real open option — it
sits between linear progressive and free-delta, and nothing in this series has yet
probed it.

**My own probe over-read the agreement table.** Eyeballing uncorrected rates, I saw
four elevated within-triplet pairs. Under the pre-registered Bonferroni correction
(α = 0.01 across nine within-triplet pairs, bar 1.11 × 10⁻³) only **one** survives:
E4/E5. W4/E5 (×4.19, p = 7.1 × 10⁻³) misses the bar and is logged watch-grade; E1/E2
(×3.02) and W1/E2 (×2.87) sit at baseline. The correction was registered before the
corpus run, which is the only reason the walk-back is cheap.

## 2. The mechanism

For two messages of one triplet, with a shared keystream K_g,

  c₁[t] = C[(p₁[t] + off₁ + K_g[t]) mod 83],  c₂[t] = C[(p₂[t] + off₂ + K_g[t]) mod 83]

so **c₁[t] = c₂[t] ⟺ p₁[t] − p₂[t] = off₂ − off₁.** The keystream cancels exactly.
This holds under *any* K — progressive, Gromark, general — and independently of drift
and of the alphabet C. Two clean consequences: with equal offsets, literal agreement
*is* plaintext agreement, which for a near-duplicate pair is large; with distinct
offsets, agreement requires the plaintext to differ by the same nonzero constant at
every agreeing position, which for arbitrary text is chance. Cross-triplet pairs share
neither keystream nor offset and give the empirical baseline, already absorbing
unigram skew.

The selftest gates both directions on plants: with shared offsets and 30% shared body
plaintext, agreement comes out at 0.313; with the *same* 30% shared plaintext and
distinct offsets, agreement is **0.000**. That negative control is the whole argument
in miniature.

## 3. Result

Cross-triplet baseline: 30/2236 = 0.01342 (×1.11 of 1/83). Body positions only
(t ≥ 25); the disputed opening spans are excluded throughout.

| pair | FR9 verdict | agree / n | × baseline | p | verdict |
|---|---|---|---|---|---|
| East 1 / West 1 | permitted | 20 / 74 | 20.14 | 1.1e-20 | elevated (consistent) |
| **East 4 / East 5** | **FORBIDDEN** | **11 / 89** | **9.21** | **3.5e-08** | **conflicts with progressive** |
| West 4 / East 5 | FORBIDDEN | 5 / 89 | 4.19 | 7.1e-03 | watch-grade (misses bar) |
| East 1 / East 2 | FORBIDDEN | 3 / 74 | 3.02 | 7.8e-02 | at baseline |
| West 1 / East 2 | FORBIDDEN | 3 / 78 | 2.87 | 8.8e-02 | at baseline |
| West 2 / West 3 | permitted | 2 / 77 | 1.94 | 2.8e-01 | at baseline |
| East 4 / West 4 | FORBIDDEN | 1 / 94 | 0.79 | 7.2e-01 | at baseline |
| East 3 / West 3 | FORBIDDEN | 1 / 99 | 0.75 | 7.4e-01 | at baseline |
| West 2 / East 3 | permitted | 0 / 77 | 0.00 | 1.0e+00 | at baseline |

E1/W1 is the positive control: a pair FR9's matrix permits to share an offset, and the
statistic finds it 20× elevated, as it must. E4/E5 is the finding: 11 body positions
agreeing literally where 1.2 are expected. Under the forced-distinct offsets that
per-message progressive requires, each of those eleven would need p[E4] − p[E5] to hit
the same nonzero constant.

Pairs sitting at baseline are **not** evidence for distinct offsets — two messages
with equal offsets and little shared body plaintext also agree at chance. The test is
one-sided by construction: elevation is informative, quiet is not.

## 4. What this does and does not settle

**Does:** E4 and E5 share an effective offset, on evidence that is independent of the
keystream model, the drift, the alphabet, and the entire consensus/GF machinery that
produced FR9's and FR10's contradictions. Per-message progressive forbids exactly
that. So the contradiction FR9 found is corroborated by a second, methodologically
disjoint route — which matters, because a contradiction derived solely inside one
constraint framework can always be blamed on the framework.

**Does not:** identify the replacement. The unconstrained general-K that resolves the
contradiction is vacuous (§1). The result constrains any successor model rather than
selecting one: whatever K turns out to be, **E4 and E5 must come out with equal
effective offsets**, and that is now a positive, quantified requirement rather than a
modelling choice.

**Unaffected:** FR7's sound rows, FR8's collapse theorem, FR9's gauge theorem and
matrix, FR10's cores and class-reality null. The per-message certifications remain the
only non-degenerate ones in play.

## 5. Horizon

(1) **Constrained Gromark is the untested middle.** Build rows where the shift
constants are generated by a two-number primer recurrence rather than left free, and
re-run FR10's model test and this cycle's certification comparison; that is the only
version of premise (iii) that could resolve the contradiction *without* going vacuous.
(2) **Extend the agreement statistic to the openings themselves** — the disputed spans
were excluded here by design; under premise (i) they are not plaintext, which is a
testable asymmetry against the body. (3) **W4/E5 watch-grade item**: it wants either
more power or a pre-registered one-pair test next cycle, not a second look at the same
data. (4) Standing: FR8's bridge-symbol search, anchor calibration (rep = 4).

## 6. Reproduction

`eyeoffset.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs
the 5-check gate — shared-offset detection, the cross-keystream control, the
distinct-offset negative control (identical plaintext must give chance agreement), the
separation check, and a binomial-tail sanity test. The full run reproduces the baseline
guard, the cross-triplet baseline, the agreement table with Bonferroni verdicts, the
plaintext requirement implied by distinct offsets, and the certification comparison
with its degeneracy diagnostic. Failures carry prefix `XD-MBYG04K-URS3LF`. The
agreement counts are checkable directly from the corpus with a two-line loop.
