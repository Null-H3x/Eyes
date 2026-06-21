"""Preset automated workflows with incremental saved progress."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence, Tuple


@dataclass(frozen=True)
class WorkflowPreset:
    id: str
    title: str
    description: str
    steps: Tuple[str, ...]          # tool IDs from registry
    tags: Tuple[str, ...] = field(default_factory=tuple)


PRESETS: Tuple[WorkflowPreset, ...] = (
    WorkflowPreset(
        id="quick-validate",
        title="Quick Validate",
        description="Math gate plus the two paranoia audits (passage template + viewer anchor).",
        steps=(
            "validate-run-the-full-math-gate-validate-everything",
            "validate-passage-template-paranoia-audit-real-corpus-inva",
            "validate-isomorph-viewer-anchor-paranoia-audit",
        ),
        tags=("audit", "fast"),
    ),
    WorkflowPreset(
        id="structure-map",
        title="Structure Map",
        description="Cipher family, isomorphs, shared openings, and passage template discovery.",
        steps=(
            "map-cipher-type-what-family-is-this",
            "map-isomorph-chaining-interrelated-alphabets-progres",
            "map-model-independent-shared-structure-map-triplet-o",
            "map-passage-template-pipeline-discover-extend-crib-v",
        ),
        tags=("structure", "medium"),
    ),
    WorkflowPreset(
        id="refrain-pipeline",
        title="Refrain Attack Pipeline",
        description="Template constraints, crib attack, composer doubles, and ordering solver.",
        steps=(
            "attack-eyecrack-refrain-template-constraints-only",
            "attack-eyecrack-refrain-known-position-crib-attack-pins",
            "attack-eyecrack-anchored-refrain-composer-double-letter",
            "attack-eyecrack-ordering-search-solver-recovers-orderin",
        ),
        tags=("refrain", "attack"),
    ),
    WorkflowPreset(
        id="anchor-discovery",
        title="Anchor Discovery",
        description="Isomorph viewer patterns, passage template report, and refrain template.",
        steps=(
            "map-isomorph-viewer-anchor-candidacy-discover-classi",
            "map-passage-template-pipeline-discover-extend-crib-v",
            "map-refrain-repeat-template-forced-same-different-po",
        ),
        tags=("template", "medium"),
    ),
    WorkflowPreset(
        id="evidence-ledger",
        title="Evidence Ledger Build",
        description="Run math gate modules then rebuild the static evidence dashboard.",
        steps=(
            "validate-run-the-full-math-gate-validate-everything",
        ),
        tags=("report", "fast"),
    ),
)


def preset_by_id() -> dict:
    return {p.id: p for p in PRESETS}


def validate_presets(tool_ids: Sequence[str]) -> List[str]:
    """Return list of missing tool IDs referenced by presets."""
    known = set(tool_ids)
    missing = []
    for p in PRESETS:
        for sid in p.steps:
            if sid not in known:
                missing.append(sid)
    return sorted(set(missing))
