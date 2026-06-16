#!/usr/bin/env python3
"""eyes.py — the front door to the EYES toolkit.

Download the repo as a .zip, extract anywhere, and run:

    python3 eyes.py

A single menu over every workflow, with one-key access to the HTML dashboard.
Stdlib-only, so it runs on a freshly-unzipped folder with nothing installed: its
first job is to bootstrap the virtualenv (via full-installer.py) if needed, then
run each tool inside that venv.

Add a tool = add one line to WORKFLOWS.
"""
from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"

# ANSI styling (Grimoire palette); disabled when not a TTY.
_TTY = sys.stdout.isatty()
def _c(s, code):  # noqa: E306
    return f"\033[{code}m{s}\033[0m" if _TTY else s
GOLD = lambda s: _c(s, "38;5;178")   # noqa: E731
DIM = lambda s: _c(s, "2")           # noqa: E731
TEAL = lambda s: _c(s, "38;5;79")    # noqa: E731
RED = lambda s: _c(s, "38;5;167")    # noqa: E731
BOLD = lambda s: _c(s, "1")          # noqa: E731


# (key, title, group, cwd, argv)   key None => auto-numbered
WORKFLOWS = [
    ("Cipher type — what family is this?", "Map the structure",
     "noita_eye_core", ["classify.py"]),
    ("Keystream scope — global vs per-triplet", "Map the structure",
     "eyewitness", ["keystream_scope_test.py"]),
    ("Triplet embedded-key test (pair + key)", "Map the structure",
     "eyewitness", ["triplet_keytest.py"]),
    ("Structural fingerprint (EyeWitness)", "Map the structure",
     "eyewitness", ["eyewitness.py"]),
    ("Verify fingerprint — independent re-check", "Map the structure",
     "eyewitness", ["verify_fingerprint.py"]),
    ("Depth / crib-drag analysis", "Map the structure",
     "noita_eye_core", ["analyze.py"]),
    ("EyeCrack — recover a planted seed (demo)", "Attack",
     "eyecrack", ["eyecrack.py", "demo"]),
    ("EyeCrack — per-triplet seed scan (1M, triplet 0)", "Attack",
     "eyecrack", ["eyecrack.py", "structscan", "--count", "1000000",
                  "--triplet", "0"]),
    ("Run the full math gate (validate everything)", "Validate",
     "noita_eye_core", ["selftest.py"]),
]


def venv_python() -> Path:
    if platform.system() == "Windows":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def have_venv() -> bool:
    return venv_python().exists()


def run(argv, cwd, use_system=False):
    py = sys.executable if use_system else str(venv_python())
    print(DIM(f"\n$ {Path(py).name} {' '.join(argv)}   (in {cwd})\n"))
    try:
        subprocess.run([py, *argv], cwd=str(ROOT / cwd))
    except KeyboardInterrupt:
        print(RED("\n(interrupted)"))
    except Exception as e:
        print(RED(f"error: {e}"))
    input(DIM("\n[enter] to return to the menu "))


def setup():
    print(GOLD("\nBootstrapping environment (venv + dependencies + smoke test)…"))
    run(["full-installer.py"], ".", use_system=True)


def open_dashboard():
    if not have_venv():
        print(RED("No environment yet — run Setup (s) first."))
        input(DIM("[enter] "))
        return
    print(GOLD("\nBuilding the evidence-ledger dashboard and opening it…"))
    run(["build.py", "--open"], "report")


def banner():
    if _TTY:
        os.system("clear" if os.name != "nt" else "cls")
    line = GOLD("═" * 58)
    print(f"""
{line}
{GOLD('              E Y E S   ·   the noita eye cipher')}
{DIM('         structure mapping · attacks · evidence ledger')}
{line}""")
    if have_venv():
        print(TEAL("  environment: ready  (.venv)"))
    else:
        print(RED("  environment: NOT set up  — choose (s) Setup first"))


def menu():
    while True:
        banner()
        print(GOLD("\n  0) ") + BOLD("Open the HTML dashboard  ")
              + DIM("(build + launch in browser)"))
        n = 0
        last_group = None
        index = {}
        for title, group, cwd, argv in WORKFLOWS:
            if group != last_group:
                print(TEAL(f"\n  {group}"))
                last_group = group
            n += 1
            index[str(n)] = (argv, cwd)
            print(f"  {GOLD(f'{n})'):>4} {title}")
        print(DIM("\n  s) Setup / reinstall      q) Quit"))
        choice = input(GOLD("\n  select › ")).strip().lower()

        if choice in ("q", "quit", "exit"):
            print(DIM("\nfarewell, seeker.\n"))
            return
        if choice == "s":
            setup()
        elif choice == "0":
            open_dashboard()
        elif choice in index:
            if not have_venv():
                print(RED("\nNo environment yet — run Setup (s) first."))
                input(DIM("[enter] "))
                continue
            argv, cwd = index[choice]
            run(argv, cwd)
        else:
            print(RED("  unknown selection"))
            input(DIM("  [enter] "))


if __name__ == "__main__":
    try:
        menu()
    except (KeyboardInterrupt, EOFError):
        print(DIM("\nfarewell, seeker.\n"))
