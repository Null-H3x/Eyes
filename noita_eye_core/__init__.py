"""noita_eye_core — shared core for the Noita eye-message analysis tools.

A single, tested home for the math that EyeStat, EyeSieve and the workbench
otherwise duplicate, plus the new depth/crib-drag keystream-recovery layer that
ties the three lines of effort together.

Modules
-------
corpus       single source of truth for the 9-message corpus
cipher_ops   canonical modular combiners (+/-, Beaufort) with round-trip KATs
stats        IoC (alphabet-aware), chi2, difference IoC
lm           character n-gram language model (scorer + depth emission/transition)
null_model   calibrated null distribution + significance + multiple-testing
prng         faithful Noita NollaPRNG port (MINSTD core, position scrambler)
trigram      base-5 trigram decomposition + per-digit statistics
depth        depth confirmation, crib-drag, and Viterbi keystream recovery
analyze      real-corpus analysis entry point
selftest     aggregate math gate

Run ``python3 selftest.py`` (from this directory) to validate everything.
"""

__all__ = [
    "corpus", "cipher_ops", "stats", "lm", "null_model",
    "prng", "trigram", "depth",
]
