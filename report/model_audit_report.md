# Refrain Model Verification (paranoia audit)

*Reproduce: `python3 eyewitness/model_audit.py`. Gate: `python3 noita_eye_core/selftest.py`.*

## Question
Is the per-message-progressive model genuinely the refrain's cipher structure (licensing the dof=2 template), or a flexible fit?

## What is SOLID: the 4 instances are the same plaintext
- Isomorph significance (L=12): observed **51** vs shuffle-null 0.0±0.4, **z=117**, p=0.000. The refrain instances share a repeated-letter structure far beyond chance — they ARE the same plaintext.

## What is NOT cleanly confirmed: the specific model
- per-message-progressive consistent extent: **22** glyphs
- pure-progressive consistent extent: **21** glyphs (nearly as deep — the per-message base barely helps)
- null (random 4-windows, n=600): mean 7.8, max 30; **empirical p(null ≥ 22) = 0.0017**
- Random 4-windows that DO reach L=22 have as much or MORE over-determination than the refrain, so over-determination does not single the refrain out either.

## Verdict
- **SOLID:** the refrain is the SAME plaintext, 4×, ~22 glyphs (isomorphs z≫100; consistency special vs random extent ~7).
- **NOT proven:** that the cipher is *specifically* per-message-progressive rather than another interrelated-alphabet member. The consistency tests are passed by a flexible model and by a small fraction of random windows; pure-progressive fits nearly as well.
- **Therefore:** the refrain repeat-template (dof=2; forced-same (3,13),(4,5),(10,16)) is a **model-dependent hypothesis**, not a fact. Use it to GENERATE candidates and TEST, but do not treat a template match as confirmation by itself.

## Audit-chain status
Every claim above is backed by a self-tested module (`model_audit.selftest`, `isomorph.selftest`) and is reproducible. This link deliberately records a NEGATIVE/inconclusive result so the chain stays honest: the model is a working hypothesis, the same-plaintext refrain is established.
