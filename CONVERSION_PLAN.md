# Plan: convert `handoff` and `continue` into generic Agent Skills

## Objective

Produce a vendor-neutral pair of Agent Skills that preserve the existing handoff/continuation workflow and its safety guarantees, while working in harnesses such as Claude Code, pi, and other skill-capable agents.

## Findings from the Claude Code sources

- `handoff` writes a structured, external handoff record; `continue` discovers, validates, and consumes it.
- Their shared `handoff-format.md` is the real protocol. It defines storage, discovery, YAML fields, required section order, state verification, and schema versioning.
- The core workflow is portable: capture observable repository state, reference primary sources rather than duplicating them, verify state on pickup, propose a plan, and require explicit approval before mutation.
- Claude-specific assumptions must be removed or isolated: `~/.claude/handoffs`, `${TMPDIR:-/tmp}/claude-handoffs`, `CLAUDE.md`, Claude slash-command terminology, and an optional harness plan-approval gate.
- `continue` currently links to the contract through the sibling Claude skill layout. The generic distribution needs a stable, self-contained relative layout.

## Target layout

Create a distributable skill bundle, separate from the source reference material:

```text
skills/
  handoff/
    SKILL.md
    references/
      handoff-format.md
  continue/
    SKILL.md
    references/
      handoff-format.md
  README.md
```

Keep the identical contract file in both skills initially (or package it once as a shared resource if the target installer supports shared files). Document that the two copies must be updated atomically. This keeps either skill independently installable, which is more compatible with existing harnesses.

## Conversion work

1. **Define generic terminology and invocation behavior.**
   - Replace “Claude Code session” with “agent session” and “Claude session” with “fresh agent session.”
   - Describe invocation in natural language rather than slash-command syntax.
   - Retain manual invocation: `handoff` is used before context loss; `continue` is used to resume a handed-off task, optionally with an explicit file path.

2. **Make handoff storage a configurable transport policy.**
   - Define **local/private** mode as the safe default: `AGENT_HANDOFF_DIR` overrides the location; otherwise use a neutral per-user location such as `~/.agent/handoffs`, with a temporary-directory fallback only when persistent home storage is unavailable.
   - Define opt-in **portable/project** mode through tracked `.agent/handoff.yaml`, with `storage.mode: portable` and repository-root-relative `storage.directory: .agent/handoffs/`. This makes a handoff available in another clone, machine, container, or harness after the user commits and shares it.
   - Never auto-commit or auto-push either code or handoffs. In portable mode, report that the document must be committed/shared to cross environments; in local mode, report its local-only scope.
   - Treat portable handoffs as immutable after creation. Record local consumption in the consumer's state store, or create a successor with `supersedes`, rather than creating routine shared `status: consumed` edits and merge churn.
   - Require a portability/secret review: local auth, tokens, and exported values are never written, and sensitive handoffs stay in local/private mode.
   - State that harness integrations may configure either mode. A pi integration can choose its stable per-user state directory for local mode without changing the skill.

3. **Publish a generic v2 handoff contract.**
   - Derive it from the existing contract, changing only vendor-bound location/configuration and terminology.
   - Bump `schema_version` to `2`, because location, discovery, and consumption rules change. Require readers to continue accepting v1 documents at the legacy Claude locations during migration.
   - Retain the required frontmatter and section schema, repository matching by `repo_root` or remote, consumed status, `supersedes`, exact facts, relative references, and the no-embedded-diff policy.
   - Add an explicit compatibility section: a v2 reader recognizes v1, uses its recorded/legacy location rules, and never rewrites a v1 document merely to migrate it.

4. **Rewrite `handoff/SKILL.md` as a generic writer.**
   - Keep the evidence-gathering requirements: repository identity, branch, commit, pushed state, dirty-file intent, referenced documents, and durable versus ephemeral environment state.
   - Keep the content-quality guidance and the hard rules against duplicating on-disk documents and prescribing pasteable next commands.
   - Replace shell-specific implementation advice with portable requirements. Where an agent has tools, it should use read-only repository inspection; where it cannot determine a value, it should state the limitation rather than invent it.
   - Require the final response to name the written file and summarize it.

5. **Rewrite `continue/SKILL.md` as a generic reader with an approval gate.**
   - Keep explicit-path preference, discovery/multiple-candidate behavior, schema validation, footing verification, primary-source rereading, and plan construction.
   - Express the approval gate independently of harness capabilities: no mutations before an unambiguous user approval of the presented plan. Harness plan mode is optional acceleration, not a dependency.
   - Treat marking a handoff consumed as a mutation that happens only after approval. Preserve the requirement to surface mismatches, unresolved questions, and unverified claims.
   - Replace references to Claude-specific skills/agents/slash commands with “available skills, subagents, tools, or workflows”; handoff documents may still name project-specific resources.

6. **Add harness integration guidance in `skills/README.md`.**
   - Explain installation/discovery at a conceptual level, without asserting one vendor’s directory convention.
   - Give a short pi note: install/expose both `SKILL.md` files through pi’s skill mechanism, ensure the agent can read/write the configured handoff directory, and optionally provide a project instruction that reminds the agent when to use the pair.
   - Specify minimum harness capabilities (read files, write files, inspect repository state, ask for approval) and degraded behavior when a capability is unavailable.

7. **Validate the bundle.**
   - Add fixture handoffs for v2 local/private and portable/project cases, clean and dirty trees, locally consumed records, malformed documents, and legacy v1 cases.
   - Test/document discovery selection: explicit path; matching repo root; matching remote across a different checkout; newest open record; consumed filtering; ambiguous candidates.
   - Review both skills against a checklist: shared contract links resolve after independent installation, all v2 required fields/headings are handled, no vendor path remains in core instructions, and no mutation is permitted before approval.

## Compatibility and migration decisions

- The original `references/productivity/` files remain unchanged as upstream reference material.
- New generic skills write v2 documents only and select local/private mode unless the project explicitly opts into portable/project mode.
- Generic `continue` should read legacy v1 Claude documents during the migration period; generic `handoff` does not need to create them.
- A v2 reader never relocates or edits a handoff during discovery/validation. After approval it records consumption locally for local/private documents; portable/project documents remain immutable and are superseded when another handoff is needed.

## Definition of done

- Two independently installable, vendor-neutral Agent Skills and their shared v2 contract exist under `skills/`.
- Their storage policy supports the documented local/private default and an explicit portable/project mode, plus `AGENT_HANDOFF_DIR` for local configuration.
- A local/private handoff is discoverable by a later session on the same stable user environment; a committed and shared portable/project handoff is discoverable and fully consumable in a different checkout of the same repository.
- The reader produces a footing-aware plan and does not modify repository, handoff, or external state before explicit approval.
- Legacy v1 handoffs are either supported as documented or rejected with a clear, actionable compatibility message.
- The bundle includes integration and validation documentation, including pi-specific installation considerations without making pi a runtime dependency.
