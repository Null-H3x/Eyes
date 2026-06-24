#!/usr/bin/env python3
"""run.py — set up EYES and open the workbench in your browser.

One command for a fresh clone or daily use:

    python3 run.py

On first run this creates ``.venv`` (via ``full-installer.py``), rebuilds
``workbench.html``, starts the local workbench server, and opens the dashboard.

Options::

    python3 run.py --port 9000
    python3 run.py --no-open          # server only, no browser tab
    python3 run.py --setup            # re-run full installer before serving
    python3 run.py --quick-setup      # installer smoke test skips EyeStat/EyeSieve
"""
from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"


def _venv_python() -> Path:
    if platform.system() == "Windows":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def have_venv() -> bool:
    py = _venv_python()
    return py.is_file()


def _run(cmd: list[str], *, label: str) -> int:
    print(f"\n→ {label}")
    print(f"  $ {' '.join(cmd)}\n")
    try:
        return subprocess.call(cmd, cwd=str(ROOT))
    except KeyboardInterrupt:
        return 130


def ensure_setup(*, force: bool, quick: bool) -> int:
    if have_venv() and not force:
        print("Environment ready (.venv)")
        return 0

    if force:
        print("Running full setup (full-installer.py)…")
    else:
        print("No .venv found — running first-time setup…")

    cmd = [sys.executable, str(ROOT / "full-installer.py")]
    if quick:
        cmd.append("--quick")
    rc = _run(cmd, label="Bootstrap environment")
    if rc != 0:
        print("\nSetup failed. On Debian/Ubuntu you may need:")
        maj, min = sys.version_info[:2]
        print(f"  sudo apt install python{maj}.{min}-venv python3-pip")
        print("Then re-run: python3 run.py")
        return rc
    if not have_venv():
        print("\nSetup finished but .venv is still missing.")
        return 1
    print("\nSetup complete.")
    return 0


def build_workbench(py: Path) -> int:
    return _run(
        [str(py), str(ROOT / "dashboard" / "build.py")],
        label="Build workbench.html",
    )


def serve_workbench(
    py: Path,
    *,
    host: str,
    port: int,
    open_browser: bool,
) -> int:
    cmd = [str(py), str(ROOT / "dashboard" / "server.py"),
           "--host", host, "--port", str(port)]
    if open_browser:
        cmd.append("--open")
    return _run(cmd, label=f"Workbench server http://{host}:{port}/workbench.html")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Set up EYES and open the HTML workbench",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Equivalent manual steps:\n"
            "  python3 full-installer.py\n"
            "  .venv/bin/python dashboard/build.py\n"
            "  .venv/bin/python dashboard/server.py --open"
        ),
    )
    ap.add_argument("--host", default="127.0.0.1", help="bind address (default: 127.0.0.1)")
    ap.add_argument("--port", type=int, default=8765, help="HTTP port (default: 8765)")
    ap.add_argument(
        "--no-open",
        action="store_true",
        help="do not open a browser tab (server still starts)",
    )
    ap.add_argument(
        "--setup",
        action="store_true",
        help="run full-installer even if .venv already exists",
    )
    ap.add_argument(
        "--quick-setup",
        action="store_true",
        help="pass --quick to full-installer (skip EyeStat/EyeSieve smoke tests)",
    )
    ap.add_argument(
        "--skip-build",
        action="store_true",
        help="skip rebuilding workbench.html (use existing snapshot)",
    )
    args = ap.parse_args()

    print("EYES — workbench launcher")
    print("=" * 40)

    rc = ensure_setup(force=args.setup, quick=args.quick_setup)
    if rc != 0:
        return rc

    py = _venv_python()
    if not args.skip_build:
        rc = build_workbench(py)
        if rc != 0:
            print("\nWorkbench build failed.")
            return rc

    url = f"http://{args.host}:{args.port}/workbench.html"
    if not args.no_open:
        print(f"\nOpening {url} …")
    else:
        print(f"\nWorkbench: {url}")
        print("Ctrl+C to stop the server.\n")

    return serve_workbench(
        py,
        host=args.host,
        port=args.port,
        open_browser=not args.no_open,
    )


if __name__ == "__main__":
    raise SystemExit(main())
