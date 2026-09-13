---
name: handoff
description: Manually capture the current agent session in a self-contained, verifiable handoff document so a fresh agent session can safely resume it. Use when context is running low or work must move to another environment. Supports private local handoffs and explicitly configured portable project handoffs.
disable-model-invocation: true
---

# Handoff

Write a concise handoff document for a future agent session. Read
[`references/handoff-format.md`](references/handoff-format.md) first; it is the binding
v2 format, storage, and safety contract.

## Procedure

1. Determine storage mode before gathering content. Use portable/project mode only when
   the repository has `.agent/handoff.yaml` selecting it; otherwise use local/private
   mode. In portable mode, check that the handoff contains no secrets or sensitive local
   values. If it cannot be safely shared, use local/private mode and explain why.
2. Ground the document in observable state. Inspect repository root, remote, branch,
   full HEAD SHA, whether HEAD is available on its remote branch, working-tree status,
   and changed files. If work remains uncommitted, list each dirty file and the intent of
   its change. Do not invent unavailable facts.
3. Identify relevant on-disk specs, plans, ADRs, tests, and key implementation files;
   cite their repository-relative paths and relevant sections rather than copying them.
   Also record durable artifacts and ephemeral setup that a new session must recreate.
4. Write a v2 document with every required frontmatter field and section, in the exact
   contract order. Capture the goal, completed work (including rejected approaches and
   unverified work), remaining direction, definition of done and verification, settled
   decisions, human questions, applicable tools/workflows, and gotchas.
5. Write it to the active mode's location. In local/private mode, use the contract's
   deterministic temporary fallback only when persistent home storage is unavailable;
   create its directory with user-private permissions where supported and warn that it
   may not survive the environment. Creating the requested handoff is authorized by
   invoking this skill, but do not commit, push, or otherwise share it. In portable mode,
   tell the user that they must deliberately commit and share it for another environment
   to access it.
6. Report the full path, storage mode, any temporary-storage limitation, and a short
   summary.

## Rules

- Do not reproduce documents already on disk or embed a full diff.
- Do not prescribe commands or prompts for the next agent; supply exact facts and useful
  direction, then leave implementation judgement to that agent.
- Do not place a local/private handoff in the repository.
- Do not write credentials, tokens, private keys, or exported secret values in either
  mode.
- Do not commit code merely to make a handoff portable. State whether the recorded code
  is committed and available remotely so the next session can reconcile it.
