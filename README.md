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
| `agents/` | Specialized agent definitions across engineering, design, sales, product, project management, and more (sourced from [agency-agents](https://github.com/iron-ham/agency-agents)) |
| `skills/` | Third-party skill plugins (impeccable, last30days, deep-review, etc.) |
| `commands/` | Custom slash commands |
| `setup.sh` | Symlink installer |

## Customizing

After making changes, commit and push:

```bash
cd ~/Developer/claude-config
git add -A && git commit -m "chore: describe your change" && git push
```

On a new machine, just clone and re-run `./setup.sh`.
