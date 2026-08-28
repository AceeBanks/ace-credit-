"""Adversarial audit of QUALITY_CANDIDATE_01 (mission §1, §7).

Proves the committed 4-claim ledger is incomplete by extracting every
material assertion sentence from the actual rendered proposal. This is a
throwaway diagnostic; the production engine lives in
grant_platform/factory/integrity.py.
"""
import re
from pathlib import Path

md = Path(__file__).resolve().parents[2] / (
    "docs/grant-sector/g1/quality-live/G1_QUALITY_LIVE_PROPOSAL.md")
text = md.read_text(encoding="utf-8")

sents = re.split(r"(?<=[.!?])\s+", text)
num = re.compile(
    r"(\$[\d,]+|\b\d+(?:\.\d+)?\s*(?:percent|%)?\s*\b|EIN|founded"
    r"|\bmembers?\b|\byouth\b|volunteers|\bsites\b|sessions|hours|weeks"
    r"|match|audit|resolution|graduation|poverty|board)", re.IGNORECASE)
mat = [s.strip().replace("\n", " ") for s in sents
       if num.search(s) and len(s) > 60]

print(f"TOTAL sentences: {len(sents)}")
print(f"MATERIAL assertion sentences: {len(mat)}")
print("(committed Claim Ledger recorded: 4)")
print()
for s in mat[:15]:
    print("-", s[:160])
