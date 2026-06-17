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
classify     cipher-type discriminator (narrow the search before recovery)
grouping     message-grouping model selection (EyeWitness core)
oracle       joint multi-message calibrated verification scorer (EyeCrack core)
embedded_key intra-triplet embedded-key test (pair + key, Model B)
keystream_scope  global vs per-triplet keystream test
header_test  is the (66,5) header keystreamed or a literal/shared marker?
depthmap     keystream-sharing / true-depth map (what is provable vs undetermined)
pairdiff     near-duplicate pair / edit-structure analysis
langdetect   key-free structure / language profiler
cribdrag     two-time-pad crib-drag over an unknown alphabet (constraint solver)
cipher_fingerprint  keyless transform-stack fingerprint (does a stack reveal structure?)
keyscan      keystream seed-scan engine (combiner- + generator-pluggable)
calibrate    calibrated language scoring (decoy/shuffle null + char-LM) — the seed-scan trust gate
analyze      real-corpus analysis entry point
selftest     aggregate math gate

Run ``python3 selftest.py`` (from this directory) to validate everything.
"""

__all__ = [
    "corpus", "cipher_ops", "stats", "lm", "null_model",
    "prng", "trigram", "depth", "classify", "grouping", "oracle",
    "embedded_key", "keystream_scope", "header_test", "depthmap", "pairdiff",
    "langdetect", "cribdrag", "cipher_fingerprint", "keyscan", "calibrate",
]
