# G0-B6-C8 — Credential Vault Constitution

## Secret classes

API_KEY, OAUTH_ACCESS_TOKEN, OAUTH_REFRESH_TOKEN, SERVICE_TOKEN,
SIGNING_KEY, DATABASE_CREDENTIAL, WEBHOOK_SECRET, PORTAL_CREDENTIAL.

## CredentialReference

Agents/services receive opaque references, never raw secrets:

```yaml
credential_ref_id: provider: tenant_id: owner_principal_or_service:
allowed_capabilities: allowed_destinations: status: expires_at:
rotation_policy:
```

## Vault requirements

Encryption at rest, access audit, rotation/revocation, no plaintext
application logs, no secret export to agent context, bounded environment
injection, OAuth tokens tied to the correct tenant/account.

## Rules (VAULT-001..007)

1. Agents/services get opaque refs, never raw secrets (SEC-LAW-006).
2. A ref is usable only for its allowed capabilities and destinations.
3. A ref is tenant-bound; wrong-tenant use is denied.
4. Rotation preserves capability without changing prompts or Hermes memory.
5. Prompts, sidechains and logs contain no raw secret (mandatory redaction).
6. Revocation denies immediately.
7. Worker runtimes read only credentials inside their granted capability.

## Implementation

- `config/g0/security/credential_vault_policy.yaml`
- `schemas/g0/security/credential_reference.schema.json`
- `prototype/g0/security/authn.py` (`CredentialVault`: `resolve`, `rotate`,
  `revoke`, `redact`, `prompt_contains_no_raw_secret`)
- `tools/g0/validate_authn_credentials.py`
- `tests/g0/book6/test_authn_credentials.py`
