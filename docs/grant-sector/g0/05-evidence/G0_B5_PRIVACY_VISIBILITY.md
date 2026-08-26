# G0-B5-C22 — Privacy, Retention & Evidence Visibility

## Visibility classes

- PUBLIC_SOURCE
- TENANT_PRIVATE
- TENANT_SHARED_APPROVED
- PLATFORM_INTERNAL
- RESTRICTED_SENSITIVE

Default visibility for undecorated evidence is TENANT_PRIVATE.

## Rules (VIS-001..006)

1. Tenant-private evidence is not globally retrievable; out-of-tenant
   queries never see it or its metadata.
2. Graph edges inherit/compute visibility safely and never raise an
   endpoint's visibility.
3. Derived embeddings/vector entries respect source visibility and honor
   deletion.
4. Deletion/retention restricts current access while preserving required
   audit tombstones and content hashes.
5. Explanation packets filter evidence by viewer authority.
6. Tenant exports enumerate only the tenant's own evidence lineage.

## Viewer classes

PUBLIC (public source only), TENANT_VIEWER (own-tenant private),
SHARED_APPROVED_VIEWER, PLATFORM_ADMIN (platform-internal),
RESTRICTED_ADMIN (restricted-sensitive).

## Implementation

- `config/g0/evidence/visibility_policy.yaml`
- `prototype/g0/evidence/visibility.py` (`VisibilityManager`)
- `tools/g0/validate_visibility.py`
- `tests/g0/book5/test_visibility.py`
