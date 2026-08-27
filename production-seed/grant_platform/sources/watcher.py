"""G1 Wave 2 — revision watcher + document parser lane.

Revision watcher: compares a freshly fetched normalized payload against the
latest snapshot; on material term change it creates a NEW OpportunityRevision
(append-only, never mutating the old) and triggers selective downstream
invalidation (Book 8 C29 semantics).

Parser lane: productionizes document extraction with page/section/locator
lineage. PDF/DOCX parsing is adapter-bound; the contract keeps extraction
lineage without assuming OCR perfection.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from grant_platform.sources.adapters import Snapshot

# terms whose change is MATERIAL (invalidates downstream decisions)
MATERIAL_TERMS = ("deadline", "funding_ceiling", "eligibility", "required",
                  "attachment")
# terms whose change is NOT material (no downstream invalidation)
NON_MATERIAL_TERMS = ("formatting", "cover_sheet_style")


@dataclass
class RevisionChange:
    changed_terms: list[str]
    material: bool
    new_revision_id: str | None
    invalidated_stages: list[str] = field(default_factory=list)


@dataclass
class ExtractedDocument:
    doc_id: str
    source_snapshot_id: str
    sections: list[dict] = field(default_factory=list)  # {page, section, locator, text}
    extraction_lineage: str = ""


def classify_change(previous_normalized: dict, new_normalized: dict) -> RevisionChange:
    """Diff two normalized payloads; classify materiality from the term
    catalog. Non-material change -> no new revision, no invalidation."""
    changed: set[str] = set()
    keys = set(previous_normalized) | set(new_normalized)
    for k in keys:
        if previous_normalized.get(k) != new_normalized.get(k):
            changed.add(k)
    material = bool(changed & set(MATERIAL_TERMS))
    return RevisionChange(changed_terms=sorted(changed), material=material,
                          new_revision_id=None)


def build_revision_change(previous: Snapshot, new: Snapshot) -> RevisionChange:
    """Snapshot-level wrapper: diffs normalized payloads, assigns a new
    revision id for material changes."""
    prev = previous.normalized or {}
    new_n = new.normalized or {}
    change = classify_change(prev, new_n)
    if change.material:
        change.new_revision_id = f"rev-{new.snapshot_id}"
        # selective downstream invalidation (Book 8 C29)
        change.invalidated_stages = ["eligibility", "match", "project",
                                     "drafting", "assurance", "package"]
    return change


def parse_document(raw: bytes, doc_id: str, snapshot_id: str,
                   split_sections: callable | None = None) -> ExtractedDocument:
    """Parser lane contract: split raw bytes into sections with locators.

    split_sections(raw) -> list of {page, section, locator, text}. A
    default splitter handles simple markdown/text documents; PDF/DOCX
    splitters are adapter-bound (G1.3) and must return the same shape.
    """
    if split_sections is None:
        text = raw.decode("utf-8", errors="replace")
        lines = [l for l in text.splitlines() if l.strip()]
        parts: list[dict] = []
        current: dict | None = None
        page = 1
        for line in lines:
            if line.startswith("## "):
                current = {"page": page, "section": line[3:].strip(),
                           "locator": line[3:].strip(), "text": ""}
                parts.append(current)
            elif current is not None:
                current["text"] = (current["text"] + " " + line).strip()
        if not parts:
            parts = [{"page": 1, "section": "body", "locator": "body",
                      "text": text[:500]}]
        return ExtractedDocument(doc_id=doc_id,
                                 source_snapshot_id=snapshot_id,
                                 sections=parts,
                                 extraction_lineage=f"parser:default:{doc_id}")
    sections = split_sections(raw)
    return ExtractedDocument(doc_id=doc_id, source_snapshot_id=snapshot_id,
                             sections=sections,
                             extraction_lineage=f"parser:adapter:{doc_id}")
