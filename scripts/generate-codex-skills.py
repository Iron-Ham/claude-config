#!/usr/bin/env python3
"""Generate Codex-normalized skill folders from repo skill sources."""

from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path


FRONTMATTER_KEYS = ("name", "description")


SPECIAL_REPLACEMENTS = {
    "last30days": [
        (
            'python3 "${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/last30days}/scripts/last30days.py" "$ARGUMENTS" --emit=compact 2>&1',
            'python3 "$HOME/.agents/skills/last30days/scripts/last30days.py" "$TOPIC" --emit=compact 2>&1',
        ),
        (
            "The script auto-detects sources (Bird CLI, API keys, etc). While waiting for it, do WebSearch.",
            "The script auto-detects sources (Bird CLI, API keys, etc). While waiting for it, use available web search to supplement the results.",
        ),
        (
            "For **ALL modes**, do WebSearch to supplement (or provide all data in web-only mode).",
            "For **ALL modes**, use available web search to supplement results or provide all data in web-only mode. If web search is unavailable, continue with script output and clearly state the gap.",
        ),
    ],
    "split": [
        (
            "You are executing the `/split` skill.",
            "You are executing the `$split` skill.",
        ),
        (
            "The skill runner populates `$ARGUMENTS` with everything after `/split`.",
            "Treat the user's prompt after `$split` as the argument string.",
        ),
        (
            "Extract from `$ARGUMENTS`:",
            "Extract from the argument string:",
        ),
        (
            'SPLIT_SCRIPT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/split}/scripts/split_diff.py"',
            'SPLIT_SCRIPT="$HOME/.agents/skills/split/scripts/split_diff.py"',
        ),
    ],
    "impeccable": [
        (
            "If neither source has context, you MUST run $impeccable teach NOW before doing anything else.",
            "If neither source has context, you MUST use `$impeccable teach` NOW before doing anything else.",
        ),
    ],
}


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{path} does not start with YAML front matter")

    marker = "\n---\n"
    end = text.find(marker, len("---\n"))
    if end == -1:
        raise ValueError(f"{path} has unterminated YAML front matter")

    frontmatter = text[len("---\n") : end]
    body = text[end + len(marker) :].strip()
    metadata: dict[str, str] = {}

    current_key = None
    current_lines: list[str] = []
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            if current_key is not None:
                metadata[current_key] = "\n".join(current_lines).strip()
            key, _, value = line.partition(":")
            current_key = key.strip()
            current_lines = [value.strip()]
        elif current_key is not None:
            current_lines.append(line.strip())

    if current_key is not None:
        metadata[current_key] = "\n".join(current_lines).strip()

    for key, value in list(metadata.items()):
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            metadata[key] = value[1:-1]

    missing = [key for key in FRONTMATTER_KEYS if not metadata.get(key)]
    if missing:
        raise ValueError(f"{path} is missing required front matter: {', '.join(missing)}")

    return metadata, body


def skill_names(skills_dir: Path) -> set[str]:
    names = set()
    for path in skills_dir.glob("*/SKILL.md"):
        metadata, _ = parse_frontmatter(path)
        names.add(metadata["name"])
    return names


def replace_skill_mentions(body: str, names: set[str]) -> str:
    for name in sorted(names, key=len, reverse=True):
        body = re.sub(
            rf"(^|[\s`(\"'>])\/{re.escape(name)}(?=($|[\s`.,):\]]))",
            rf"\1${name}",
            body,
        )
    return body


def normalize_body(name: str, body: str, names: set[str]) -> str:
    for before, after in SPECIAL_REPLACEMENTS.get(name, []):
        body = body.replace(before, after)

    body = replace_skill_mentions(body, names)
    body = body.replace("Invoke $impeccable", "Use `$impeccable`")
    body = body.replace("run $impeccable teach", "use `$impeccable teach`")
    body = body.replace("Run impeccable teach", "Use `$impeccable teach`")
    body = body.replace("STOP and call the AskUserQuestion tool to clarify.", "STOP and ask the user to clarify.")
    body = body.replace("STOP and call the AskUserQuestion tool to clarify.", "STOP and ask the user to clarify.")
    body = body.replace("Then STOP and call the AskUserQuestion tool to clarify whether", "Then STOP and ask the user to clarify whether")
    body = body.replace("Use AskUserQuestion with options", "Ask the user directly with options")
    body = body.replace("AskUserQuestion tool", "direct user question")
    body = body.replace("Then STOP and ask the user to clarify. whether", "Then STOP and ask the user whether")
    body = body.replace("If `CLAUDE.md` contains", "If `AGENTS.md` contains")
    body = body.replace("CLAUDE.md", "AGENTS.md")
    body = body.replace("Claude Code", "Codex")
    body = body.replace("Claude is capable", "Codex is capable")
    body = body.replace("Claude invokes WebSearch", "Codex uses available web search")
    body = body.replace("Claude's built-in WebSearch tool", "available web search")
    body = body.replace("WebSearch", "web search")

    return body


def render_skill(metadata: dict[str, str], body: str) -> str:
    return "\n".join(
        [
            "---",
            f"name: {metadata['name']}",
            f"description: {metadata['description']}",
            "---",
            "",
            body,
            "",
        ]
    )


def relative_symlink_target(source: Path, destination: Path) -> str:
    return os.path.relpath(source, start=destination.parent)


def link_resources(source_dir: Path, destination_dir: Path) -> None:
    for source in source_dir.iterdir():
        if source.name == "SKILL.md":
            continue
        destination = destination_dir / source.name
        if destination.exists() or destination.is_symlink():
            if destination.is_dir() and not destination.is_symlink():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        destination.symlink_to(relative_symlink_target(source, destination))


def generate_skill(source_dir: Path, destination_dir: Path, names: set[str]) -> None:
    metadata, body = parse_frontmatter(source_dir / "SKILL.md")
    normalized_body = normalize_body(metadata["name"], body, names)

    destination_dir.mkdir(parents=True, exist_ok=True)
    for existing in destination_dir.iterdir():
        if existing.is_dir() and not existing.is_symlink():
            shutil.rmtree(existing)
        else:
            existing.unlink()

    (destination_dir / "SKILL.md").write_text(render_skill(metadata, normalized_body))
    link_resources(source_dir, destination_dir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="codex/skills",
        help="Directory for generated Codex skill folders.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate source skills without writing generated output.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    source_root = repo_root / "skills"
    output_root = repo_root / args.output
    source_dirs = sorted(path.parent for path in source_root.glob("*/SKILL.md"))
    names = skill_names(source_root)

    for source_dir in source_dirs:
        parse_frontmatter(source_dir / "SKILL.md")

    if args.check:
        print(f"Validated {len(source_dirs)} source skills")
        return

    output_root.mkdir(parents=True, exist_ok=True)
    generated_dirs = set()
    for source_dir in source_dirs:
        destination_dir = output_root / source_dir.name
        generate_skill(source_dir, destination_dir, names)
        generated_dirs.add(destination_dir)

    for existing in output_root.iterdir():
        if existing not in generated_dirs:
            if existing.is_dir() and not existing.is_symlink():
                shutil.rmtree(existing)
            else:
                existing.unlink()

    print(f"Generated {len(generated_dirs)} Codex skills in {output_root.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
