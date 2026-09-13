---
name: continue
description: Manually resume work from a generic handoff document: validate its repository footing and sources, then present a continuation plan for explicit user approval before making any change.
disable-model-invocation: true
---

# Continue

Read a handoff and prepare a safe, approval-gated continuation. Read
[`references/handoff-format.md`](references/handoff-format.md) first; it defines v2
storage/discovery and legacy v1 compatibility.

> Do not modify code, files, git state, handoff state, or external systems before the
> user explicitly approves the continuation plan you present. Reading and read-only
> inspection are allowed.

## Procedure

1. If the user supplied a handoff path, use it. Otherwise determine the active storage
   mode from `.agent/handoff.yaml` and discover v2 records only in that mode's directory
   according to the contract. Do not automatically scan legacy locations; a v1 handoff
   requires a user-supplied path. If no matching v2 record exists, ask for its
   path. If the newest candidates tie or cannot be safely ordered, show their paths,
   timestamps, and one-line goals and ask the user to select one.
2. Parse frontmatter and validate the schema and all required headings. For an unknown
   future version, identify the limitation and rely only on recognized fields. For a
   malformed document, state exactly what is absent instead of guessing.
3. Verify the recorded footing with read-only inspection: current branch, full HEAD SHA,
   remote availability where relevant, and working tree. Compare every mismatch with the
   recorded starting state; do not conceal or silently reconcile it.
4. Reread all cited primary sources and the key files named in completed/outstanding
   work. The handoff is a map, not a replacement for those sources.
5. Present a reviewable continuation plan: restated goal and definition of done, actual
   footing and discrepancies, proposed ordered steps, applicable skills/tools/workflows,
   settled boundaries, all human questions, and risks or unverified claims.
6. Stop and wait for unambiguous approval. A plan-mode approval feature may help, but is
   not required and does not replace clear user authorization.
7. After approval only, record consumption according to the contract and execute the
   approved plan. For a v2 document, record consumption in local agent state without
   editing the document; portable documents remain immutable. For legacy v1 only, set
   `status: consumed`. If another handoff is needed later, invoke `handoff` and set its
   `supersedes` value to this document's filename.

## Guardrails

- User acknowledgement, silence, or an ambiguous response is not approval.
- Authorisation covers only the plan presented; obtain fresh approval for a materially
  different approach or an unresolved human question.
- Treat `## Decisions made (do not relitigate)` as binding and stop to ask about anything
  in `## Open questions (needs human)`.
- Never fabricate a referenced source, completed claim, repository state, or local
  consumption record.
