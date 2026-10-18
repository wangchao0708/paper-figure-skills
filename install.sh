#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./install.sh [--copy] [--only opencode|codex]

Install the paper-figure-spec skill for OpenCode and/or Codex.

  --copy                 Copy files instead of creating a symlink.
  --only opencode|codex  Install only one target.
EOF
}

MODE="symlink"
ONLY="all"
while [ "$#" -gt 0 ]; do
  case "$1" in
    --copy)
      MODE="copy"
      shift
      ;;
    --only)
      if [ "$#" -lt 2 ]; then
        echo "install.sh: --only requires opencode or codex" >&2
        exit 2
      fi
      ONLY="$2"
      shift 2
      ;;
    --only=*)
      ONLY="${1#*=}"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "install.sh: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$ONLY" in
  all|opencode|codex) ;;
  *)
    echo "install.sh: --only must be opencode, codex, or all" >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$SCRIPT_DIR"
SOURCE="$REPO_ROOT/skills/paper-figure-spec"
SOURCE_REAL="$(cd "$SOURCE" 2>/dev/null && pwd -P)" || {
  echo "install.sh: skill source not found: $SOURCE" >&2
  exit 1
}
if [ ! -f "$SOURCE_REAL/SKILL.md" ]; then
  echo "install.sh: SKILL.md not found in $SOURCE_REAL" >&2
  exit 1
fi

if [ "$MODE" = "copy" ] && ! command -v rsync >/dev/null 2>&1; then
  echo "install.sh: rsync is required for --copy" >&2
  exit 1
fi

OPENCODE_SKILLS_DIR="${OPENCODE_SKILLS_DIR:-$HOME/.config/opencode/skills}"
CODEX_SKILLS_DIR="${CODEX_SKILLS_DIR:-$HOME/.codex/skills}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
MARKER=".figspec-source"

is_our_link() {
  local target="$1"
  [ -L "$target" ] || return 1
  [ "$(cd "$target" 2>/dev/null && pwd -P)" = "$SOURCE_REAL" ]
}

is_our_copy() {
  local target="$1"
  [ -d "$target" ] && [ ! -L "$target" ] || return 1
  [ -f "$target/$MARKER" ] || return 1
  [ "$(cat "$target/$MARKER" 2>/dev/null)" = "$REPO_ROOT" ]
}

backup_target() {
  local target="$1"
  local backup="${target}.bak-${TIMESTAMP}"
  if [ -e "$backup" ] || [ -L "$backup" ]; then
    backup="${backup}-$$"
  fi
  mv "$target" "$backup"
  echo "backed up: $target -> $backup"
}

install_target() {
  local target="$1"
  local parent
  parent="$(dirname "$target")"
  mkdir -p "$parent"

  if is_our_link "$target"; then
    if [ "$MODE" = "symlink" ]; then
      echo "unchanged (symlink): $target"
      return
    fi
    rm -f "$target"
  elif is_our_copy "$target"; then
    if [ "$MODE" = "copy" ]; then
      rsync -a --delete --exclude='.DS_Store' "$SOURCE_REAL/" "$target/"
      printf '%s\n' "$REPO_ROOT" > "$target/$MARKER"
      echo "updated (copy): $target"
      return
    fi
    rm -rf "$target"
  elif [ -e "$target" ] || [ -L "$target" ]; then
    backup_target "$target"
  fi

  if [ "$MODE" = "symlink" ]; then
    ln -sfn "$SOURCE_REAL" "$target"
    echo "installed (symlink): $target -> $SOURCE_REAL"
  else
    mkdir -p "$target"
    rsync -a --delete --exclude='.DS_Store' "$SOURCE_REAL/" "$target/"
    printf '%s\n' "$REPO_ROOT" > "$target/$MARKER"
    echo "installed (copy): $target"
  fi
}

if [ "$ONLY" = "all" ] || [ "$ONLY" = "opencode" ]; then
  install_target "$OPENCODE_SKILLS_DIR/paper-figure-spec"
fi
if [ "$ONLY" = "all" ] || [ "$ONLY" = "codex" ]; then
  install_target "$CODEX_SKILLS_DIR/paper-figure-spec"
fi

echo
echo "Next steps:"
echo "  pip install -e \"$REPO_ROOT\""
echo "  restart OpenCode and/or Codex"
if [ "$MODE" = "copy" ]; then
  echo "  (copy install: rerun ./install.sh --copy after git pull)"
fi
