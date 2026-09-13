# Handoff storage migration

The source Claude Code skills use a single local directory, `~/.claude/handoffs/`. That
is appropriate for private, same-machine continuation, but it does not transport a
handoff to another clone, machine, container, or agent harness.

The generic `handoff` and `continue` skills support two explicit storage modes.

## Modes

### Local/private (default)

Use this for personal, sensitive, or same-environment continuation.

1. If set, `AGENT_HANDOFF_DIR` is the handoff directory.
2. Otherwise use `~/.agent/handoffs/`.
3. Only if no persistent home directory exists, use `${TMPDIR:-/tmp}/agent-handoffs/` as
   the temporary fallback; report that it may not survive the environment.

A local/private handoff is not expected to be available in a fresh environment. It must
not be committed, and its consumed state may be recorded in local agent state after user
approval.

### Portable/project (opt-in)

Use this when the next session may run in another checkout, machine, container, or
harness. Add this tracked project configuration:

```yaml
# .agent/handoff.yaml
version: 1
storage:
  mode: portable
  directory: .agent/handoffs
```

`directory` is repository-root-relative and must remain inside the repository. The
project configuration selects portable mode; `AGENT_HANDOFF_DIR` applies only to the
local/private mode and must not silently redirect portable documents outside the repo.

A portable handoff is available elsewhere only after the user deliberately commits and
shares it. The skill must report that requirement, but must never commit or push on the
user's behalf.

Portable handoffs are immutable after creation. `continue` must not update shared
frontmatter to mark one consumed; it records consumption locally. If work is handed off
again, the new document references the earlier one through `supersedes`.

## Security rules

Before writing a portable handoff, the agent must check that it contains no credentials,
tokens, private keys, exported secret values, or sensitive machine-specific data. Such
state belongs only in the document's instruction to re-establish the environment, not in
the document itself. Keep the handoff local/private if that separation is not possible.

## Schema and legacy compatibility

The generic format is schema version 2 because its storage, discovery, and consumption
semantics differ from the Claude-specific v1 format.

- Generic `handoff` writes v2 only.
- Generic `continue` accepts a legacy v1 document only when the user supplies its
  explicit path; it does not automatically scan legacy Claude locations.
- Discovery and validation never relocate or modify either v1 or v2 documents.
- A legacy v1 document retains its original `status: consumed` behavior when the user
  has approved continuation. A v2 portable document remains immutable.

## Choosing a mode

| Situation | Mode |
| --- | --- |
| Resume later on the same persistent workstation | Local/private |
| Resume in a different worktree on that workstation | Local/private |
| Resume from a new clone, remote runner, or another harness | Portable/project |
| Handoff includes information that cannot safely be shared | Local/private |

Harness integrations, including pi, may select the local directory through
`AGENT_HANDOFF_DIR`; they should respect `.agent/handoff.yaml` for portable/project
mode and expose it only when the repository and user workflow support deliberate
sharing. When no persistent home directory exists, both skills use the deterministic
v2 fallback `${TMPDIR:-/tmp}/agent-handoffs/`; it is temporary rather than durable.
