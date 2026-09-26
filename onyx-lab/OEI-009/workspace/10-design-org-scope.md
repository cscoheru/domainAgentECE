# OEI-009 — Org Scope Design (the OEI-010 hook)

> Status: **design + minimum model placement**, code touched in this cut
> (Identity.org_id / PermissionScope.org_id are now first-class; see
> `tests/unit/test_org_scope.py` for the deterministic rule). Implementation
> of org-scoped *memory* is **OEI-010**, not this cut.

---

## 1. The question

The OEI-010 cut will add **persistent memory** — both user-level
(preferences / facts about an individual) and **org-level** (canonical
terminology, templates, shared stances). The org-level memory must
follow the rule "memory write / read must go through the permission
engine, and **read** must happen **after** permission — otherwise we
re-introduce the post-filter side-channel that A6 closed".

This doc answers three questions:

1. What is the *org dimension*'s source of truth?
2. How does an org-level object become *visible*?
3. Who is allowed to *write* an org-level memory?

## 2. Source of truth for "which org does the user belong to"

Two candidates were floating around:

### 2.A. `X-Org-Id` request header

- **Pro**: zero DB writes; works for any tenant.
- **Con**: **caller-controlled** — a hostile caller can claim any org_id.
  This is the same anti-pattern as `/permissions/check`'s body-supplied
  user_ref (TASK §1.3 事实 B, V0→Production must-pass gate). Cannot be
  the source of truth for an authorization decision.

### 2.B. `0007_user_orgs` table (entity attribute)

- The 0007 migration added `org_id` to `context_requests`. The
  `entities.attributes` JSONB column carries department / roles /
  is_management and could carry org_id the same way.
- `resolve_identity` (parser.py) reads attributes → can populate
  `Identity.org_id` from there.
- **Pro**: trusted (DB-derived); same trust boundary as dept / roles.
- **Con**: every user must have an org_id set on their entity record
  before org-scoped authorization can fire.

**Decision**: **2.B**. The `X-Org-Id` header is removed from the
authorization path entirely; it stays available only for `/audit` and
`/debug` (where it's a hint, not a decision input). This matches
ADR-004 ("subject comes from the credential, never from the caller").

`Identity.org_id` (OEI-009 minimum placement) is populated by
`resolve_identity` from `entities.attributes.org_id`. Missing → None.
Missing is *not* the same as empty string — the filter treats `None` as
"no org claim" and falls through to the classification matrix.

## 3. How an org-level object becomes visible

Two scope classes we must support:

### 3.A. user-level object

Owner = one user. Visible to: owner only. Already covered by ACL rows
with `subject_type=user`. **No schema change** — works today.

### 3.B. org-level object

Owner = one org. Visible to: all users in the same org.

Two implementations considered:

**3.B.1**: New ACL row shape: `subject_type='org', subject_ref='<org_id>'`.
The `_subject_matches` function already supports arbitrary subject_types
if the matching logic is extended.

```python
if st == "org" and sr == identity.org_id:
    return True
```

Single change to `_subject_matches`. No schema change.

**3.B.2**: New `org_scope` column on `acl_entries`. Adds a tag dimension
orthogonal to subject_type. More expressive but doubles the model
surface.

**Decision**: **3.B.1**. One line of code in `_subject_matches`; no
migration; works with the existing ACL dataset.

The OEI-010 cut adds:

- `_subject_matches` line: `if st == "org" and sr == identity.org_id: return True`
- A `org_scope` literal on `EngineItem` / `KnowledgeObject` so the SPA can
  label "this is org-wide" vs "this is yours"
- A small seeded dataset (5–10 entries) to exercise the path

The OEI-009 deliverable is **just** the dataclass field on `Identity`
and `PermissionScope`, plus the unit test `test_user_level_object_visible_to_owner_only`
which exercises the existing path with a future org_id parametrisation.

## 4. Org-level memory WRITE permission

The hard open question — flagged by `REVIEW-sonnet-assessment.md §4.2`
— is **who can write an org-level memory row**.

### Candidate A: Admins only

- Pro: tightest; matches existing admin-only paths in ECE.
- Con: admins don't know the domain. A sales methodology term that should
  become canonical org memory needs a sales lead to propose it.

### Candidate B: "Org manager" role (is_management=True on the org)

- Pro: respects domain ownership. Sales lead manages sales memory; legal
  lead manages legal memory.
- Con: requires per-org `is_management` flag — schema churn.

### Candidate C: Anyone in the org, with peer review (async)

- Pro: open participation, captures knowledge at the source.
- Con: "peer review" is itself a workflow; OEI-010 says no approval
  flows.

### Candidate D: Anyone in the org, no review, but write is versioned

- Pro: simplest; can rollback.
- Con: garbage can leak into the org scope before review.

### Decision (for OEI-010)

**Candidate B for org-stance changes** (e.g. "we use 'consumption tax'
not 'sales tax'"), **Candidate A for safety-critical terms** (anything
that's checked into compliance workflows).

The OEI-009 deliverable does not lock this in — it's a product decision.
The design constraint is:

> **Org-level memory writes MUST go through `check_permission`**,
> using a new `effect: 'write'` row in `acl_entries`. The default is
> deny. Whether the predicate is "admin", "org manager", or
> "peer-reviewed" is a model parametrisation, not a code change.

The minimum OEI-010 plumbing: a `memory.write` ACL check on the write
path. Without it, OEI-009 closes this cut but leaves the door open for
OEI-010 to plug in any of A–D by adding rows to `acl_entries`.

## 5. Why this is "design + minimum placement" (TASK §4 step 4 + 5)

- The **placement** (carrier fields + unit test) ships in OEI-009.
- The **scope model finalization** (Candidate 3.B.1 above) is documented
  here; code change is one line in `_subject_matches` + a few seeded
  rows — fits in OEI-010.
- The **write permission candidates** are listed here so the OEI-010
  design picks one *before* it ships.

The TEST in `tests/unit/test_org_scope.py` that covers the *deterministic*
visibility rule (`test_user_level_object_visible_to_owner_only`) exercises
the existing ACL path with `Identity.org_id` populated — it does NOT
exhaust org-scoped ACL rows (those need OEI-010).