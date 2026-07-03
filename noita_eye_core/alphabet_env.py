"""Resolve plaintext alphabet from environment (workbench cut-recipe runs)."""
from __future__ import annotations

import os

import refrain as rf


def resolve_alphabet(default: str | None = None) -> str:
    """Return ``EYES_ALPHABET`` when set and non-empty, else ``default`` or ``DEFAULT_ALPHABET``."""
    env = os.environ.get("EYES_ALPHABET", "").strip()
    if env:
        return env
    if default is not None:
        return default
    return rf.DEFAULT_ALPHABET


def inject_alphabet_argv(argv: list[str], alphabet: str) -> list[str]:
    """Insert or replace ``--alphabet`` in a tool argv list."""
    if "--alphabet" in argv:
        out = list(argv)
        out[argv.index("--alphabet") + 1] = alphabet
        return out
    return ["--alphabet", alphabet, *argv]
