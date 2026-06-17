#!/usr/bin/env bash
#
# salakieli_sweep.sh — run the strongest salakieli cribs across all nine eye
# messages on the GPU, asking the globality question for each.
#
# For every (crib, message) it sweeps a position window x all generators x the
# seed range; a crib whose seed decrypts ALL nine messages to structure is a
# GLOBAL keystream hit (and a confirmed plaintext). Results + per-run logs land
# in $OUTDIR; any global hit is echoed and collected in summary.txt.
#
# USAGE
#   ./salakieli_sweep.sh                      # defaults below
#   NUM_CRIBS=10 POS_END=40 ./salakieli_sweep.sh
#   SEED_END=4294967295 ./salakieli_sweep.sh  # full 32-bit seed space
#   CRIBS="threeeyesarewatchingyou allseeing" ./salakieli_sweep.sh   # explicit
#
# TUNABLES (env overrides):
#   PYTHON      interpreter (default: the EyeStat venv that has CuPy)
#   SEED_END    seeds per cell (default 100000000)
#   POS_START   / POS_END   crib-start sweep window (default 3..25)
#   GENERATORS  'all' or comma list (default all)
#   NUM_CRIBS   how many strongest register cribs to use (default 6)
#   CRIBS       explicit space-separated cribs (overrides NUM_CRIBS)
#   OUTDIR      results dir (default salakieli_sweep_results)

# Re-exec under bash if launched via `sh` / dash.
if [ -z "${BASH_VERSION:-}" ]; then exec bash "$0" "$@"; fi
set -uo pipefail   # NOT -e: one failing run must not abort the whole sweep

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"
CORE="$DIR/../noita_eye_core"

PYTHON="${PYTHON:-$HOME/.venvs/eyestat/bin/python3}"
[ -x "$PYTHON" ] || PYTHON="$(command -v python3)"
SEED_END="${SEED_END:-100000000}"
POS_START="${POS_START:-3}"
POS_END="${POS_END:-25}"
GENERATORS="${GENERATORS:-all}"
NUM_CRIBS="${NUM_CRIBS:-6}"
OUTDIR="${OUTDIR:-salakieli_sweep_results}"
mkdir -p "$OUTDIR"

MESSAGES=("East 1" "West 1" "East 2" "West 2" "East 3" \
          "West 3" "East 4" "West 4" "East 5")

# Strongest cribs straight from the register (kept in sync with salakieli.py),
# unless CRIBS is given explicitly.
if [ -z "${CRIBS:-}" ]; then
    CRIBS="$("$PYTHON" -c "import sys;sys.path.insert(0,'$CORE');import salakieli;\
print('\n'.join(w for w,_,_ in salakieli.ranked()[:$NUM_CRIBS]))")"
else
    CRIBS="$(printf '%s\n' $CRIBS)"
fi

echo "=================================================================="
echo " salakieli GPU sweep"
echo "=================================================================="
echo " python    : $PYTHON"
echo " seeds/cell: $SEED_END   positions: $POS_START..$POS_END   gens: $GENERATORS"
echo " messages  : ${#MESSAGES[@]}    cribs:"
printf '   %s\n' $CRIBS

# Confirm we are actually on the GPU before spending hours.
if "$PYTHON" globality_gpu.py 2>/dev/null | grep -q "CuPy (GPU)"; then
    echo " backend   : CuPy (GPU) — confirmed"
else
    echo " backend   : NumPy (CPU) — WARNING: not on GPU."
    echo "             Run with PYTHON=~/.venvs/eyestat/bin/python3, or Ctrl-C."
    sleep 5
fi

SUMMARY="$OUTDIR/summary.txt"; : > "$SUMMARY"
n_cribs="$(printf '%s\n' $CRIBS | grep -c .)"
total=$(( n_cribs * ${#MESSAGES[@]} ))
i=0
start=$(date +%s)

while IFS= read -r crib; do
    [ -n "$crib" ] || continue
    for msg in "${MESSAGES[@]}"; do
        i=$((i+1))
        safe_msg="${msg// /_}"
        tag="${crib:0:24}_${safe_msg}"
        log="$OUTDIR/$tag.log"
        html="$OUTDIR/$tag.html"
        echo
        echo "[$i/$total] crib='$crib'  msg='$msg'  pos=$POS_START..$POS_END"
        "$PYTHON" globality_gpu.py \
            --crib-word "$crib" --crib-msg "$msg" \
            --crib-pos "$POS_START" --crib-pos-end "$POS_END" \
            --generators "$GENERATORS" --seed-end "$SEED_END" \
            --require-gpu --html "$html" 2>&1 | tee "$log"
        if grep -q "GLOBAL keystream candidate" "$log"; then
            echo "*** GLOBAL HIT  crib='$crib'  msg='$msg'  ($log)" | tee -a "$SUMMARY"
        fi
    done
done <<< "$CRIBS"

dt=$(( $(date +%s) - start ))
echo
echo "=================================================================="
echo " sweep complete in ${dt}s — $total cells, results in $OUTDIR/"
if [ -s "$SUMMARY" ]; then
    echo " GLOBAL HIT(S) FOUND:"
    cat "$SUMMARY"
else
    echo " No global hit across the sweep. If every crib/message/generator is"
    echo " null over this seed range, the eye keystream is very likely NOT a"
    echo " small-seed PRNG from this set — pointing at the salakieli/in-game key"
    echo " derivation as the next thing to pin down."
fi
echo "=================================================================="
