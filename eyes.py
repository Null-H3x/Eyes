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
    ("Header test — is (66,5) keystreamed or a literal marker?", "Map the structure",
     "eyewitness", ["header_test.py"]),
    ("Number test — does the header (66,5) encode 34?", "Map the structure",
     "eyewitness", ["number_test.py", "--target", "34"]),
    ("Depth map — how much shared keystream is provable?", "Map the structure",
     "eyewitness", ["depth_map.py"]),
    ("Salakieli AES test — is the eye cipher AES-128-CTR?", "Map the structure",
     "eyewitness", ["salakieli_aes.py"]),
    ("Repeat census — stream vs block/periodic/transposition", "Map the structure",
     "eyewitness", ["repeat_census.py"]),
    ("Isomorph chaining — interrelated alphabets / progressive test", "Map the structure",
     "eyewitness", ["isomorph_chain.py"]),
    ("Maximal-aligned-isomorph extractor (contamination-resistant)", "Map the structure",
     "eyewitness", ["iso_extract.py"]),
    ("Triplet embedded-key test (pair + key)", "Map the structure",
     "eyewitness", ["triplet_keytest.py"]),
    ("Structural fingerprint (EyeWitness)", "Map the structure",
     "eyewitness", ["eyewitness.py"]),
    ("Verify fingerprint — independent re-check", "Map the structure",
     "eyewitness", ["verify_fingerprint.py"]),
    ("Datastream consistency check (integrity + WarFairy cross-check)", "Map the structure",
     "eyewitness", ["datastream_check.py"]),
    ("Header-base deduction + progressive contamination correction", "Map the structure",
     "eyewitness", ["header_base.py"]),
    ("Pure-progressive recovery + decryption attempt (IoC test)", "Map the structure",
     "eyewitness", ["pure_progressive.py"]),
    ("Digit-level / fractionation (Trifid) analysis of eye-marks", "Map the structure",
     "eyewitness", ["trifid_scan.py"]),
    ("Binary provenance (decompiled SpawnSecretEyes -> corpus, 9/9)", "Map the structure",
     "eyewitness", ["binary_provenance.py"]),
    ("Depth / crib-drag analysis", "Map the structure",
     "noita_eye_core", ["analyze.py"]),
    ("Cipher fingerprint — keyless transform-stack test", "Map the structure",
     "eyecrack", ["cipher_fingerprint.py"]),
    ("EyeCrack — crib-drag (Noita wordlist, unknown alphabet)", "Attack",
     "eyecrack", ["cribdrag.py"]),
    ("EyeCrack — crib-placement tester (4x repeated isomorph target)", "Attack",
     "eyecrack", ["crib_fit.py", "--list-targets"]),
    ("EyeCrack — refrain known-position crib attack (pins C, IoC-scored)", "Attack",
     "eyecrack", ["refrain_attack.py", "--constraints"]),
    ("EyeCrack — crib-seeded English n-gram solver", "Attack",
     "eyecrack", ["ngram_solve.py", "trueknowledge"]),
    ("EyeCrack — ordering-search solver (recovers ordering from a crib)", "Attack",
     "eyecrack", ["order_solve.py", "trueknowledgeofthegods"]),
    ("EyeCrack — template-guided refrain sweep (wordlist + enum)", "Attack",
     "eyecrack", ["refrain_sweep.py", "--wordlist", "../eyestat/noita_wordlist.txt",
                  "--top", "20"]),
    ("EyeCrack — refrain template constraints only", "Attack",
     "eyecrack", ["refrain_sweep.py", "--show-template"]),
    ("EyeCrack — anchored refrain composer (double-letter map + wcov)", "Attack",
     "eyecrack", ["refrain_compose.py", "--doubles"]),
    ("EyeCrack — residual ordering exhaust (Phase 2)", "Attack",
     "eyecrack", ["ordering_exhaust.py", "--phrase", "trueknowledgeofthegods"]),
    ("Keyspace ledger (block structure -> key hypotheses)", "Map the structure",
     "eyewitness", ["keyspace_ledger.py"]),
    ("EyeScoreboard — cipher candidate ranking (plant + corpus + premise)", "Map the structure",
     "eyewitness", ["eyescoreboard.py"]),
    ("Refrain repeat-template (forced same/different positions, dof)", "Map the structure",
     "eyewitness", ["refrain_template.py"]),
    ("Model verification (per-msg-progressive vs null; honest verdict)", "Map the structure",
     "eyewitness", ["model_audit.py"]),
    ("Model-independent shared-structure map (triplet openings, repeats)", "Map the structure",
     "eyewitness", ["shared_structure.py"]),
    ("Passage template pipeline (discover · extend · crib validate)", "Map the structure",
     "eyewitness", ["passage_template.py", "--html"]),
    ("Passage template — paranoia audit (real corpus invariants)", "Validate",
     "eyewitness", ["passage_template.py", "--audit"]),
    ("Isomorph Viewer → anchor candidacy (discover + classify)", "Map the structure",
     "eyewitness", ["viewer_anchor.py", "--html"]),
    ("Isomorph Viewer anchor — paranoia audit", "Validate",
     "eyewitness", ["viewer_anchor.py", "--audit"]),
    ("Cipher-construction lattice (what fits; excludes ciphertext-autokey)", "Map the structure",
     "eyewitness", ["cipher_lattice.py"]),
    ("EyeCrack — salakieli crib battery (register + globality commands)", "Attack",
     "eyecrack", ["salakieli_crib.py"]),
    ("EyeCrack — keystream seed-scan (structure, additive, writes HTML)", "Attack",
     "eyecrack", ["keyscan.py", "--count", "1000000",
                  "--html", "../keyscan_report.html"]),
    ("EyeCrack — keystream seed-scan (injective/rotor branch)", "Attack",
     "eyecrack", ["keyscan.py", "--combiner", "subst", "--generators", "nolla",
                  "--count", "200000", "--html", "../keyscan_report.html"]),
    ("EyeCrack — crib->seed bridge (guessed word filters seeds)", "Attack",
     "eyecrack", ["keyscan.py", "--crib-word", "eye", "--crib-pos", "3",
                  "--generators", "nolla", "--count", "1000000",
                  "--html", "../keyscan_cribword_report.html"]),
    ("EyeCrack — crib-globality test (is the keystream global?)", "Attack",
     "eyecrack", ["globality.py", "--crib-word", "messages", "--crib-msg",
                  "East 1", "--crib-pos", "3", "--crib-pos-end", "40",
                  "--generators", "all", "--count", "1000000",
                  "--html", "../globality_report.html"]),
    ("EyeStat — crib-globality on GPU (CuPy; validate then scan)", "Attack",
     "eyestat", ["globality_gpu.py", "--crib-word", "messages", "--crib-msg",
                 "East 1", "--crib-pos", "3", "--crib-pos-end", "40",
                 "--generators", "all", "--seed-end", "100000000",
                 "--html", "../globality_gpu_report.html"]),
    ("EyeCrack — recover a planted seed (demo)", "Attack",
     "eyecrack", ["eyecrack.py", "demo"]),
    ("Calibrate EyeStat results (decoy + char-LM trust gate)", "Attack",
     "eyestat", ["calibrate_report.py",
                 "triplet-results/ctak_right_park_miller_v0_report.html"]),
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


def run(argv, cwd, use_system=False) -> int:
    py = sys.executable if use_system else str(venv_python())
    print(DIM(f"\n$ {Path(py).name} {' '.join(argv)}   (in {cwd})\n"))
    try:
        proc = subprocess.run([py, *argv], cwd=str(ROOT / cwd))
        rc = proc.returncode
    except KeyboardInterrupt:
        print(RED("\n(interrupted)"))
        rc = 130
    except Exception as e:
        print(RED(f"error: {e}"))
        rc = 1
    input(DIM("\n[enter] to return to the menu "))
    return rc


def setup():
    print(GOLD("\nBootstrapping environment (venv + dependencies + smoke test)…"))
    rc = run(["full-installer.py"], ".", use_system=True)
    if rc == 0 and have_venv():
        print(TEAL("\n  environment ready — menu tools will use .venv"))
    elif rc != 0:
        print(RED("\n  Setup did not complete successfully."))
        if not have_venv():
            maj, min = sys.version_info[:2]
            print(DIM(f"  Tip: Ubuntu/Debian minimal images often need:"))
            print(DIM(f"    sudo apt install python{maj}.{min}-venv python3-pip"))
            print(DIM(f"  Then re-run Setup (s), or: python3 full-installer.py"))


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
