#!/usr/bin/env python3
"""Tool 1 — closure residual + acquisition ranking, on the CLEAN (contamination-filtered)
isomorph set from chain_extract. Adds the two things chain_extract does not: the honest
residual budget and the information-gain ranking of what to acquire next.

RAILS: ordering is per-msg-progressive-CONDITIONAL (a candidate, per EYEWITNESS). Reduces &
ranks; never pins a value or claims a cross-triplet magnitude. Residual is real, not zero.
"""
import sys, json
from collections import defaultdict
sys.path.insert(0, "/home/claude/eyes_repo/Eyes-main/noita_eye_core")
import corpus as corpus_mod, chain_extract as ce, chain_models as cm

N = 83
TRIPLETS = ((0,1,2),(3,4,5),(6,7,8)); tri_of = {m: ti for ti, t in enumerate(TRIPLETS) for m in t}
c = corpus_mod.load(); M = [list(x) for x in c.ciphertexts]
r = ce.extract(M, base_len=13, broad_repeats=3, rows_fn=cm.per_msg_prog_rows, N=N)

# ---- re-derive closure from clean pairs (validates my union-find vs chain_extract) ----
parent, pot = {}, {}
def _mk(g):
    if g not in parent: parent[g]=g; pot[g]=0
def find(g):
    if parent[g]==g: return g
    root=find(parent[g]); pot[g]=(pot[g]+pot[parent[g]])%N; parent[g]=root; return root
def union(a,b,d):
    _mk(a);_mk(b); ra,rb=find(a),find(b); pa,pb=pot[a],pot[b]
    if ra==rb: return (pa-pb)%N==d%N
    parent[rb]=ra; pot[rb]=(pa-pb-d)%N; return True

contradictions=0; triplets_touched=set()
for pr in r.clean_pairs:
    d=(pr.p1-pr.p2)%N     # Delta_base=0 within triplet (all clean pairs are T1)
    triplets_touched.add(tri_of[pr.m1]); triplets_touched.add(tri_of[pr.m2])
    for k in range(pr.length):
        ga, gb = M[pr.m1][pr.p1+k], M[pr.m2][pr.p2+k]
        if not union(ga, gb, d): contradictions += 1

linked=set(parent); comps=defaultdict(list)
for g in linked: comps[find(g)].append(g)
big=max(comps.values(), key=len)
pots_big={pot[g]%N for g in big}
collapses={p:[g for g in big if pot[g]%N==p] for p in pots_big}
collapse_pairs={p:v for p,v in collapses.items() if len(v)>1}

print("="*68)
print("TOOL 1 — closure residual + acquisition ranking (clean set)")
print("="*68)
print(f"clean isomorph pairs: {len(r.clean_pairs)}  | contradictions: {contradictions}")
print(f"glyphs linked: {len(linked)}   components: {len(comps)}  (sizes {sorted((len(v) for v in comps.values()),reverse=True)})")
print(f"biggest comp: {len(big)} glyphs on {len(pots_big)} distinct positions")
print(f"CROSS-CHECK vs chain_extract: linked {len(linked)} (theirs {r.symbols_recovered}),"
      f" distinct {len(pots_big)} (theirs {r.positions_distinct}) -> {'MATCH' if len(linked)==r.symbols_recovered and len(pots_big)==r.positions_distinct else 'DIFFER'}")
print(f"triplets contributing clean isomorphs: {sorted(triplets_touched)}  (0=T1,1=T2,2=T3)")

unlinked = N - len(linked)
print(f"\nRESIDUAL BUDGET (reported in native units, not summed):")
print(f"  (1) UNLINKED glyphs, no constraint at all : {unlinked}/{N}   <-- dominant residual")
print(f"  (2) collapse ambiguities within linked set: {len(collapse_pairs)} unresolved pairs  {collapse_pairs}")
print(f"  (3) global gauge (rotation)               : 1")
print(f"  (4) cross-triplet base deltas (field map) : 2  [T1-T2, T2-T3]")
print(f"  => the closure pins {len(linked)}/{N} glyphs' RELATIVE positions; everything else is open.")

print(f"\nACQUISITION RANKING (what each fact buys, honestly):")
print(f"  +{len(big):2d} abs  : pin ANY 1 of the {len(big)} linked glyphs -> fixes the gauge, locking the")
print(f"            ABSOLUTE value of all {len(big)} linked glyphs at once. The single best pin.")
print(f"  + var   : acquire clean isomorphs in T2/T3 -> the clean set is ALL T1, so T2/T3")
print(f"            currently contribute 0 linked glyphs. Their internal isomorphs would add")
print(f"            new glyphs directly (biggest lever on the unlinked+island glyphs).")
print(f"  + var   : measure a cross-triplet bridge shift -> only helps once T2/T3 isomorphs")
print(f"            exist to align; then it merges their glyphs into this component.")
print(f"  + 2     : a distinguishing isomorph separating a collapse pair {list(collapse_pairs.values())}")
print(f"  + 1 ea  : a crib/anchor on any UNLINKED glyph -> +1 glyph (low leverage, but the only")
print(f"            direct way to touch the {unlinked} unlinked ones without new structure).")

print(f"\nHONEST HEADLINE: the isomorph closure reaches {len(linked)}/{N} glyphs, all from T1.")
print(f"No manipulation of the existing constraints pins the {unlinked} unlinked glyphs — that")
print(f"needs ACQUIRING structure (T2/T3 isomorphs, bridges) or {unlinked} individual anchors.")
print(f"Tool 1 quantifies the gap; it cannot close it. Ordering shown is model-CONDITIONAL.")

json.dump({
  "clean_pairs": len(r.clean_pairs), "contradictions": contradictions,
  "glyphs_linked": len(linked), "linked_glyphs": sorted(int(g) for g in linked),
  "distinct_positions": len(pots_big), "matches_chain_extract": len(linked)==r.symbols_recovered,
  "triplets_contributing": sorted(triplets_touched),
  "residual": {"unlinked_glyphs": unlinked, "collapse_pairs": {str(k):v for k,v in collapse_pairs.items()},
               "global_gauge": 1, "cross_triplet_base_deltas": 2},
  "ranking": [
     {"gain": f"{len(big)} absolute values", "action": "pin any 1 linked glyph (fixes gauge)"},
     {"gain": "variable", "action": "acquire T2/T3 internal isomorphs (adds new glyphs; clean set is all T1)"},
     {"gain": "variable", "action": "measure cross-triplet bridge shift (merges T2/T3 once they have isomorphs)"},
     {"gain": "2", "action": "distinguishing isomorph for a collapse pair"},
     {"gain": "1 each", "action": "crib/anchor on an unlinked glyph"}],
  "model_conditional": True,
}, open("/home/claude/tool1_result.json","w"), indent=1)
print("\nwrote tool1_result.json")
