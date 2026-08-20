#!/usr/bin/env python3
"""Validate the repository's Agent Skills without third-party dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL_GLOB = "kits/*/.agents/skills/*/SKILL.md"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass(frozen=True)
class SkillMeta:
    path: Path
    name: str
    description: str


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> SkillMeta:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening YAML frontmatter delimiter")

    try:
        closing = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("missing closing YAML frontmatter delimiter") from exc

    fields: dict[str, str] = {}
    for line in lines[1:closing]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = unquote(value)

    name = fields.get("name", "").strip()
    description = fields.get("description", "").strip()
    if not name:
        raise ValueError("missing non-empty 'name'")
    if not description:
        raise ValueError("missing non-empty 'description'")
    if not NAME_RE.fullmatch(name):
        raise ValueError("'name' must be lower kebab-case")
    if "\n" in description or len(description) > 320:
        raise ValueError("'description' must be one concise line of at most 320 characters")
    if not any(line.strip() for line in lines[closing + 1 :]):
        raise ValueError("skill body is empty")

    folder_name = path.parent.name
    if folder_name != name:
        raise ValueError(f"folder name {folder_name!r} does not match skill name {name!r}")

    return SkillMeta(path=path, name=name, description=description)


def main() -> int:
    paths = sorted(ROOT.glob(SKILL_GLOB))
    if not paths:
        print(f"error: no skills matched {SKILL_GLOB}", file=sys.stderr)
        return 1

    errors: list[str] = []
    skills: list[SkillMeta] = []
    for path in paths:
        try:
            skills.append(parse_frontmatter(path))
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(f"{path.relative_to(ROOT)}: {exc}")

    by_name: dict[str, list[Path]] = {}
    for skill in skills:
        by_name.setdefault(skill.name, []).append(skill.path)
    for name, duplicates in sorted(by_name.items()):
        if len(duplicates) > 1:
            rendered = ", ".join(str(path.relative_to(ROOT)) for path in duplicates)
            errors.append(f"duplicate skill name {name!r}: {rendered}")

    for kit_dir in sorted((ROOT / "kits").glob("*")):
        if not kit_dir.is_dir():
            continue
        for required in ("AGENTS.md", "README.md", "SOURCES.md"):
            if not (kit_dir / required).is_file():
                errors.append(f"{kit_dir.relative_to(ROOT)}: missing {required}")

    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(skills)} skills:")
    for skill in skills:
        print(f"- {skill.name}: {skill.path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
