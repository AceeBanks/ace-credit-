# G0-B3 — Private/Foundation Sources & Hostile-Source Security (C18-C19)

## Scope

Supports the client's non-government grant categories without a mandatory paid data dependency (B3.C18), and treats **all external source content as untrusted data** (B3.C19).

## C18 — Private/Foundation/Corporate Source Protocol

Config of truth: `config/g0/source/private_source_policy.yaml` · Prototype: `prototype/g0/source/private_sources.py`

Registered funder pages (foundation opportunities, corporate philanthropy programs, community foundations, local grantmakers) are supported through governed crawling. Optional curated providers (Candid or equivalent) may be integrated **later** after measuring marginal value/cost — never mandatory for MVP.

A private source may only be `ENABLED` after **every** registration requirement is met: issuer ownership verified, relevant pages identified, update frequency estimated, terms/robots reviewed, crawler strategy tested, authority limited to what the issuer controls, and historical winners captured only where the source supports them.

Uncertainty is preserved, never invented away: a private grantmaker without a clean stable external ID still receives governed internal identity (`source_id`), and missing history is represented as unknown rather than structured certainty.

Identity continuity is fail-closed: a webpage redesign with the same canonical URL and the same issuer-visible opportunity key is the SAME opportunity; a changed key on the same URL is `NEEDS_REVIEW` (never a silent duplicate); only a distinct URL **and** distinct key is a NEW opportunity. An old/archived foundation page never outranks the current issuer-controlled page — equal-authority temporal resolution keeps the newest effective date.

## C19 — Source Security & Prompt-Injection Constitution

Config of truth: `config/g0/source/source_security_policy.yaml` · Prototype: `prototype/g0/source/security.py`

Eleven threat classes are governed (prompt injection, malicious links, data exfiltration instructions, embedded scripts, poisoned metadata, malicious documents, decompression bombs, credential phishing, source-domain impersonation, SSRF via crawler URLs, redirect abuse) and ten security rules are enforced, all fail-closed:

1. source content cannot grant capabilities;
2. workers receive source text in an untrusted-data envelope;
3. browser/crawler egress restricted by policy;
4. raw HTML/scripts never execute in a trusted control context;
5. downloads scanned/validated by file type;
6. redirects/domain changes logged;
7. credentials never exposed to source content;
8. extraction prompts distinguish instructions from source data;
9. suspicious source content can be quarantined;
10. model/tool decisions remain policy-gated outside source context.

The **Sanitized SourceEnvelope** separates trusted metadata (snapshot id, content type, security flags, allowed operations) from an untrusted content reference. Content is data: exfiltration instructions are `BLOCK`ed, prompt-injection/embedded-script content is `FLAG`ged or `QUARANTINE`d, tool-like syntax in source text grants nothing (allowed operations stay empty), redirects to ungoverned domains are blocked, and unsupported executable content is quarantined rather than run.

## Tests

- `tests/g0/book3/test_private_sources.py` — registration gating (ENABLED requires all requirements), missing stable ID still yields internal identity, redesign continuity (SAME / NEEDS_REVIEW / NEW), old page cannot outrank current issuer page;
- `tests/g0/book3/test_source_security.py` — exfiltration blocked, prompt injection flagged, embedded script quarantined, tool syntax inert, malicious redirect blocked, executable quarantined, credentials never ride the envelope.

## Validation

- `python tools/g0/validate_private_source_security.py` → **PASS**

## Commits

- `G0-B3-C18-C19` chapter band.

## Status

PASS — private sources are governed and uncertainty-safe; hostile source content is inert, quarantinable, and never authoritative.
