# nyx-agent-skills

Vendor-neutral Agent Skills for preserving and safely resuming agent work across sessions.

## Implemented skills

### `handoff`

Creates a concise, verifiable handoff document for a future agent session. It records
repository footing, completed and outstanding work, settled decisions, human questions,
references to primary on-disk sources, and durable versus ephemeral environment state.

- Defaults to private local storage: `AGENT_HANDOFF_DIR`, then `~/.agent/handoffs/`.
- Supports opt-in portable project storage through `.agent/handoff.yaml` and
  `.agent/handoffs/`.
- Never commits or pushes a handoff; portable handoffs must be deliberately shared.
- Excludes credentials, tokens, private keys, and exported secret values.
- Writes v2 documents only.

### `continue`

Safely resumes a handoff by validating it and presenting a continuation plan before any
mutation.

- Prefers a user-supplied handoff path; otherwise discovers matching v2 records in the
  active storage mode.
- Verifies branch, commit, remote availability, working tree, and cited primary sources.
- Surfaces mismatches, open questions, and unverified claims.
- Requires unambiguous user approval before changing repository, handoff, consumption, or
  external state.
- Records v2 consumption locally without editing portable handoffs.
- Supports legacy v1 documents only when the user supplies an explicit path.

## Storage modes

Local/private storage is the default and is intended for same-environment continuation.
Portable/project storage is enabled by this tracked repository configuration:

```yaml
# .agent/handoff.yaml
version: 1
storage:
  mode: portable
  directory: .agent/handoffs
```

Portable handoffs become available in another clone or environment only after the user
commits and shares them. See [skills/MIGRATION.md](skills/MIGRATION.md) for the complete
storage and migration policy.

## Installation

Each skill is independently installable:

- `skills/handoff/`
- `skills/continue/`

Expose these directories through the selected harness’s skill-discovery mechanism. In pi,
use a global or trusted-project skill location, the `skills` setting, or `--skill <path>`;
then invoke `/skill:handoff` or `/skill:continue`.

See [skills/README.md](skills/README.md) for integration requirements and degraded
behavior when a harness cannot read files, write state, inspect Git, or obtain approval.

## Validation

Run the dependency-free validator from the repository root:

```text
python3 skills/_shared/validate.py
```

It validates the shared contracts, skill metadata and links, fixture schemas, and
fixture-based discovery behavior. Manual safety checks are documented in
[skills/VALIDATION.md](skills/VALIDATION.md).
