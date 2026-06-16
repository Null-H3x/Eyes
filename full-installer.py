#!/usr/bin/env python3
"""full-installer.py — one-shot setup + smoke test for the Noita eye toolkit.

Creates an isolated virtualenv, installs the dependencies, and runs a short
functional smoke test across every tool in the repository:

    noita_eye_core   the math gate (104 checks)         [required]
    classify         cipher-type discriminator           [required]
    EyeWitness       fingerprint + independent verifier + triplet key-test [required]
    EyeCrack         depth/crib-drag + seed-scan demo     [required]
    EyeStat          GPU seed-scan (CPU self-test)         [best-effort]
    EyeSieve         structural hypothesis sweep           [best-effort]
    EyeStat GPU      CuPy device probe                     [only with --gpu]

Usage
-----
    python3 full-installer.py                 # venv + install + smoke test
    python3 full-installer.py --gpu           # also install CuPy + probe the GPU
    python3 full-installer.py --quick         # core tools only (skip EyeStat/EyeSieve)
    python3 full-installer.py --no-venv       # install into the current interpreter
    python3 full-installer.py --skip-install  # just run the smoke test
    python3 full-installer.py --venv .venv    # choose the venv location

Designed to be dependency-free itself (stdlib only) and safe to re-run.  On
Ubuntu 24.04/26.04 the default venv path sidesteps the PEP 668
"externally-managed-environment" pip error.
"""
from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Tuple

ROOT = Path(__file__).resolve().parent

# Core dependency baseline (numpy for everything; scipy speeds EyeStat scoring
# but it has a pure-Python fallback, so it is not strictly required).
BASE_DEPS = ["numpy>=1.24", "scipy>=1.11"]
GPU_DEPS = ["cupy-cuda12x>=13.4"]

C_GREEN = "\033[32m"
C_RED = "\033[31m"
C_YEL = "\033[33m"
C_DIM = "\033[2m"
C_OFF = "\033[0m"


def _c(s: str, color: str) -> str:
    return f"{color}{s}{C_OFF}" if sys.stdout.isatty() else s


def banner(msg: str) -> None:
    print("\n" + "=" * 72)
    print(msg)
    print("=" * 72)


# ---------------------------------------------------------------------------
# venv + dependency install
# ---------------------------------------------------------------------------

def venv_python(venv_dir: Path) -> Path:
    if platform.system() == "Windows":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def ensure_venv(venv_dir: Path) -> Path:
    py = venv_python(venv_dir)
    if py.exists():
        print(_c(f"  venv already present: {venv_dir}", C_DIM))
        return py
    print(f"  creating venv at {venv_dir} ...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    if not py.exists():
        raise RuntimeError(f"venv creation did not produce {py}")
    return py


def pip_install(py: Path, packages: List[str]) -> None:
    print(f"  upgrading pip ...")
    subprocess.run([str(py), "-m", "pip", "install", "--upgrade", "pip"],
                   check=False)
    print(f"  installing: {', '.join(packages)}")
    subprocess.run([str(py), "-m", "pip", "install", *packages], check=True)


# ---------------------------------------------------------------------------
# Smoke tests
# ---------------------------------------------------------------------------

class Test:
    def __init__(self, name: str, cwd: str, argv: List[str], timeout: int,
                 required: bool):
        self.name = name
        self.cwd = cwd
        self.argv = argv
        self.timeout = timeout
        self.required = required


def build_tests(quick: bool, gpu: bool, tmp_fp: str) -> List[Test]:
    tests = [
        Test("noita_eye_core math gate", "noita_eye_core",
             ["selftest.py"], 240, True),
        Test("classify (cipher-type) selftest", "noita_eye_core",
             ["classify.py", "--selftest"], 180, True),
        Test("EyeWitness fingerprint build", "eyewitness",
             ["eyewitness.py", "--quiet", "--n-null", "200", "--out", tmp_fp],
             180, True),
        Test("EyeWitness independent verifier", "eyewitness",
             ["verify_fingerprint.py"], 120, True),
        Test("EyeWitness triplet key-test", "eyewitness",
             ["triplet_keytest.py"], 180, True),
        Test("EyeCrack end-to-end demo", "eyecrack",
             ["eyecrack.py", "demo"], 180, True),
    ]
    if not quick:
        tests += [
            Test("EyeStat self-test (CPU)", "eyestat",
                 ["eyestat_selftest.py"], 900, False),
            Test("EyeSieve self-test", "eyesieve",
                 ["eyesieve_selftest.py"], 900, False),
        ]
    if gpu:
        tests.append(Test("EyeStat GPU probe (CuPy)", "eyestat",
                          ["eyestat_gpu_probe.py"], 300, False))
    return tests


def run_test(py: Path, t: Test) -> Tuple[str, float, str]:
    """Return (status, seconds, tail). status in PASS/FAIL/SKIP."""
    cwd = ROOT / t.cwd
    script = cwd / t.argv[0]
    if not script.exists():
        return "SKIP", 0.0, f"missing {t.argv[0]}"
    start = time.time()
    try:
        proc = subprocess.run([str(py), *t.argv], cwd=str(cwd),
                              capture_output=True, text=True,
                              timeout=t.timeout)
    except subprocess.TimeoutExpired:
        return "FAIL", float(t.timeout), f"timeout after {t.timeout}s"
    dt = time.time() - start
    out = (proc.stdout or "") + (proc.stderr or "")
    tail = "\n".join(line for line in out.strip().splitlines()[-3:])
    if proc.returncode == 0:
        return "PASS", dt, tail
    # Distinguish "missing optional dependency" so best-effort tools read SKIP.
    if not t.required and ("ModuleNotFoundError" in out or "No module named" in out):
        return "SKIP", dt, tail.splitlines()[-1] if tail else "missing dependency"
    return "FAIL", dt, tail


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Install dependencies and smoke-test the Noita eye toolkit.")
    ap.add_argument("--venv", default=str(ROOT / ".venv"),
                    help="virtualenv location (default: ./.venv)")
    ap.add_argument("--no-venv", action="store_true",
                    help="install into the current interpreter instead of a venv")
    ap.add_argument("--gpu", action="store_true",
                    help="also install CuPy and probe the GPU (RTX 50xx: needs "
                         "the open NVIDIA driver + CUDA 12.8+)")
    ap.add_argument("--quick", action="store_true",
                    help="core tools only (skip EyeStat/EyeSieve self-tests)")
    ap.add_argument("--skip-install", action="store_true",
                    help="do not install anything; only run the smoke test")
    args = ap.parse_args()

    banner("Noita eye toolkit — full installer + smoke test")
    print(f"  repo   : {ROOT}")
    print(f"  python : {sys.version.split()[0]}  ({platform.system()} "
          f"{platform.machine()})")

    # 1. Resolve target interpreter.
    if args.no_venv:
        py = Path(sys.executable)
        print(_c("  mode   : --no-venv (current interpreter)", C_DIM))
    else:
        banner("[1/3] Virtual environment")
        try:
            py = ensure_venv(Path(args.venv))
        except Exception as e:
            print(_c(f"  ERROR creating venv: {e}", C_RED))
            print("  Tip: install the venv module (e.g. "
                  "`sudo apt install python3-venv`) or use --no-venv.")
            return 2

    # 2. Install dependencies.
    if args.skip_install:
        print(_c("\n  --skip-install: not installing dependencies", C_DIM))
    else:
        banner("[2/3] Dependencies")
        deps = list(BASE_DEPS) + (GPU_DEPS if args.gpu else [])
        try:
            pip_install(py, deps)
        except subprocess.CalledProcessError as e:
            print(_c(f"  ERROR installing dependencies: {e}", C_RED))
            if args.gpu:
                print("  Tip: CuPy needs the NVIDIA open driver + CUDA 12.8+ "
                      "for Blackwell (RTX 50xx). Verify `nvidia-smi` first.")
            return 2

    # 3. Smoke test.
    banner("[3/3] Smoke test")
    if args.gpu and not shutil.which("nvidia-smi"):
        print(_c("  note: --gpu set but `nvidia-smi` not found; GPU probe will "
                 "likely report no device.", C_YEL))
    elif not args.gpu and shutil.which("nvidia-smi"):
        print(_c("  note: an NVIDIA GPU was detected; re-run with --gpu to "
                 "install CuPy and exercise the GPU path.", C_YEL))

    tmp_fp = str(Path(tempfile.gettempdir()) / "eyewitness_smoke_fingerprint.json")
    tests = build_tests(args.quick, args.gpu, tmp_fp)

    results: List[Tuple[Test, str, float, str]] = []
    for t in tests:
        print(f"\n  -> {t.name} ...", flush=True)
        status, dt, tail = run_test(py, t)
        color = {"PASS": C_GREEN, "FAIL": C_RED, "SKIP": C_YEL}[status]
        print(f"     {_c('[' + status + ']', color)}  ({dt:.1f}s)")
        if tail and status != "PASS":
            for line in tail.splitlines():
                print(_c(f"       {line}", C_DIM))
        elif tail:
            print(_c(f"       {tail.splitlines()[-1]}", C_DIM))
        results.append((t, status, dt, tail))

    # Summary.
    banner("Summary")
    required_fail = 0
    for t, status, dt, _ in results:
        color = {"PASS": C_GREEN, "FAIL": C_RED, "SKIP": C_YEL}[status]
        tag = "" if t.required else _c(" (best-effort)", C_DIM)
        print(f"  {_c(status.ljust(4), color)}  {t.name}{tag}")
        if t.required and status != "PASS":
            required_fail += 1

    print()
    if required_fail == 0:
        print(_c("  ALL REQUIRED TOOLS PASSED.", C_GREEN))
        if not args.no_venv:
            act = (f"{args.venv}\\Scripts\\activate" if platform.system() ==
                   "Windows" else f"source {args.venv}/bin/activate")
            print(f"\n  Activate the environment to use the tools:\n    {act}")
        print("\n  Try:")
        print("    python3 eyewitness/triplet_keytest.py")
        print("    python3 eyecrack/eyecrack.py demo")
        if not args.gpu:
            print("    python3 full-installer.py --gpu   # to set up the GPU path")
        return 0
    print(_c(f"  {required_fail} REQUIRED tool(s) failed — see output above.",
             C_RED))
    return 1


if __name__ == "__main__":
    sys.exit(main())
