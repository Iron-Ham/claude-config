# Claude Code Config

Personal [Claude Code](https://docs.anthropic.com/en/docs/claude-code) configuration -- agents, skills, settings, and workflow conventions. Clone this repo and run the setup script to symlink everything into `~/.claude/`.

## Quick Start

```bash
git clone git@github.com:Iron-Ham/claude-config.git ~/Developer/claude-config
cd ~/Developer/claude-config
./setup.sh
```

The setup script symlinks `CLAUDE.md`, `settings.json`, `agents/`, `skills/`, and `commands/` into `~/.claude/`. Existing files are backed up with a `.bak.*` suffix before being replaced.

## Recommended: Max Effort Alias

By default, Claude Code runs at a moderate effort level. For consistently thorough responses, add this alias to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
alias claude='claude --effort max'
```

This ensures every invocation uses the highest effort level without needing to remember the flag each time.

## What's Included

| Path | Description |
|---|---|
| `CLAUDE.md` | Global instructions -- git workflow, commit conventions, agent delegation strategy, testing and documentation guidelines |
| `settings.json` | Model preferences, enabled plugins, and effort level defaults |
| `agents/` | Specialized agent definitions across engineering, design, sales, product, project management, and more (snapshotted from [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) -- see [Syncing agents](#syncing-agents) below) |
| `skills/` | Third-party skill plugins (impeccable, last30days, deep-review, etc.) |
| `commands/` | Custom slash commands |
| `setup.sh` | Symlink installer |

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
