# Eye Crib Sweep — command reference

Automates the crib→cascade search: for every lexicon candidate at every validated
same-plaintext target, it places the crib, solves the implied partial alphabet over
GF(83), **cascades** it to decrypt the rest of that triplet, and scores the result
against a k-gram model of the lore register. Consistency gates; cascade ranks.

## Layout (repo root of github.com/Null-H3x/…)

```
eyecrib_sweep.py                 the runner
run_sweep.sh                     the campaign driver
noita_eye_core/corpus.json       the 9 messages (auto-discovered)
lexicon/
  sized_candidates.tsv           candidate plaintexts, tiered, per target length
  lore_en.txt  lore_fi.txt       corpora for the k-gram scorer
```

`corpus.json` is found automatically if it sits in `noita_eye_core/` or the repo root;
otherwise pass `--corpus PATH`.

## 1. Sanity-check the tool first (always)

```bash
python3 eyecrib_sweep.py --selftest
```

Plants a known crib in a synthetic triplet and asserts it ranks #1. If this fails,
don't trust any real run.

## 2. Single runs

```bash
# one target, highest-signal candidates only, English lore scorer
python3 eyecrib_sweep.py \
    --lexicon lexicon/sized_candidates.tsv --lore lexicon/lore_en.txt \
    --target refrain --tier 1 --top 25 --procs $(nproc)

# all five targets, English + Finnish scorers together, tiers 1-2
python3 eyecrib_sweep.py \
    --lexicon lexicon/sized_candidates.tsv \
    --lore lexicon/lore_en.txt --lore lexicon/lore_fi.txt \
    --target all --tier 2 --top 40 --procs $(nproc)
```

Flags: `--target {refrain,t3dof1,t1open,t3open,t2pass,all}` · `--tier 1|2|3` (max
candidate tier) · `--lore FILE` (repeatable) · `--top N` · `--procs N` · `--corpus PATH`
· `--lexicon PATH`.

## 3. The full campaign (automated)

```bash
./run_sweep.sh                                 # lexicon/sized_candidates.tsv, tiers 1-2
./run_sweep.sh lexicon/sized_candidates.tsv 3  # go deep, include tier-3 slop
```

Runs both lore languages × tiers × all targets, tees each run to
`runs/<timestamp>/`, and prints the strongest hits across the whole matrix at the end.

## 4. Reading the output

Columns: `score  kgram  cov  drift  target  candidate`.
- **kgram** — average log-probability per decrypted character under the lore model
  (higher/less-negative = reads more like the author). Random ≈ −3 to −4; coherent lore ≈ −1.5.
- **cov** — fraction of the triplet the crib's alphabet decrypts. A real read needs
  **high coverage AND strong kgram together** — one without the other is noise.
- **drift** — which gauge won (language lives at ±1).

A candidate worth inspecting by eye is one that jumps clear of the pack on *both* axes.
On the real corpus today, nothing does — the top guess cascades to ~17% coverage at
kgram ≈ −1.9, which is "least-bad guess," not a solve. That is the wall, seen from the
crib side; the tool is correctly reporting no read rather than inventing one.

## Performance

The search is small — a few thousand candidates × five targets × four gauges. It runs
in **minutes on your 64 threads**; there is no GPU path because there is nothing to
saturate. The limiter is lexicon quality, not compute. Widen `lexicon/` (better
author-voice phrases) before you widen the hardware.

## Honest limits

- **Single-target cascade only (v1).** The sharper filter — *joint* placement across two
  overlapping targets with the 35-symbol overlap gate — is not built yet; that's the next
  enhancement and it's what turns "permissive" into "decisive."
- **Bets on lore-in-voice under the clock/language branch.** If the body is high-entropy
  under the static reading, no crib cascades regardless of lexicon.
- **Ranking, not proof.** A #1 rank means "cascades least-badly," not "correct." Verify
  the top few by eye and by re-running under the other language model.
