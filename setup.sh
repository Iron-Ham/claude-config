#!/usr/bin/env bash
set -euo pipefail

# Claude Code config setup script
# Symlinks config from this repo into ~/.claude/

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

# Items to symlink: source (relative to repo) -> target (relative to ~/.claude/)
ITEMS=(
  "CLAUDE.md"
  "settings.json"
  "agents"
  "skills"
  "commands"
)

mkdir -p "$CLAUDE_DIR"

for item in "${ITEMS[@]}"; do
  src="$REPO_DIR/$item"
  dest="$CLAUDE_DIR/$item"

  if [ ! -e "$src" ]; then
    echo "SKIP  $item (not in repo)"
    continue
  fi

  # Back up existing non-symlink targets
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    backup="$dest.bak.$(date +%Y%m%d%H%M%S)"
    echo "BACKUP $dest -> $backup"
    mv "$dest" "$backup"
  fi

  # Remove existing symlink if it points somewhere else
  if [ -L "$dest" ]; then
    current="$(readlink "$dest")"
    if [ "$current" = "$src" ]; then
      echo "OK     $item (already linked)"
      continue
    fi
    rm "$dest"
  fi

  ln -s "$src" "$dest"
  echo "LINK   $dest -> $src"
done

echo ""
echo "Done. Your ~/.claude/ config is now symlinked from $REPO_DIR"
