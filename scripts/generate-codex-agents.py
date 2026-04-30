#!/usr/bin/env python3
"""Generate Codex custom-agent TOML files from agency-agent Markdown files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_AGENT_SOURCES = [
    "agents/engineering/engineering-code-reviewer.md",
    "agents/engineering/engineering-frontend-developer.md",
    "agents/engineering/engineering-backend-architect.md",
    "agents/engineering/engineering-software-architect.md",
    "agents/engineering/engineering-security-engineer.md",
    "agents/engineering/engineering-database-optimizer.md",
    "agents/engineering/engineering-technical-writer.md",
    "agents/engineering/engineering-git-workflow-master.md",
    "agents/testing/testing-accessibility-auditor.md",
    "agents/testing/testing-evidence-collector.md",
]


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

    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            continue
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        metadata[key.strip()] = value

    return metadata, body


def codex_name(display_name: str) -> str:
    name = display_name.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return re.sub(r"_+", "_", name).strip("_")


def toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def source_name(source: Path, repo_root: Path) -> str:
    relative_source = source.relative_to(repo_root / "agents").with_suffix("")
    return codex_name("_".join(relative_source.parts))


def render_agent(source: Path, repo_root: Path, name: str) -> str:
    metadata, body = parse_frontmatter(source)
    display_name = metadata["name"]
    description = metadata["description"]
    vibe = metadata.get("vibe")

    instructions = body
    if vibe:
        instructions = f"{instructions}\n\n## Operating Style\n\n{vibe}"

    relative_source = source.relative_to(repo_root)
    rendered = "\n".join(
        [
            f"# Generated from {relative_source}.",
            f'name = {toml_string(name)}',
            f'description = {toml_string(description)}',
            'model_reasoning_effort = "high"',
            "",
            f"developer_instructions = {toml_string(instructions)}",
            "",
        ]
    )
    return rendered


def source_paths(repo_root: Path, include_all: bool) -> list[Path]:
    if include_all:
        return sorted(
            path
            for path in (repo_root / "agents").glob("*/*.md")
            if path.read_text().startswith("---\n")
        )
    return [repo_root / source for source in DEFAULT_AGENT_SOURCES]


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--all",
        action="store_true",
        help="Convert every top-level Markdown agent with front matter.",
    )
    parser.add_argument(
        "--output",
        default="codex/agents",
        help="Directory for generated Codex agent TOML files.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    output_dir = repo_root / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    generated: set[Path] = set()
    seen_names: dict[str, Path] = {}

    for source in source_paths(repo_root, args.all):
        metadata, _ = parse_frontmatter(source)
        name = codex_name(metadata["name"])
        if name in seen_names:
            name = source_name(source, repo_root)
        if name in seen_names:
            raise ValueError(f"duplicate Codex agent name {name!r}: {seen_names[name]} and {source}")
        seen_names[name] = source

        rendered = render_agent(source, repo_root, name)
        destination = output_dir / f"{name}.toml"
        destination.write_text(rendered)
        generated.add(destination)

    for existing in output_dir.glob("*.toml"):
        if existing not in generated:
            existing.unlink()

    print(f"Generated {len(generated)} Codex agents in {display_path(output_dir, repo_root)}")


if __name__ == "__main__":
    main()
