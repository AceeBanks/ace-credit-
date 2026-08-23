# ADR-0002 — Legal Entity & Tenancy Boundary

- **Status:** Accepted for Phase 1
- **Date:** 2026-08-23
- **Decision owners:** Project owner + legal/compliance review before production
- **Applies to:** nonprofit, for-profit, shared application infrastructure

## Context
ACE Credit is being designed as an ecosystem with separate nonprofit and for-profit legal entities. The organizations may share brand strategy, founder expertise, software, curriculum, vendors, referrals, or documented services where lawful, but separate finances, payroll, grants, contracts, governance, and legal obligations must remain enforceable.

A common software platform can reduce duplicate engineering, but an ordinary single-tenant CRM model would create unacceptable ambiguity about record ownership, data access, grant-funded activity, and cross-entity use.

## Decision
The application will treat **legal entity as a first-class security and data ownership boundary**.

The initial target architecture is one shared codebase with explicit entity tenancy, not one undifferentiated database context.

Every operational transaction must resolve an `entity_id` or equivalent entity context.

## Required rules
1. Programs belong to one entity.
2. Grants/awards belong to one entity.
3. Contracts belong to one entity.
4. Staff memberships and permissions are entity-scoped.
5. Participant enrollments are entity-scoped.
6. Commercial engagements are entity-scoped.
7. Case records are entity-scoped.
8. Agent profiles/runs must declare entity context for operational work.
9. Audit events include entity context.
10. Exports/reports are generated from an explicit entity context.
11. Cross-entity data access is denied by default.
12. A user with roles in both entities receives separate memberships; one membership does not imply the other.

## Shared identity
A minimal `Person` identity anchor may be shared at the platform level to reduce duplicate account/login handling, subject to privacy review.

However:
- entity A cannot read entity B relationship data merely because both link to the same Person;
- participant/client status is not stored as a universal global role;
- cross-entity matching/linking must be purpose-limited;
- consent or other lawful basis may be required for specific data reuse or transfer;
- sensitive notes/documents never become globally visible by default.

## Data ownership categories

### Entity-owned
Default for operational records: programs, applications, enrollments, cases, notes, grants, contracts, credit workflows, outcomes, staff records, client engagements.

### Shared reference
May include public curriculum templates, resource directories, generic form definitions, code/configuration, non-sensitive taxonomies.

### Shared identity/control
Potentially authentication identity, policy framework, audit infrastructure, and system metadata. Access to underlying entity data remains scoped.

### Prohibited implicit sharing
- participant case notes → commercial sales record;
- grant-funded participant data → for-profit marketing;
- nonprofit staff time/cost → commercial operation without documented arrangement;
- commercial client data → nonprofit reporting;
- one entity's credentials/integrations → other entity without authorization;
- unrestricted document visibility across entity contexts.

## Authorization model
Authorization should evaluate at least:
`actor + entity membership + permission + target entity + resource + data class + contextual policy + approval state`.

Roles alone are insufficient for highly sensitive data. Attribute/context checks may restrict survivor-sensitive, credit, HR, or legal records further.

## Database implementation guidance
Exact database technology is deferred, but implementation must make missing entity filters difficult.

Preferred safeguards may include:
- mandatory `entity_id` foreign key on entity-owned records;
- database row-level security where supported;
- repository/service methods requiring entity context;
- composite uniqueness including entity where appropriate;
- tests proving cross-entity denial;
- separate storage prefixes/buckets/keys for sensitive documents;
- per-entity encryption keys later if risk/scale justifies;
- per-entity integration credentials when practical.

Do not rely only on UI filters.

## Finance/grant boundary
The application may track budgets, restrictions, payroll allocations, and grant-funded service delivery, but it must not create accounting entries that blur entities.

If later integrated with accounting/payroll:
- each transaction is linked to the correct legal entity;
- grant restrictions attach to the receiving entity;
- staff allocation methodology is explicit;
- related-party/vendor transactions are documented;
- accounting system remains authoritative for books unless a later ADR says otherwise.

## Shared services between entities
Possible, but only through an explicit relationship record and approved agreement. The platform should be capable of storing:
- service provider entity;
- receiving entity;
- scope;
- effective dates;
- pricing/cost allocation;
- approval;
- contract/reference;
- data-sharing terms;
- conflict/related-party review status.

Software must not invent the legal sufficiency of such an agreement.

## Alternatives considered

### A. Completely separate codebases/databases from day one
Not selected as the initial default because it may duplicate engineering and reporting infrastructure. It remains a valid future isolation option.

### B. One ordinary shared CRM with tags for nonprofit/for-profit
Rejected. Tags are not a sufficient legal/security boundary.

### C. One shared database with entity-aware application controls only
Potentially acceptable for early implementation but should be strengthened with database-level controls where practical.

### D. One shared identity plus separate entity databases
Deferred as a possible later architecture if compliance, contracts, scale, or risk require stronger physical separation.

## Consequences
### Positive
- supports one platform without legal ambiguity;
- enables staff who legitimately work in both entities while retaining scoped access;
- clearer audits/reports;
- facilitates later physical data separation;
- supports grant/program integrity.

### Negative
- every query/workflow must respect entity context;
- more complex test fixtures and authorization;
- cross-entity analytics require deliberate aggregated paths;
- shared identity/privacy design needs care.

## Required tests before production
- user with nonprofit-only role cannot read/write for-profit records;
- user with for-profit-only role cannot read/write nonprofit records;
- user with both roles must select/resolve correct active entity;
- agent cannot omit entity context for operational write;
- exports never include another entity by default;
- object/file access checks entity ownership;
- ID guessing cannot cross boundary;
- background jobs preserve entity scope;
- logs/audit include entity scope without leaking protected values.

## Revisit triggers
- legal counsel requires physical database separation;
- external partner/funder contract requires dedicated environment;
- security review finds row-level tenancy insufficient;
- product expands to unrelated third-party organizations/SaaS multi-tenancy;
- shared identity becomes unnecessary or too privacy-sensitive.
