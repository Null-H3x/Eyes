#!/usr/bin/env bash
#
# run.sh — Convenience launcher.
#
# Activates a Python environment that has numpy, then invokes eyestat_runner.py
# with any arguments you pass. Falls back to a small smoke-test run if no
# arguments are given.
#
# Environment resolution order (first that works wins):
#   1. $EYESTAT_VENV / $BF_VENV          (explicit override)
#   2. ~/.venvs/eyestat                  (the venv install.sh creates)
#   3. <repo-root>/.venv                 (the shared eye-tools venv, if present)
#   4. an already-activated venv         ($VIRTUAL_ENV)
#   5. system python3                    (if it has numpy)
#
# USAGE
#   ./run.sh                       # small smoke-test (1000 seeds)
#   ./run.sh --modes all --seed-end 1000000 --workers 32 --languages fi
#   EYESTAT_VENV=/path/to/.venv ./run.sh    # force a specific environment
#

# Re-exec under bash if started via `sh run.sh` / dash — otherwise the next line
# (`set -o pipefail`) aborts with "set: Illegal option -o pipefail".
if [ -z "${BASH_VERSION:-}" ]; then exec bash "$0" "$@"; fi
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

_try_activate() {  # $1 = candidate venv dir
    [ -n "${1:-}" ] || return 1
    if [ -f "$1/bin/activate" ]; then
        # shellcheck disable=SC1090
        source "$1/bin/activate"
        return 0
    fi
    return 1
}

PY=""
for cand in "${EYESTAT_VENV:-}" "${BF_VENV:-}" "$HOME/.venvs/eyestat" \
            "$PROJECT_DIR/../.venv" "$PROJECT_DIR/.venv"; do
    if _try_activate "$cand"; then PY="$(command -v python3)"; break; fi
done
# Already inside an activated venv?
if [ -z "$PY" ] && [ -n "${VIRTUAL_ENV:-}" ]; then PY="$(command -v python3 || true)"; fi
# Last resort: system python3.
if [ -z "$PY" ]; then PY="$(command -v python3 || true)"; fi

if [ -z "$PY" ]; then
    echo "ERROR: no python3 interpreter found." >&2
    exit 1
fi

if ! "$PY" -c 'import numpy' >/dev/null 2>&1; then
    echo "ERROR: numpy is not available in the selected environment:" >&2
    echo "         $PY" >&2
    echo "  Fix any one of:" >&2
    echo "    - run ./install.sh   (sets up ~/.venvs/eyestat with numpy+scipy)" >&2
    echo "    - activate a venv that has numpy, then re-run" >&2
    echo "    - point EYESTAT_VENV at one, e.g. the shared eye-tools venv:" >&2
    echo "        EYESTAT_VENV=\"$PROJECT_DIR/../.venv\" ./run.sh" >&2
    exit 1
fi

cd "$PROJECT_DIR"

if [ $# -eq 0 ]; then
    echo "[run.sh] No args given — running a small smoke-test (using $PY)."
    echo "[run.sh] Pass arguments to override (e.g. --modes all --seed-end 1000000)."
    echo
    exec "$PY" eyestat_runner.py \
        --data noita_eye_data.json \
        --modes ctak_right \
        --prngs park_miller \
        --seed-start 0 --seed-end 1000 \
        --workers 4 \
        --threshold 13 \
        --output-dir eyestat_results_smoke
else
    exec "$PY" eyestat_runner.py "$@"
fi
