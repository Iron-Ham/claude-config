# Agent Config

Personal agent configuration for Claude Code and Codex: global instructions, skills, upstream-derived agent declarations, and setup scripts.

## Quick Start

For Claude Code:

```bash
git clone git@github.com:Iron-Ham/claude-config.git ~/Developer/claude-config
cd ~/Developer/claude-config
./setup.sh
```

For Codex:

```bash
git clone git@github.com:Iron-Ham/claude-config.git ~/Developer/claude-config
cd ~/Developer/claude-config
./setup-codex.sh
```

`setup.sh` symlinks Claude Code config into `~/.claude/`. `setup-codex.sh` symlinks `AGENTS.md`, generated Codex custom agents, and generated Codex-normalized skills into Codex's expected locations while leaving `~/.codex/config.toml` untouched. Existing non-symlink files are backed up with a `.bak.*` suffix before being replaced.

## Recommended: Max Effort Alias

By default, Claude Code runs at a moderate effort level. For consistently thorough responses, add this alias to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
alias claude='claude --effort max'
```

This ensures every invocation uses the highest effort level without needing to remember the flag each time.

## What's Included

| Path | Description |
|---|---|
| `AGENTS.md` | Canonical global instructions -- git workflow, commit conventions, agent delegation strategy, testing and documentation guidelines |
| `CLAUDE.md` | Symlink to `AGENTS.md` for Claude Code compatibility |
| `settings.json` | Claude Code model preferences, enabled plugins, and effort level defaults |
| `agents/` | Specialized agent definitions across engineering, design, sales, product, project management, and more (snapshotted from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) -- see [Syncing agents](#syncing-agents) below) |
| `codex/agents/` | Codex custom-agent TOML generated from the curated Markdown agent subset |
| `skills/` | Source skills, including Claude Code-compatible metadata and resources |
| `codex/skills/` | Codex-normalized skills generated from `skills/` |
| `commands/` | Custom slash commands |
| `scripts/generate-codex-agents.py` | Regenerates `codex/agents/*.toml` from `agents/**/*.md` |
| `scripts/generate-codex-skills.py` | Regenerates `codex/skills/*/SKILL.md` from `skills/*/SKILL.md` |
| `setup.sh` | Claude Code symlink installer |
| `setup-codex.sh` | Codex symlink installer |

## Codex agents

Codex custom agents are generated from a curated subset of the upstream-style Markdown agents:

```bash
python scripts/generate-codex-agents.py
```

To experiment with a full conversion of every top-level Markdown agent that has front matter:

```bash
python scripts/generate-codex-agents.py --all
```

Review the generated files before installing. The default checked-in set is intentionally smaller than the full upstream snapshot to keep Codex agent routing predictable.

## Codex skills

Codex reads skills from directories containing a `SKILL.md` with `name` and `description` front matter. Generate Codex-normalized copies from the source skills with:

```bash
python scripts/generate-codex-skills.py
```

To validate the source skill front matter without writing generated files:

```bash
python scripts/generate-codex-skills.py --check
```

Generated skill folders keep only Codex-relevant front matter and symlink resource folders/files back to `skills/`, so large assets and helper scripts are not duplicated.

## Syncing agents

The `agents/` directory is a plain snapshot of [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) -- no submodule, no subtree. To pull in upstream updates:

```bash
# 1. Clone upstream to a throwaway location
TMP=$(mktemp -d)
git clone --depth 1 https://github.com/msitarzewski/agency-agents.git "$TMP/agency-agents"

# 2. Mirror its contents into agents/, removing files upstream has deleted
rsync -a --delete --exclude='.git' "$TMP/agency-agents/" agents/

# 3. Review, commit, and reference the upstream commit in the message
cd ~/Developer/claude-config
git status
UPSTREAM_SHA=$(git -C "$TMP/agency-agents" rev-parse --short HEAD)
git checkout -b Iron-Ham/sync-agency-agents-"$UPSTREAM_SHA"
git add agents/
git commit -m "chore: sync agents from msitarzewski/agency-agents@$UPSTREAM_SHA"
rm -rf "$TMP"
```

Notes:
- The `--delete` flag is intentional -- it prunes local files the upstream removed so the snapshot stays faithful.
- Nested `.github/` and `.gitignore` inside `agents/` are mirrored from upstream. The nested `.github/` is inert (GitHub only reads the repo-root one) and the nested `.gitignore` only scopes generated artifacts under `agents/integrations/*` that this repo doesn't produce.

## Customizing

After making changes, commit and push:

```bash
cd ~/Developer/claude-config
git add -A && git commit -m "chore: describe your change" && git push
```

On a new machine, just clone and re-run `./setup.sh`.
For Codex setup, run `./setup-codex.sh` as well.
