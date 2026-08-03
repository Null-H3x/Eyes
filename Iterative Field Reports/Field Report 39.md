# Field Report 39 — The Ledger Was Not Empty

**Series note.** Thirty-ninth report of the EYESPIRAL series. FR38 recorded that no
unexecuted internal structural items remained and that every route now needed external
input. This cycle challenges that verdict, finds it wrong, and runs the measurement it had
written off. Instrument `eyepool2.py`, selftest 5/5 green.

**Scope constraint (given).** Isomorphs untouched; repo machinery unmodified;
read-only throughout.

**One-paragraph verdict.** FR36 declared the scattered-alphabet variant of branch B
blocked, on the grounds that resolving it needed roughly four times FR30's sample and that
FR31, FR34 and FR35 had closed every route to more component coverage. That reasoning
assumed **within-block pairs only**, and it should not have. For two positions in the same
component but different messages, a plaintext coincidence requires
drift·(v − v′) = base difference = drift·w, hence **v − v′ = w — drift-free**, with w
supplied by the seven forced base differences FR32 established. Cross-message pairs are
therefore testable, and they take the sample from 3,233 to **6,384 pairs** without any new
coverage. Pooled naively the channel runs hot, and the reason is a confound worth the
cycle on its own: **85% of East 1 / West 1's coincidences and 90% of East 4 / East 5's sit
at shift zero** — those two pairs are the corpus's near-duplicates, and what the channel
is counting there is shared passages, not token frequency. Excluding them, the
measurement is **flat: 72 coincidences against an empirical null of 77.0 ± 8.9,
z = −0.56**, with power to detect an effective alphabet of 60 at 3.3σ. Combined with
FR36's clustering test, which excluded small *contiguous* alphabets at the same scale,
**the plaintext effective alphabet exceeds roughly 60 however the tokens are numbered.**

---

## 1. Corrections first

**FR38's "ledger empty" verdict was wrong**, and it was my verdict. The scattered-alphabet
question was recorded as blocked by a coverage requirement that could not be met. It was
blocked by an unexamined assumption about which pairs are comparable. Cross-message
comparison inside a component is drift-free for exactly the same reason the within-block
version is, and the constant it needs was already sitting in FR32's table of forced base
differences.

**A threshold I set too tightly, caught by the gate.** I pre-registered that pooling must
more than double the sample; it multiplies it by 1.97. The check failed, correctly, and
the fix was to state the measured ratio rather than a round number chosen in advance.

## 2. P1–P2 — the sample, and the confound

| channel | pairs |
|---|---|
| within-block only (FR30) | 3,233 |
| + cross-message, all pairs | 7,303 |
| **+ cross-message, near-duplicates dropped** | **6,384 (2.0×)** |

Coincidences by positional shift, which is what exposes the confound:

| pair | hits | pairs | flat | top shift | share at top |
|---|---|---|---|---|---|
| **East 1 / West 1** | 20 | 519 | 6.3 | **0** | **85%** |
| **East 4 / East 5** | 20 | 400 | 4.8 | **0** | **90%** |
| East 1 / East 2 | 11 | 664 | 8.0 | −108 | 9% |
| West 1 / East 2 | 6 | 401 | 4.8 | −103 | 17% |
| East 3 / West 3 | 17 | 1308 | 15.8 | 54 | 18% |
| East 4 / West 4 | 4 | 459 | 5.5 | −119 | 25% |
| West 4 / East 5 | 2 | 319 | 3.8 | 0 | 50% |

The two near-duplicate pairs put nearly all their coincidences at a single shift. That is
shared plaintext — the near-duplicate structure the corpus has been known to have since
the doctrine's earliest agreement statistics — and counting it as token-frequency evidence
would have inflated the result by a factor of 1.6. Excluded.

## 3. P3–P4 — the measurement

| quantity | value |
|---|---|
| pairs | 6,384 |
| coincidences | 72 |
| empirical null | 77.0 ± 8.87 |
| **z** | **−0.56** |
| IoC-style effective alphabet | 88.7 |

Power at this sample:

| effective alphabet | expected | z |
|---|---|---|
| 79 | 80.8 | +0.43 |
| 70 | 91.2 | +1.60 |
| 65 | 98.2 | +2.39 |
| **60** | **106.4** | **+3.32** |
| 50 | 127.7 | +5.71 |

An effective alphabet of 60 or below would show at better than three sigma. It does not.

## 4. P5 — what this settles, and what it costs

FR36 excluded a small **contiguous** plaintext alphabet by a clustering statistic. This
cycle excludes a small **scattered** one by a coincidence statistic, at the same scale and
by an unrelated mechanism. Together:

> **The plaintext effective alphabet exceeds roughly 60, however the tokens are
> numbered.**

That is the A-vs-B fork narrowed about as far as internal evidence can take it. Branch B
survives only in the form of a token stream with a very large inventory — which is
possible, but is not the version that would help.

**The consequence for the endgame is unwelcome and should be stated plainly.** FR19
measured the residual gap *shape* and found it favourable: with 74% of positions exposed,
the unknowns are mostly isolated single positions between known runs. FR19 was careful to
say that shape buys readability only under branch B. With the inventory now known to
exceed 60, **context will not fill those gaps**. The favourable shape does not convert
into readable text.

**Caveat.** This measures the plaintext as the current model reconstructs it, and remains
conditional on repair A — the assumption that E1@68 is spurious — which FR37 and FR38
strengthened but did not prove.

## 5. Where the programme stands

- **384 relations over 56 glyphs**, components 25/11/7/3 plus five pairs, injectivity
  clean, 74.1% exposure, drift unpinned.
- **A-vs-B substantially resolved** against the readable branch: alphabet > ~60 both
  contiguous and scattered.
- **Every internal structural route closed** — this cycle reopened one and closed it
  properly, which is a better outcome than leaving it recorded as impossible.
- **Acquisition remains the lever**, and its value is now clearer: anchors would deliver
  the alphabet, not a reading.

## 6. Horizon

(1) **Re-examine what "solved" means for this corpus.** If the plaintext inventory exceeds
60 over 83 symbols, recovering C yields a token stream that is not natural language, and
the project's success criterion should be restated accordingly — that is a doctrine
question, not a measurement. (2) **The remaining measurable quantity is the drift**, and
it needs two external anchors in component 1. (3) H1 predicts drift 31 and becomes a
genuine test the moment an anchor arrives.

## 7. Reproduction

`eyepool2.py` (repo checkout; `EYE_CORPUS`/`EYE_ATLAS` overrides): `--selftest` runs the
5-check gate — the cross-message identity proved drift-free on synthetic data with
everything known, the near-duplicate confound detected at shift 0, pooling shown to
enlarge the sample by the measured ratio, a planted small alphabet detected, and the
baseline guard. The full run reproduces P1–P5. Failures carry prefix
`XD-MBYG04K-URS3LF`.
