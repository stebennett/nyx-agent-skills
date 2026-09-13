# Handoff skill validation

Run this whenever either generic handoff skill or the shared protocol changes.

## Automated checks

Run from the repository root:

```text
python3 skills/_shared/validate.py
```

The dependency-free validator checks that contract copies are byte-identical, skill
frontmatter and local Markdown links are valid, v2 fixtures contain required fields and
ordered headings, dirty fixtures describe dirty files, and fixture discovery covers root
and remote matching, consumption, supersession, newest selection, ambiguity, malformed
rejection, and explicit-path v1 compatibility.

## Manual checks

- Without `.agent/handoff.yaml`, confirm writes use `AGENT_HANDOFF_DIR`, then
  `~/.agent/handoffs/`, then `${TMPDIR:-/tmp}/agent-handoffs/` only when home storage is
  unavailable. Confirm temporary fallback use is reported.
- With the documented portable configuration, confirm writes remain under the configured
  repository directory and `AGENT_HANDOFF_DIR` does not redirect them.
- Confirm a portable writer warns that it neither commits nor pushes and redirects a
  secret-bearing handoff to local/private storage.
- Confirm `continue` performs only reads and read-only inspection before unambiguous
  approval, including no consumption-state update.
- Confirm approved v2 consumption updates only local state and never edits portable
  documents; confirm approved v1 consumption alone may change `status: consumed`.
- Confirm a legacy v1 handoff is accepted only when its path is supplied. Automatic v2
  discovery must not scan `~/.claude/handoffs/` or its temporary legacy fallback.
- Confirm a second checkout can consume a deliberately committed and shared portable
  handoff after footing validation and approval.

Intentional Claude paths are permitted only in legacy compatibility or migration
material. Core skill instructions must not require vendor-specific paths or features.
