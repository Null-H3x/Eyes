#!/usr/bin/env bash
# eyecrib campaign driver — runs the crib->cascade sweep across the full matrix
#   (both lore languages x tiers 1..MAXTIER x all targets), logs each run, then
#   collects the strongest hits. Put this next to eyecrib_sweep.py at the repo root.
#
# usage:  ./run_sweep.sh [lexicon.tsv] [max_tier]
#   ./run_sweep.sh                                  # defaults: lexicon/sized_candidates.tsv, tier<=2
#   ./run_sweep.sh lexicon/sized_candidates.tsv 3   # go deep (include tier-3 window slop)
set -euo pipefail
LEX="${1:-lexicon/sized_candidates.tsv}"
MAXTIER="${2:-2}"
PROCS="$(nproc 2>/dev/null || echo 8)"
STAMP="$(date +%Y%m%d-%H%M%S)"; OUT="runs/${STAMP}"; mkdir -p "${OUT}"
echo "lexicon=${LEX}  max_tier=${MAXTIER}  procs=${PROCS}  out=${OUT}"

for LORE in lexicon/lore_en.txt lexicon/lore_fi.txt; do
  [ -f "${LORE}" ] || continue
  TAG="$(basename "${LORE}" .txt)"
  for TIER in $(seq 1 "${MAXTIER}"); do
    echo ">>> lore=${TAG}  tier=${TIER}"
    python3 eyecrib_sweep.py \
        --lexicon "${LEX}" --lore "${LORE}" \
        --target all --tier "${TIER}" --top 40 --procs "${PROCS}" \
      | tee "${OUT}/sweep_${TAG}_tier${TIER}.txt"
  done
done
echo "campaign complete -> ${OUT}"
echo "=== strongest hits across every run (sort by score) ==="
grep -hE '^[[:space:]]*-?[0-9]+\.[0-9]' "${OUT}"/*.txt | sort -k1 -g -r | head -25 || true
