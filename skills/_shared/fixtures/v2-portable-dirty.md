---
schema_version: 2
id: portable-example-002
project: example
repo_root: /work/example
remote: https://example.test/org/example.git
branch: feature/example
head_sha: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
branch_pushed: false
working_tree: dirty
storage_mode: portable
created: 2026-01-02T10:00:00+0000
supersedes: ""
---
## Goal
Resume the portable example task.
## Starting state
Branch `feature/example`; HEAD `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`; pushed: false. Dirty file `src/example.js`: partial validation change. Confirm HEAD and reconcile the dirty tree before acting.
## Completed
Validation approach selected; it is unverified.
## Outstanding & next steps
Finish and verify validation.
## Definition of done
Relevant validation tests pass.
## Decisions made (do not relitigate)
Keep the selected validation approach.
## Open questions (needs human)
None.
## Skills / agents / workflows to use
None.
## References (on disk — read, don't duplicate)
None.
## Environment
Durable: local branch only. Ephemeral to re-establish: None.
## Notes & gotchas
This fixture must contain no secrets.
