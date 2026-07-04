#!/usr/bin/env python3
"""run.py — one-command launcher for the EyeStat progressive PRNG scan.

Wraps eyestat_gpu_runner.py with the guards a multi-day run needs, so you
don't retype flags or re-trip the resume/short-run traps. Commit this,
pull it onto the Ubuntu box, and run it.

WHAT IT DOES, IN ORDER
======================
  1. PRE-FLIGHT   — confirms the venv python sees CuPy + a GPU, the corpus
                    file exists, and the selftest passes (skippable).
  2. DIR GUARD    — refuses to launch into an output dir that already holds
                    shards unless you pass --resume or --fresh, because a
                    silent resume is exactly what makes a full-range launch
                    "only run a short selection."
  3. LAUNCH       — calls the GPU runner with sane defaults for the
                    progressive scan: seeds start at 1 (Park-Miller seed 0
                    is a fixed point → all-zero stream), end at 2^31-1
                    (the generator's real ceiling), merge + summary on.

USAGE
=====
    python3 run.py                         # progressive_pmp, full PM range
    python3 run.py --mode progressive_beaufort
    python3 run.py --seed-end 5_000_000    # a shorter first slice
    python3 run.py --fresh                 # wipe the output dir first
    python3 run.py --resume                # continue a partial run
    python3 run.py --dry-run               # print the command, run nothing
    python3 run.py --skip-preflight        # jump straight to the dir guard

Everything after a literal `--` is passed through untouched to the GPU
runner, e.g.:  python3 run.py -- --threshold 11 --workers 12
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GPU_RUNNER = HERE / "eyestat_gpu_runner.py"
SELFTEST = HERE / "eyestat_selftest.py"

# Park-Miller state space is 1 .. 2^31-2; M = 2^31-1 is the runner's ceiling.
# Seed 0 is a fixed point (x -> a*x mod M keeps 0 at 0), so START AT 1.
PM_SEED_START = 1
PM_SEED_END = 2_147_483_647          # 2^31 - 1, the runner's hard ceiling

VALID_MODES = ("progressive_pmp", "progressive_beaufort")


def _c(txt: str, code: str) -> str:
    return f"\033[{code}m{txt}\033[0m" if sys.stdout.isatty() else txt


def preflight(data_path: Path, run_selftest: bool) -> bool:
    """Confirm the stack is sane on THIS machine before a long run."""
    ok = True

    print(_c("[preflight] python  :", "1;36"), sys.executable)
    print(_c("[preflight] cwd     :", "1;36"), Path.cwd())

    # CuPy + GPU visibility — the fresh-boot failure mode.
    try:
        import cupy  # type: ignore
        n = cupy.cuda.runtime.getDeviceCount()
        name = cupy.cuda.runtime.getDeviceProperties(0)["name"].decode() \
            if n else "none"
        print(_c("[preflight] cupy    :", "1;36"),
              f"{cupy.__version__}, {n} GPU(s), device0={name}")
        if n < 1:
            print(_c("  ✗ no CUDA device visible — a driver/boot issue.",
                     "1;31"))
            ok = False
    except Exception as e:
        print(_c("[preflight] cupy    :", "1;31"),
              f"IMPORT FAILED — {type(e).__name__}: {e}")
        print("    The GPU runner can't scan without CuPy. Fix the venv/"
              "driver, or test-drive the CPU runner instead.")
        ok = False

    # Corpus present and non-empty.
    if data_path.is_file() and data_path.stat().st_size > 0:
        print(_c("[preflight] corpus  :", "1;36"),
              f"{data_path} ({data_path.stat().st_size:,} bytes)")
    else:
        print(_c("[preflight] corpus  :", "1;31"),
              f"MISSING or empty: {data_path}")
        ok = False

    # Selftest — the 9/9 gate.
    if run_selftest:
        print(_c("[preflight] selftest: running…", "1;36"))
        r = subprocess.run([sys.executable, str(SELFTEST)],
                           capture_output=True, text=True)
        tail = r.stdout.strip().splitlines()[-1:] if r.stdout else [""]
        print("    " + (tail[0] if tail else "(no output)"))
        if r.returncode != 0:
            print(_c("  ✗ selftest FAILED — do not launch.", "1;31"))
            ok = False
    else:
        print(_c("[preflight] selftest: skipped (--skip-preflight-selftest)",
                 "1;33"))

    print(_c("[preflight] result  :", "1;36"),
          _c("PASS", "1;32") if ok else _c("FAIL", "1;31"))
    return ok


def dir_state(output_dir: Path) -> str:
    """'empty' | 'has_shards' — how the resume guard decides."""
    if not output_dir.exists():
        return "empty"
    shard_dirs = [output_dir, output_dir / "temp"]
    for d in shard_dirs:
        if d.exists() and any(d.glob("results_*.txt")):
            return "has_shards"
    return "empty"


def build_cmd(args, passthrough) -> list:
    cmd = [
        sys.executable, str(GPU_RUNNER),
        "--data", str(args.data),
        "--mode", args.mode,
        "--prng", args.prng,
        "--seed-start", str(args.seed_start),
        "--seed-end", str(args.seed_end),
        "--output-dir", str(args.output_dir),
        "--merge",
    ]
    if args.skip_validate:
        cmd.append("--skip-validate")
    return cmd + list(passthrough)


def doctor(output_dir: Path, log_path: Path | None) -> int:
    """Diagnose a stuck / short / finished run from on-disk artifacts alone.

    Written for the offline case: when you're on the Ubuntu box with no
    Claude to paste output to, `python3 run.py --doctor` reconstructs what
    the run actually did from shard filenames (which encode each shard's
    seed range) and points you at the next command to run yourself."""
    print(_c("=" * 66, "1;36"))
    print(_c("run.py --doctor : reconstructing the run from disk", "1;36"))
    print(_c("=" * 66, "1;36"))

    if not output_dir.exists():
        print(f"output dir does not exist: {output_dir}")
        print("→ nothing has run here. Launch with:  python3 run.py")
        return 0

    # Shards can be in temp/ (new layout) or flat (legacy).
    search = [output_dir / "temp", output_dir]
    shards = []
    for d in search:
        if d.exists():
            shards += sorted(d.glob("results_*.txt"))
    shards = sorted(set(shards))

    print(f"output dir            : {output_dir}")
    print(f"completed shards      : {len(shards)}")

    if not shards:
        print("\nNo completed shards on disk. Either the run never reached "
              "its\nfirst shard boundary, or it died in preflight/validate.")
        if log_path and log_path.is_file():
            _tail_diagnostics(log_path)
        else:
            print("→ check the run log:  grep -iE "
                  "'error|abort|validate|fail|Traceback' <your.log>")
        return 0

    # Parse seed ranges out of the filenames: results_<mode>_<prng>_<s>_<e>.txt
    covered = []
    for s in shards:
        parts = s.stem.split("_")
        try:
            lo, hi = int(parts[-2]), int(parts[-1])
            covered.append((lo, hi))
        except (ValueError, IndexError):
            continue
    covered.sort()
    if covered:
        lo_min = min(c[0] for c in covered)
        hi_max = max(c[1] for c in covered)
        span = sum(hi - lo for lo, hi in covered)
        print(f"seed range on disk    : [{lo_min:,} … {hi_max:,})")
        print(f"seeds actually covered: {span:,}")
        full = PM_SEED_END - PM_SEED_START
        print(f"fraction of PM space  : {span / full * 100:.4f}%  "
              f"(of {full:,})")
        # Detect gaps — a non-contiguous cover is the resume/short signature.
        gaps = []
        cur = covered[0][1]
        for lo, hi in covered[1:]:
            if lo > cur:
                gaps.append((cur, lo))
            cur = max(cur, hi)
        if gaps:
            print(_c(f"\n⚠ {len(gaps)} GAP(S) in coverage — the run did NOT "
                     "scan contiguously:", "1;33"))
            for g0, g1 in gaps[:5]:
                print(f"    missing [{g0:,} … {g1:,})")
            print("  This is the 'short selection' signature: shards were "
                  "skipped\n  (resume into a used dir) or the run stopped "
                  "early.")

    # run_summary.txt is the richer artifact if it exists.
    summ = output_dir / "results" / "run_summary.txt"
    if summ.is_file():
        print(_c(f"\nrun_summary.txt present → read it:", "1;32"))
        print(f"    cat {summ}")
    else:
        print("\nno run_summary.txt yet (written at end-of-run / merge).")

    if log_path and log_path.is_file():
        _tail_diagnostics(log_path)
    print(_c("\nnext:", "1;36"),
          "resume with  python3 run.py --resume  |  restart clean with "
          "--fresh")
    return 0


def _tail_diagnostics(log_path: Path) -> None:
    """Surface the tell-tale lines from a run log without needing Claude."""
    print(_c(f"\nlog tell-tales ({log_path}):", "1;36"))
    keys = ("error", "abort", "validate", "fail", "traceback", "exceeds",
            "cupy", "memory", "skip", "done")
    try:
        hits = []
        with open(log_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                low = line.lower()
                if any(k in low for k in keys):
                    hits.append(line.rstrip())
        if hits:
            for h in hits[-15:]:
                print("    " + h)
        else:
            print("    (no error/skip/done markers found)")
    except OSError as e:
        print(f"    could not read log: {e}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Anything after `--` is passed straight to the GPU runner.")
    ap.add_argument("--data", type=Path,
                    default=HERE / "noita_eye_data.json")
    ap.add_argument("--mode", default="progressive_pmp", choices=VALID_MODES)
    ap.add_argument("--prng", default="park_miller_v0")
    ap.add_argument("--seed-start", type=int, default=PM_SEED_START)
    ap.add_argument("--seed-end", type=int, default=PM_SEED_END)
    ap.add_argument("--output-dir", type=Path,
                    default=HERE / "prng_run_progressive")
    ap.add_argument("--fresh", action="store_true",
                    help="delete the output dir before launching")
    ap.add_argument("--resume", action="store_true",
                    help="allow continuing a run with existing shards")
    ap.add_argument("--skip-validate", action="store_true",
                    help="skip the 50-seed GPU-vs-CPU check (NOT advised)")
    ap.add_argument("--skip-preflight", action="store_true",
                    help="skip all preflight checks")
    ap.add_argument("--skip-preflight-selftest", action="store_true",
                    help="preflight, but don't run the full selftest")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the command and exit without running")
    ap.add_argument("--doctor", action="store_true",
                    help="diagnose a stuck/short/finished run from disk and "
                         "exit (offline-friendly: needs no network)")
    ap.add_argument("--log", type=Path, default=None,
                    help="path to the run log for --doctor to scan")
    args, passthrough = ap.parse_known_args()
    # argparse leaves a leading '--' in passthrough; drop it.
    if passthrough and passthrough[0] == "--":
        passthrough = passthrough[1:]

    if args.doctor:
        return doctor(args.output_dir, args.log)

    if args.seed_start < 1:
        print(_c("[warn] seed-start < 1: Park-Miller seed 0 is a fixed "
                 "point (all-zero stream). Bumping to 1.", "1;33"))
        args.seed_start = 1
    if args.seed_end > PM_SEED_END:
        print(_c(f"[warn] seed-end > {PM_SEED_END:,} exceeds the Park-Miller "
                 "ceiling; the runner would reject it. Clamping.", "1;33"))
        args.seed_end = PM_SEED_END

    # --- preflight ---
    if not args.skip_preflight:
        if not preflight(args.data, run_selftest=not
                         args.skip_preflight_selftest):
            print(_c("Aborting: preflight failed. Nothing launched.", "1;31"))
            return 1
    print()

    # --- dir guard ---
    state = dir_state(args.output_dir)
    if args.fresh and args.output_dir.exists():
        print(_c(f"[dir] --fresh: removing {args.output_dir}", "1;33"))
        if not args.dry_run:
            shutil.rmtree(args.output_dir)
        state = "empty"
    if state == "has_shards" and not args.resume:
        print(_c(f"[dir] REFUSING TO LAUNCH: {args.output_dir} already holds "
                 "shard files.", "1;31"))
        print("    A silent resume is what makes a full-range launch 'only "
              "run a short selection' —")
        print("    the runner skips every shard already on disk. Choose:")
        print(f"      • continue that run   : add {_c('--resume', '1;32')}")
        print(f"      • start over clean    : add {_c('--fresh', '1;32')} "
              "(deletes the dir)")
        print(f"      • keep it, run elsewhere: {_c('--output-dir <new>', '1;32')}")
        return 2
    if state == "has_shards" and args.resume:
        print(_c(f"[dir] --resume: continuing run in {args.output_dir} "
                 "(completed shards will be skipped).", "1;33"))

    # --- launch ---
    cmd = build_cmd(args, passthrough)
    span = args.seed_end - args.seed_start
    print(_c("[launch] scan span  :", "1;36"),
          f"{span:,} seeds  [{args.seed_start:,} … {args.seed_end:,})")
    print(_c("[launch] mode/prng  :", "1;36"),
          f"{args.mode} / {args.prng}")
    print(_c("[launch] output     :", "1;36"), args.output_dir)
    print(_c("[launch] command    :", "1;36"), " ".join(cmd))
    if args.dry_run:
        print(_c("[dry-run] nothing executed.", "1;33"))
        return 0
    print(_c("[launch] starting — Ctrl-C to stop; run_summary.txt updates "
             "per shard.", "1;32"))
    print("=" * 70)
    try:
        return subprocess.call(cmd)
    except KeyboardInterrupt:
        print(_c("\n[launch] interrupted. Shards on disk are preserved; "
                 "re-run with --resume to continue.", "1;33"))
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
