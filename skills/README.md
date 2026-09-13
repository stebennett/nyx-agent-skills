# Generic Agent Skills

This directory contains vendor-neutral, independently installable Agent Skills.

## Included skills

- `handoff/` — write a verifiable handoff for a future agent session. It defaults to
  local/private storage and supports explicit portable/project storage.
- `continue/` — validate and resume a handoff after explicit user approval.

## Layout

- `<skill-name>/SKILL.md` — the skill’s instructions and metadata.
- `<skill-name>/references/` — material loaded by that skill on demand.
- `_shared/fixtures/` — cross-skill test fixtures; this is not an installable skill.
- `_shared/validate.py` — dependency-free static and fixture validator.
- `VALIDATION.md` — automated and manual verification guidance.

Each skill is self-contained: it does not require another skill’s relative files at
runtime. Shared protocols needed by two independently installed skills are copied into
each skill and must be kept byte-identical, or packaged by a target harness as an
explicit shared dependency.

## Installation and integration

Install or expose each skill directory through the skill-discovery mechanism of the
chosen harness. The harness must let the agent read the selected handoff directory,
write a handoff and local consumption state, inspect repository state read-only, and ask
the user for explicit approval. If it cannot read files, it cannot safely consume a
handoff. If it cannot write files, it may draft but cannot persist a handoff or
consumption record. If it cannot inspect the repository, it must report footing as
unverified. If it cannot obtain interactive approval, it must stop after presenting the
plan.

### pi

Pi can discover skill directories from its global or trusted-project skill locations,
from its `skills` setting, or through repeated `--skill <path>` options. Expose both
`handoff/` and `continue/`, and ensure the pi process can read/write the configured
handoff and local consumption-state locations. Users can invoke them with
`/skill:handoff` and `/skill:continue`; a project instruction may also remind the agent
when to use the pair. The included `disable-model-invocation: true` is supported by pi to
keep these manual-only; harnesses that do not support this optional frontmatter field may
ignore or remove it while preserving the instruction-level approval gate.

See [`../CONVERSION_PLAN.md`](../CONVERSION_PLAN.md), [`MIGRATION.md`](MIGRATION.md), and
[`VALIDATION.md`](VALIDATION.md).

## Adding a skill

1. Create `skills/<skill-name>/SKILL.md` with standard Agent Skill frontmatter.
2. Add only skill-specific supporting files under `references/`.
3. Put reusable test data under `_shared/fixtures/`.
4. Keep harness integrations optional and document them without making a particular
   harness a runtime dependency.
