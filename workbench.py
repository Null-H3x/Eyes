#!/usr/bin/env python3
"""workbench.py — bootstrap dependencies and open the EYES workbench.

Run from the repository root::

    python3 workbench.py

On a fresh clone this will:

  1. Create ``.venv`` and install dependencies (via ``full-installer.py``)
  2. Rebuild ``workbench.html`` with the current tool registry snapshot
  3. Start ``dashboard/server.py`` and open the workbench in your browser

The server enables live tool runs, workflow automation, dataset import/plant,
and cipher validation.  Stdlib-only entry point — safe before any venv exists.
"""
from __future__ import annotations

import argparse
import platform
import subprocess
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"


def _venv_python() -> Path:
    if platform.system() == "Windows":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def have_venv() -> bool:
    return _venv_python().is_file()


def _run(cmd: list[str], *, cwd: Path | None = None, check: bool = True) -> int:
    print(f"\n$ {' '.join(cmd)}\n", flush=True)
    try:
        proc = subprocess.run(cmd, cwd=str(cwd or ROOT), check=check)
        return proc.returncode
    except KeyboardInterrupt:
        print("\n(interrupted)")
        return 130


def ensure_dependencies(*, force: bool = False, quick: bool = False) -> int:
    """Create .venv and install packages when missing (or when --setup)."""
    if have_venv() and not force:
        return 0
    argv = [sys.executable, "full-installer.py"]
    if quick:
        argv.append("--quick")
    rc = _run(argv)
    if rc != 0:
        print("Setup failed — fix errors above, then re-run workbench.py")
    return rc


def build_workbench() -> int:
    if not have_venv():
        return 1
    return _run([str(_venv_python()), "build.py"], cwd=ROOT / "dashboard", check=False)


def serve(*, host: str, port: int, open_browser: bool) -> int:
    if not have_venv():
        return 1
    py = str(_venv_python())
    url = f"http://{host}:{port}/workbench.html"
    if open_browser:
        print(f"\nOpening {url}\n", flush=True)
        webbrowser.open(url)
    return _run(
        [py, "server.py", "--host", host, "--port", str(port)],
        cwd=ROOT / "dashboard",
        check=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Bootstrap EYES dependencies and open the workbench")
    ap.add_argument("--setup", action="store_true",
                    help="re-run full-installer before launching")
    ap.add_argument("--quick", action="store_true",
                    help="with --setup: skip EyeStat/EyeSieve smoke tests")
    ap.add_argument("--build-only", action="store_true",
                    help="only rebuild workbench.html, do not start server")
    ap.add_argument("--no-build", action="store_true",
                    help="skip workbench.html rebuild")
    ap.add_argument("--no-open", action="store_true",
                    help="start server without opening a browser tab")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    if not (ROOT / "dashboard" / "server.py").is_file():
        print("error: run workbench.py from the EYES repository root")
        return 1

    rc = ensure_dependencies(force=args.setup, quick=args.quick)
    if rc != 0:
        return rc

    if not args.no_build:
        rc = build_workbench()
        if rc != 0:
            print("warning: workbench build exited with", rc)

    if args.build_only:
        print("Built workbench.html")
        return 0

    print("EYES Workbench — live tool runs require this server to stay running.")
    print("  Ctrl+C stops the server.\n")
    return serve(host=args.host, port=args.port, open_browser=not args.no_open)


if __name__ == "__main__":
    raise SystemExit(main())
