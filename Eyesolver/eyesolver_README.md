# eyesolver — dual-model classical solver for the Noita Eye corpus

One engine, both candidate cipher models, seeded by the 16 gauge-invariant pins.
This is the purpose-built equivalent of running AZDecrypt / `stblake/polyalphabetic`
against the corpus: those tools are hardcoded for 26-letter alphabets and standard
key structures and cannot ingest N=83-with-scattered-embedding, so this
reimplements the same algorithm class (shotgun hill-climb + simulated annealing +
strong n-gram objective + crib anchoring) for our exact structure.

## Models

- **`static`** — the repo's reading: Quagmire-IV with a progressive/Trithemius
  key. `c_m[t] = C[(σ·E[L[t]] + base_triplet + drift·t) mod N]`; decrypt is
  vectorized. This is "AZDecrypt against the corpus."
- **`autokey`** — the community's reading: plaintext-autokey Alberti.
  `c[t] = C[(E[L[t]] + S(t)) mod N]`, `S(t) = init + Σ_{k<t} E[L[k]]`; decrypt is
  sequential (state).

Both search `q` (the 83-symbol de-drifting alphabet, seeded by pins) plus `M`
(the read map) plus params (three per-triplet bases for static / `init` for
autokey), with parallel shotgun restarts.

## The finding this tool establishes (read before running)

The selftest proves both engines are **sound** — they recover planted language
plaintext when seeded near the solution (static 63% from a 70-pin seed, autokey
54% from a 76-pin seed). But it also pins the wall: **from the 16 pins we
actually have, neither model converges** (static stays at ~8%, the random floor),
and the double-mixed search only becomes navigable at **~60 of 83 correct
q-values**. This held with the strongest objective (real 3-gram log-likelihood),
was not rescued by cribs (static: 8%→26% with a 25-char crib, no breakthrough),
and is *worse* for autokey, whose accumulating state propagates any q-error
downstream and makes the landscape more brittle, not less.

This is the Quagmire-IV / double-mixed hardness the classical literature warns
about, quantified on our structure. Practical consequence: **more compute or GPU
will not solve it from 16 pins** — the landscape, not the speed, is the block.
`eyesolver` is therefore validated and ready, and its real-corpus run is an
independent confirmation of the pin-count wall (it will not read). It becomes a
*solver* the moment pins cross ~40–60 (an external anchor, a correct crib, or the
cross-triplet-bridge densification of Field Guide 4).

## Usage

```bash
python3 eyesolver.py --selftest                       # validate engines + wall (~5 min, 4 procs)
python3 eyesolver.py --model static  --lang finnish  --restarts 64 --iters 500000
python3 eyesolver.py --model autokey --lang karelian --restarts 64
python3 eyesolver.py --model static  --lang english  --crib-file crib.tsv
```

- `--lang` ∈ {english, finnish, karelian}. LMs are built from `../corpora`
  (`english_big.txt`, `kalevala_finnish_clean.txt`, `corpus-olo/…` for Karelian).
- `--restarts` scales across CPUs (`--procs` to cap). On a 64-core box, run
  `--restarts 64 --iters 500000` per language×model; each restart is independent.
- `--crib-file` is a TSV of `position<TAB>letter` lines; the objective rewards
  crib agreement (AZDecrypt-style anchoring — plug candidate cribs from
  `jointcrib`). Cribs help only marginally from 16 pins, but a *correct* full-span
  crib effectively raises the seed and is the intended bridge.
- `--k 4` uses 4-gram scoring (stronger, slower); default 3.

## How to read the output

Each run prints the language **reference score** (what real text of that language
scores) and the best decrypt's score. A genuine read lands near the reference; a
16-pin run lands well short and prints `no read (expected)`. Do not over-read a
score modestly above the random floor — that is fluent-gibberish, the classic
hill-climb trap, not plaintext. Confirm any candidate by eye and by the
crib/overlap gates before believing it.

## Placement

Drop `eyesolver.py` into a new folder at the repo root (e.g. `Eyesolver/`). It is
**self-contained**: it needs no other repo modules to run on the real corpus.

- **Corpora** are found automatically — `find_corpora()` searches the script dir,
  its parents, and the CWD for a folder containing `english_big.txt` (or
  `corpus-olo/` for Karelian). If your corpora live elsewhere, pass
  `--corpora <dir>`. A missing corpus now prints a clear, actionable error naming
  the exact file and where it looked, instead of a raw traceback.
- **`corpus.json`** is auto-discovered under `noita_eye_core/` or the CWD; override
  with `--corpus <path>`.
- **Pins** come from `iso_relax` if it happens to be importable, otherwise from a
  hardcoded `KNOWN_PINS` constant (the 16 gauge-invariant pins) — so the tool
  runs even if the rest of the repo isn't on the path. Override with
  `--pins-file` (TSV: `symbol<TAB>position`) when you have more pins.

So the minimal footprint is just `eyesolver.py` + a `corpora/` folder reachable
up-tree (or via `--corpora`). Everything else is optional.

## Honest expectations

This tool will not, by itself, read the eyes today — and that outcome is
information, not failure: it converts "a strong solver might crack it" from a
hope into a quantified *no* at 16 pins, consistent with every other line of this
investigation. Its value is (1) a validated, hardware-ready solver for the moment
pins cross the threshold, (2) the only in-repo test of the community's autokey
model on the strong-objective footing, and (3) a fast way to burn candidate cribs
and languages: if a *correct* crib exists, feeding it here is how you would find
out, because a correct crib plus the pins is what crosses the wall.
