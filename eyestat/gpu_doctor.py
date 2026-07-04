#!/usr/bin/env python3
"""gpu_doctor.py — why can't EyeStat "see" the GPU? One command, full answer.

Run this with the SAME python you launch the scan with:

    source ~/.venvs/eyestat/bin/activate
    python3 gpu_doctor.py

It checks the four things that make a present GPU look absent, and for each
failure prints the exact command to fix it — no network, no Claude needed.

THE FOUR TRAPS (all seen in the wild on this project)
=====================================================
  1. GPU invisible to the driver   — nvidia-smi can't talk to the card.
  2. CuPy in a DIFFERENT venv       — cupy is installed, but not in THIS
                                       python. The classic cause: install.sh
                                       run under sudo puts the venv in
                                       /root/.venvs while you activate
                                       ~/.venvs, or a separate ./.venv holds
                                       cupy and this interpreter isn't it.
  3. CuPy present but can't init     — imports, but the CUDA runtime/driver
                                       version doesn't match the wheel.
  4. Root-owned artifacts            — /tmp logs or the output dir created
                                       under sudo, so your user hits Errno 13.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


def _tty() -> bool:
    return sys.stdout.isatty()


def c(txt: str, code: str) -> str:
    return f"\033[{code}m{txt}\033[0m" if _tty() else txt


def hdr(t: str) -> None:
    print(c("\n" + "─" * 68, "36"))
    print(c(t, "1;36"))
    print(c("─" * 68, "36"))


OK = c("[ OK ]", "1;32")
BAD = c("[FAIL]", "1;31")
WARN = c("[WARN]", "1;33")
FIX = c("  ↳ FIX:", "1;35")


def run(cmd: list) -> tuple:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return 127, "", str(e)


def main() -> int:
    problems = []

    # -- context --------------------------------------------------------
    hdr("CONTEXT — which python is asking?")
    py = sys.executable
    venv = os.environ.get("VIRTUAL_ENV", "(none active)")
    user = os.environ.get("USER", "?")
    print(f"  python      : {py}")
    print(f"  version     : {sys.version.split()[0]}")
    print(f"  VIRTUAL_ENV : {venv}")
    print(f"  user        : {user}")
    if os.environ.get("SUDO_USER"):
        print(f"  {WARN} running under sudo (SUDO_USER={os.environ['SUDO_USER']}); "
              "$HOME is /root here — a venv created now lands in /root, not "
              "your home.")
        problems.append("running_under_sudo")

    # -- 1. driver sees the card ---------------------------------------
    hdr("1. GPU visible to the NVIDIA driver (authoritative)")
    rc, out, err = run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                        "--format=csv,noheader"])
    have_driver_gpu = False
    if rc == 0 and out:
        have_driver_gpu = True
        for line in out.splitlines():
            print(f"  {OK} {line.strip()}")
    else:
        print(f"  {BAD} nvidia-smi can't see a GPU  ({err or 'no output'})")
        print(f"{FIX} confirm the card:  lspci | grep -i nvidia")
        print(f"{FIX} if present, (re)install the driver:  "
              "sudo ubuntu-drivers autoinstall && reboot")
        problems.append("no_driver_gpu")

    # -- 2. CuPy in THIS python ----------------------------------------
    hdr("2. CuPy importable in THIS interpreter")
    cupy_here = False
    cupy_ver = None
    try:
        import cupy  # type: ignore
        cupy_here = True
        cupy_ver = cupy.__version__
        print(f"  {OK} import cupy → {cupy_ver}  (at {Path(cupy.__file__).parent})")
    except Exception as e:
        print(f"  {BAD} import cupy failed → {type(e).__name__}: {e}")
        # Hunt for cupy in OTHER pythons so we can point at the mismatch.
        found = _find_cupy_elsewhere(py)
        if found:
            print(f"  {WARN} but CuPy IS installed in other environment(s):")
            for path, ver in found:
                print(f"         {ver:12s} {path}")
            print(f"{FIX} you're running the wrong python. Activate the venv "
                  "that has CuPy, e.g.:")
            # best-guess activate path
            guess = _venv_of(found[0][0])
            if guess:
                print(f"           source {guess}/bin/activate")
            print(f"{FIX} or install CuPy into THIS one:")
            print(f"           {py} -m pip install cupy-cuda12x")
            problems.append("cupy_wrong_venv")
        else:
            print(f"{FIX} install CuPy into THIS python "
                  "(match suffix to your CUDA major):")
            print(f"           {py} -m pip install cupy-cuda12x")
            problems.append("cupy_missing")

    # -- 3. CuPy can actually init the runtime -------------------------
    if cupy_here:
        hdr("3. CuPy can initialize the CUDA runtime")
        try:
            import cupy  # type: ignore
            n = cupy.cuda.runtime.getDeviceCount()
            if n >= 1:
                name = cupy.cuda.runtime.getDeviceProperties(0)["name"]
                name = name.decode() if isinstance(name, bytes) else name
                # a real kernel round-trips
                x = cupy.arange(1000, dtype=cupy.int64)
                s = int((x * 2).sum().get())
                assert s == 999 * 1000
                print(f"  {OK} {n} device(s); device0 = {name}; "
                      "kernel round-trip verified")
                rtv = cupy.cuda.runtime.runtimeGetVersion()
                print(f"  {OK} CUDA runtime {rtv // 1000}.{(rtv % 1000)//10} "
                      f"(CuPy {cupy_ver})")
            else:
                print(f"  {BAD} CuPy sees 0 devices")
                problems.append("cupy_zero_devices")
        except Exception as e:
            print(f"  {BAD} CuPy init/kernel failed → {type(e).__name__}: {e}")
            print(f"{FIX} usually a wheel/driver mismatch. Check driver CUDA "
                  "with nvidia-smi (top-right), then match the wheel:")
            print("           pip uninstall -y cupy-cuda12x && "
                  "pip install cupy-cuda11x   # if driver is CUDA 11.x")
            problems.append("cupy_init_failed")

    # -- 4. writable artifact locations --------------------------------
    hdr("4. Writable output / log locations (Errno 13 guard)")
    checks = [Path.cwd(), Path("/tmp")]
    for d in checks:
        w = os.access(d, os.W_OK)
        owner = _owner(d)
        tag = OK if w else BAD
        print(f"  {tag} {d}  (owner={owner}, writable={w})")
        if not w:
            print(f"{FIX} sudo chown -R {user}:{user} {d}")
            problems.append(f"unwritable:{d}")
    # any root-owned eyestat artifacts in cwd?
    for pat in ("eyestat_results*", "*.log", ".venv", "prng_run*"):
        for hit in Path.cwd().glob(pat):
            if not os.access(hit, os.W_OK):
                print(f"  {WARN} root/other-owned: {hit} (owner={_owner(hit)})")
                print(f"{FIX} sudo chown -R {user}:{user} {hit}")
                problems.append(f"unwritable:{hit}")

    # -- verdict --------------------------------------------------------
    hdr("VERDICT")
    if not problems:
        print(f"  {OK} All clear — this python sees the GPU, CuPy initializes, "
              "and paths are writable. Launch the scan.")
        return 0
    print(f"  {BAD} {len(problems)} issue(s) found:")
    for p in dict.fromkeys(problems):   # dedupe, keep order
        print(f"        • {p}")
    print("\n  Fix the items marked ↳ FIX above (top-down), then re-run "
          "gpu_doctor.py until VERDICT is all-clear.")
    return 1


def _find_cupy_elsewhere(current_py: str) -> list:
    """Look for cupy in sibling venvs and common locations."""
    found = []
    seen = set()
    candidates = []
    home = Path.home()
    real_home = home
    if os.environ.get("SUDO_USER"):
        try:
            import pwd
            real_home = Path(pwd.getpwnam(os.environ["SUDO_USER"]).pw_dir)
        except Exception:
            pass
    for base in {home, real_home, Path("/root"), Path.cwd()}:
        if not base.exists():
            continue
        # ~/.venvs/<name>/bin/python3
        candidates += list(base.glob(".venvs/*/bin/python3"))
        # any dir starting with .venv directly under base (.venv, .venv_x, …)
        candidates += list(base.glob(".venv*/bin/python3"))
        # a project-local venv one level down: <proj>/.venv*/bin/python3
        candidates += list(base.glob("*/.venv*/bin/python3"))
    for pyexe in candidates:
        pyexe = str(pyexe)
        if pyexe == current_py or pyexe in seen or not Path(pyexe).exists():
            continue
        seen.add(pyexe)
        rc, out, _ = run([pyexe, "-c",
                          "import cupy,sys; sys.stdout.write(cupy.__version__)"])
        if rc == 0 and out:
            found.append((pyexe, out.strip()))
    return found


def _venv_of(python_path: str):
    p = Path(python_path)
    # .../venv/bin/python3 → .../venv
    if p.parent.name == "bin":
        return p.parent.parent
    return None


def _owner(path: Path) -> str:
    try:
        import pwd
        return pwd.getpwuid(path.stat().st_uid).pw_name
    except Exception:
        return "?"


if __name__ == "__main__":
    raise SystemExit(main())
