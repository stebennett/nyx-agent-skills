# Portable handoff document format

This is the shared v2 protocol for the generic `handoff` writer and `continue` reader.
Both skills must implement it. It is self-contained in each installable skill so either
skill can be installed alone; matching copies must change together.

## Storage policy

### Local/private mode (default)

Write outside the repository to `AGENT_HANDOFF_DIR` when set, otherwise to
`~/.agent/handoffs/`. If no persistent home directory is available, use the deterministic
temporary fallback `${TMPDIR:-/tmp}/agent-handoffs/`. Create a local directory with
user-private permissions where the platform supports them. Tell the user when the
temporary fallback is used: it may be removed with the temporary environment and is not
a durable cross-session transport.

### Portable/project mode (opt-in)

A repository opts in with this tracked configuration:

```yaml
# .agent/handoff.yaml
version: 1
storage:
  mode: portable
  directory: .agent/handoffs
```

`directory` is repository-root-relative and must stay inside the repository. In this
mode the writer places documents there. It never commits or pushes them; the user must
deliberately share the handoff. `AGENT_HANDOFF_DIR` does not override portable mode.

Before creating a portable handoff, exclude credentials, tokens, private keys, exported
secret values, and sensitive machine-specific data. Keep it local/private if that is not
possible.

## Naming and discovery

Files are named `<project>-<YYYYMMDD-HHMMSS>-<id>.md`, where `project` is the repository
root basename and `id` is a writer-generated identifier safe for filenames. Timestamps
sort chronologically. Handoff documents are matched by `repo_root` or `remote`, never
by filename alone.

A reader uses an explicit path when supplied. Otherwise it searches **only the active
v2 mode's directory**. It rejects malformed or unsupported-version documents from
candidate selection, excludes documents superseded by a newer matching document, and
excludes locally consumed documents when its local state is available. It selects the
remaining document with the newest parseable `created` timestamp. If two or more newest
candidates have the same timestamp, or their timestamps cannot be safely ordered, it
presents their paths, timestamps, and one-line goals and asks the user to choose. If no
v2 record matches, it asks for a path; it does not automatically search legacy locations.

Consumption is local state, keyed by handoff path and `id`; its implementation location
is harness-specific. It is updated only after the user approves a continuation plan.
Portable documents are immutable: do not edit them to record consumption. A reader on a
different machine may not have the local consumption record, so it must still validate
footing and obtain approval before acting.

## Version 2 file structure

A v2 document is YAML frontmatter followed by all required sections, in the stated
order. Empty sections contain `None.`.

```yaml
---
schema_version: 2
id: <writer-generated identifier>
project: <repo-root basename>
repo_root: <absolute path to repo root>
remote: <origin remote URL, or "">
branch: <current branch name>
head_sha: <full HEAD commit SHA>
branch_pushed: <true|false>
working_tree: <clean|dirty>
storage_mode: <local|portable>
created: <ISO 8601 timestamp with offset>
supersedes: <prior handoff filename or "">
---
```

Required headings, exactly spelled and ordered:

1. `## Goal`
2. `## Starting state`
3. `## Completed`
4. `## Outstanding & next steps`
5. `## Definition of done`
6. `## Decisions made (do not relitigate)`
7. `## Open questions (needs human)`
8. `## Skills / agents / workflows to use`
9. `## References (on disk — read, don't duplicate)`
10. `## Environment`
11. `## Notes & gotchas`

`## Starting state` states the branch, `head_sha`, pushed status, and an explicit
instruction to compare the current HEAD before acting. When dirty, it lists every dirty
file and the intent of its change; it never embeds a full diff.

Across all sections, reference existing documents by repository-root-relative path and
specific section rather than copying them. Describe remaining work as direction and
constraints, not commands to paste. Facts such as paths, test ids, SHAs, and URLs must
be exact.

## Reader obligations

A reader validates the schema and required headings, compares current branch, HEAD, and
working tree with the recorded footing, and surfaces any mismatch. It rereads every
referenced primary source, respects settled decisions, and asks about open human
questions. It presents a concrete continuation plan and waits for explicit approval
before changing files, git state, the consumption record, or anything external.

## Legacy version 1

During migration, a reader accepts a Claude-specific v1 document **only when the user
supplies its explicit path**. Typical legacy locations are `~/.claude/handoffs/` and,
when no home directory was available, `${TMPDIR:-/tmp}/claude-handoffs/`. A v2 reader
does not scan either location automatically.

It honours a v1 document's `status` field and may set it to `consumed` only after
approval. Writers create v2 only. Discovery and validation never relocate or rewrite a
v1 document merely to migrate it.
