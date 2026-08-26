# G0-B6-C12/C13/C14/C15 — Integration, Egress, Data Classification & PII

## Integration boundary (C12)

Activepieces or equivalent may execute bounded connector actions (calendar,
approved storage writes, approved email, CRM sync, bounded admin
workflows). It never owns canonical project state, agent authority,
eligibility truth, approval truth or permanent source-of-record status
(SEC-LAW-018). Platform outages never erase accepted task state;
connectors cannot mutate unrelated resources; outside automation gains no
authority; connector results are validated before state promotion.

## Egress (C13)

Egress classes: REGISTERED_SOURCE_READ, APPROVED_API, APPROVED_INTEGRATION,
EMAIL_EXTERNAL, SUBMISSION_PORTAL, UNKNOWN_EXTERNAL. Phase 1: source reads
and approved APIs enabled, external sends and submission disabled. SSRF
protections block localhost, cloud metadata (169.254.169.254), private
networks and `file://`; redirects are revalidated; sensitive data cannot
egress to unapproved destinations.

## Data classification (C14)

Eight classes (PUBLIC … RESTRICTED_SYSTEM_SECURITY) with strongest-class
inheritance for derived artifacts; secrets never downgrade by summarization;
public source + private annotations → tenant-private derived object.

## PII (C15)

Field-scoped context bundles (workers receive only task-required fields),
sidechain/log redaction, public explanation packets omit restricted fields,
and tenant-private data is gated from global eval/training without explicit
governance.

## Implementation

- `config/g0/security/integration_egress_policy.yaml`,
  `config/g0/security/data_classification_policy.yaml`
- `prototype/g0/security/boundaries.py` (`IntegrationExecutor`,
  `EgressController`, `ClassificationEngine`, `PIIFilter`)
- `tools/g0/validate_boundaries.py`
- `tests/g0/book6/test_boundaries.py` (16 tests)
