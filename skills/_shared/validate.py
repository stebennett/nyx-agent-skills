#!/usr/bin/env python3
"""Dependency-free checks for the generic handoff skill bundle."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CONTRACTS = [
    SKILLS / "handoff/references/handoff-format.md",
    SKILLS / "continue/references/handoff-format.md",
]
HEADINGS = [
    "## Goal", "## Starting state", "## Completed", "## Outstanding & next steps",
    "## Definition of done", "## Decisions made (do not relitigate)",
    "## Open questions (needs human)", "## Skills / agents / workflows to use",
    "## References (on disk — read, don't duplicate)", "## Environment",
    "## Notes & gotchas",
]
V2_FIELDS = {
    "schema_version", "id", "project", "repo_root", "remote", "branch", "head_sha",
    "branch_pushed", "working_tree", "storage_mode", "created", "supersedes",
}
V1_FIELDS = V2_FIELDS - {"id", "storage_mode"} | {"status"}

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter delimiter")
    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        raise ValueError("missing closing frontmatter delimiter")
    data: dict[str, str] = {}
    for line in parts[0].splitlines()[1:]:
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data, parts[1]


def validate_document(path: Path) -> dict[str, str] | None:
    try:
        data, body = frontmatter(path)
    except ValueError as exc:
        fail(f"{path.name}: {exc}")
        return None
    version = data.get("schema_version")
    expected = V2_FIELDS if version == "2" else V1_FIELDS if version == "1" else set()
    missing = expected - data.keys()
    if missing:
        fail(f"{path.name}: missing frontmatter fields {sorted(missing)}")
    positions = [body.find(heading) for heading in HEADINGS]
    missing_headings = [h for h, pos in zip(HEADINGS, positions) if pos < 0]
    if missing_headings:
        fail(f"{path.name}: missing headings {missing_headings}")
    elif positions != sorted(positions):
        fail(f"{path.name}: headings are not ordered")
    if version == "2":
        if data.get("working_tree") not in {"clean", "dirty"}:
            fail(f"{path.name}: invalid working_tree")
        if data.get("storage_mode") not in {"local", "portable"}:
            fail(f"{path.name}: invalid storage_mode")
        if data.get("working_tree") == "dirty" and "Dirty file" not in body:
            fail(f"{path.name}: dirty tree lacks dirty-file description")
    return data


def created(data: dict[str, str]) -> datetime | None:
    try:
        return datetime.fromisoformat(data["created"])
    except (KeyError, ValueError):
        return None


def discover(paths: list[Path], repo_root: str, remote: str, consumed: set[str] = set()):
    """Model contract selection: v2 inputs only; return selected path, 'ambiguous', or None."""
    records = []
    for path in paths:
        data, _ = frontmatter(path)
        if data.get("schema_version") != "2" or path.name in consumed:
            continue
        if data.get("repo_root") != repo_root and data.get("remote") != remote:
            continue
        stamp = created(data)
        if stamp is None:
            continue
        records.append((path, data, stamp))
    superseded = {data.get("supersedes") for _, data, _ in records if data.get("supersedes")}
    records = [record for record in records if record[0].name not in superseded]
    if not records:
        return None
    newest = max(record[2] for record in records)
    winners = [record for record in records if record[2] == newest]
    return "ambiguous" if len(winners) != 1 else winners[0][0].name


def check_links() -> None:
    link = re.compile(r"\[[^]]+\]\(([^)#]+)(?:#[^)]+)?\)")
    for path in SKILLS.rglob("*.md"):
        for target in link.findall(path.read_text(encoding="utf-8")):
            if not (path.parent / target).resolve().exists():
                fail(f"{path.relative_to(ROOT)}: unresolved link {target}")


def check_discovery(documents: dict[str, dict[str, str]]) -> None:
    def paths(*names: str) -> list[Path]:
        return [FIXTURES / name for name in names]
    cases = [
        ("newest", paths("v2-oldest-open.md", "v2-newest-open.md"), "/work/selection", "https://example.test/org/selection.git", set(), "v2-newest-open.md"),
        ("superseded", paths("v2-superseded-old.md", "v2-superseding-new.md"), "/work/chain", "https://example.test/org/chain.git", set(), "v2-superseding-new.md"),
        ("ambiguous", paths("v2-ambiguous-a.md", "v2-ambiguous-b.md"), "/work/ambiguous", "https://example.test/org/ambiguous.git", set(), "ambiguous"),
        ("consumed", paths("v2-local-open.md"), "/work/example", "https://example.test/org/example.git", {"v2-local-open.md"}, None),
        ("remote", paths("v2-remote-match.md"), "/other/checkout", "https://example.test/org/remote-match.git", set(), "v2-remote-match.md"),
        ("legacy-not-auto-discovered", paths("v1-open.md"), "/work/example", "https://example.test/org/example.git", set(), None),
    ]
    for name, candidates, root, remote, consumed, expected in cases:
        actual = discover(candidates, root, remote, consumed)
        if actual != expected:
            fail(f"discovery {name}: expected {expected!r}, got {actual!r}")
    for name in ("v1-open.md", "v1-consumed.md"):
        if documents[name].get("schema_version") != "1":
            fail(f"{name}: explicit-path legacy fixture is not v1")


def main() -> int:
    if CONTRACTS[0].read_bytes() != CONTRACTS[1].read_bytes():
        fail("handoff format copies differ")
    for skill in (SKILLS / "handoff", SKILLS / "continue"):
        skill_file = skill / "SKILL.md"
        if not skill_file.exists():
            fail(f"{skill.name}: missing SKILL.md")
        elif "description:" not in skill_file.read_text(encoding="utf-8"):
            fail(f"{skill.name}: missing skill description")
    check_links()
    for skill_file in (SKILLS / "handoff/SKILL.md", SKILLS / "continue/SKILL.md"):
        if "Claude" in skill_file.read_text(encoding="utf-8"):
            fail(f"{skill_file.relative_to(ROOT)}: vendor-specific core instruction")

    documents: dict[str, dict[str, str]] = {}
    for path in sorted(FIXTURES.glob("*.md")):
        if path.name == "malformed-v2.md":
            try:
                data, body = frontmatter(path)
                if data.get("schema_version") != "2" or not (V2_FIELDS - data.keys()) or all(h in body for h in HEADINGS):
                    fail("malformed-v2.md: no longer malformed")
            except ValueError:
                pass
            continue
        data = validate_document(path)
        if data is not None:
            documents[path.name] = data
    check_discovery(documents)
    if errors:
        print("Validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
