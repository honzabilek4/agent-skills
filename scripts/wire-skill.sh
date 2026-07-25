#!/usr/bin/env bash
# wire-skill.sh — Symlink a skill from this repo into all agent skill directories.
# Usage:
#   ./scripts/wire-skill.sh <skill-dir>            # Wire one skill
#   ./scripts/wire-skill.sh --all                   # Wire all skills in repo
#   ./scripts/wire-skill.sh --unwire <skill-dir>    # Remove symlinks for one skill
#   ./scripts/wire-skill.sh --unwire --all           # Remove all symlinks
#   ./scripts/wire-skill.sh --list                  # Show what's wired where
#
# Options:
#   --hermes-category <cat>   Category subdirectory for Hermes (default: general)
#   --dry-run                 Show what would be done without doing it

set -uo pipefail  # no -e: we handle errors in wire_skill explicitly

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT"
HERMES_CATEGORY="general"
DRY_RUN=false
ACTION="wire"

# ── Agent definitions ──────────────────────────────────────────────
# Each agent: "name|root_dir|strategy|extra"
#   strategy: file-symlink  → symlink SKILL.md directly
#             dir-symlink    → symlink the whole skill directory
#             dir-file       → create real dir, symlink SKILL.md inside
#   extra: for Hermes — the category subdirectory gets interpolated as {category}
AGENTS=(
  "hermes|$HOME/.hermes/skills/{category}|file-symlink|category"
  "claude|$HOME/.claude/skills|file-symlink|flat-name"   # flat .md file, not dir
  "codex|$HOME/.codex/skills|dir-file|"
  "gemini|$HOME/.gemini/skills|dir-file|"
  "pi|$HOME/.pi/agent/skills|dir-file|"
  "agents-hub|$HOME/.agents/skills|dir-symlink|"
)

# ── Helpers ────────────────────────────────────────────────────────

link_it() {
  local src="$1" dst="$2"
  if $DRY_RUN; then
    echo "  [DRY-RUN] ln -sf $src $dst"
  else
    mkdir -p "$(dirname "$dst")"
    ln -sf "$src" "$dst"
    echo "  → $dst"
  fi
}

remove_link() {
  local path="$1"
  if $DRY_RUN; then
    echo "  [DRY-RUN] rm $path"
  elif [[ -L "$path" ]]; then
    rm "$path"
    echo "  ✕ removed $path"
  elif [[ -f "$path" ]]; then
    echo "  ⚠ $path is a regular file, not a symlink — skipping"
  elif [[ -d "$path" && ! -L "$path" ]]; then
    echo "  ⚠ $path is a real directory, not a symlink — skipping"
  fi
}

wire_skill() {
  local skill_dir="$1"
  # Make absolute
  [[ "$skill_dir" != /* ]] && skill_dir="$SKILLS_DIR/$skill_dir"
  local skill_name
  skill_name="$(basename "$skill_dir")"
  local skill_md="$skill_dir/SKILL.md"

  if [[ ! -f "$skill_md" ]]; then
    echo "⚠ $skill_dir has no SKILL.md — skipping"
    return 1
  fi

  echo "Wiring: $skill_name"

  for def in "${AGENTS[@]}"; do
    IFS='|' read -r agent_name root_dir_tmpl strategy extra <<< "$def"

    # Resolve template variables
    local root_dir="${root_dir_tmpl//\{category\}/$HERMES_CATEGORY}"
    root_dir="${root_dir//\{skill\}/$skill_name}"

    case "$strategy" in
      file-symlink)
        if [[ "$extra" == "flat-name" ]]; then
          # Claude Code: flat .md file
          link_it "$skill_md" "$root_dir/${skill_name}.md"
        else
          # Hermes: directory + SKILL.md
          link_it "$skill_md" "$root_dir/${skill_name}/SKILL.md"
        fi
        ;;
      dir-symlink)
        link_it "$skill_dir" "$root_dir/${skill_name}"
        ;;
      dir-file)
        # Real dir + symlinked SKILL.md (avoids dir-symlink bugs)
        local real_dir="$root_dir/${skill_name}"
        if $DRY_RUN; then
          echo "  [DRY-RUN] mkdir -p $real_dir && ln -sf $skill_md $real_dir/SKILL.md"
        else
          mkdir -p "$real_dir"
          ln -sf "$skill_md" "$real_dir/SKILL.md"
          echo "  → $real_dir/SKILL.md"
        fi
        ;;
    esac
  done
  echo ""
}

unwire_skill() {
  local skill_dir="$1"
  local skill_name
  skill_name="$(basename "$skill_dir")"

  echo "Unwiring: $skill_name"

  for def in "${AGENTS[@]}"; do
    IFS='|' read -r agent_name root_dir_tmpl strategy extra <<< "$def"

    local root_dir="${root_dir_tmpl//\{category\}/$HERMES_CATEGORY}"
    root_dir="${root_dir//\{skill\}/$skill_name}"

    case "$strategy" in
      file-symlink)
        if [[ "$extra" == "flat-name" ]]; then
          remove_link "$root_dir/${skill_name}.md"
        else
          remove_link "$root_dir/${skill_name}/SKILL.md"
        fi
        ;;
      dir-symlink)
        remove_link "$root_dir/${skill_name}"
        ;;
      dir-file)
        remove_link "$root_dir/${skill_name}/SKILL.md"
        # Remove the real directory if empty
        local real_dir="$root_dir/${skill_name}"
        if [[ -d "$real_dir" ]] && [[ -z "$(ls -A "$real_dir" 2>/dev/null)" ]]; then
          if $DRY_RUN; then
            echo "  [DRY-RUN] rmdir $real_dir"
          else
            rmdir "$real_dir" 2>/dev/null || true
          fi
        fi
        ;;
    esac
  done
  echo ""
}

list_skills() {
  echo "Skills in repo:"
  for d in "$SKILLS_DIR"/*/; do
    local name
    name="$(basename "$d")"
    if [[ -f "$d/SKILL.md" ]]; then
      local link_target=""
      [[ -L "$d/SKILL.md" ]] && link_target=" → $(readlink "$d/SKILL.md")"
      echo "  $name$link_target"
    fi
  done
  echo ""

  echo "Agent symlinks:"
  for def in "${AGENTS[@]}"; do
    IFS='|' read -r agent_name root_dir_tmpl strategy extra <<< "$def"
    local root_dir="${root_dir_tmpl//\{category\}/$HERMES_CATEGORY}"
    # Remove trailing {skill} from display path
    local display_dir="${root_dir//\{skill\}/<skill>}"
    echo "  [$agent_name] $display_dir"
    # List symlinked skills for this agent
    local found=0
    for d in "$SKILLS_DIR"/*/; do
      local name
      name="$(basename "$d")"
      [[ ! -f "$d/SKILL.md" ]] && continue

      local target=""
      case "$strategy" in
        file-symlink)
          if [[ "$extra" == "flat-name" ]]; then
            target="${root_dir//\{skill\}/$name}/${name}.md"
          else
            target="${root_dir//\{skill\}/$name}/${name}/SKILL.md"
          fi
          ;;
        dir-symlink)
          target="${root_dir//\{skill\}/$name}/${name}"
          ;;
        dir-file)
          target="${root_dir//\{skill\}/$name}/${name}/SKILL.md"
          ;;
      esac

      if [[ -L "$target" ]]; then
        echo "    $name → $(readlink "$target")"
        found=1
      elif [[ -f "$target" ]]; then
        echo "    $name (regular file, not symlinked)"
        found=1
      fi
    done
    [[ $found -eq 0 ]] && echo "    (none)"
  done
}

# ── Main ───────────────────────────────────────────────────────────

# Parse flags
SKILL_ARG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)              SKILL_ARG="--all" ;;
    --unwire)           ACTION="unwire" ;;
    --list)             ACTION="list" ;;
    --dry-run)          DRY_RUN=true ;;
    --hermes-category)  HERMES_CATEGORY="$2"; shift ;;
    -h|--help)
      echo "Usage: wire-skill.sh [--all | <skill-dir>] [--unwire] [--list] [--dry-run] [--hermes-category <cat>]"
      echo ""
      echo "Wire skills from this repo to all installed AI coding agents."
      echo ""
      echo "  <skill-dir>        Name of the skill directory in this repo"
      echo "  --all              Operate on all skills in the repo"
      echo "  --unwire           Remove symlinks instead of creating them"
      echo "  --list             Show current wiring state"
      echo "  --dry-run          Show what would be done without doing it"
      echo "  --hermes-category  Category for Hermes skill (default: general)"
      exit 0
      ;;
    *) SKILL_ARG="$1" ;;
  esac
  shift
done

cd "$REPO_ROOT"

case "$ACTION" in
  list)
    list_skills
    ;;
  wire)
    if [[ "$SKILL_ARG" == "--all" ]]; then
      for d in */; do
        [[ -d "$d" ]] && wire_skill "${d%/}"
      done
    elif [[ -n "$SKILL_ARG" ]]; then
      if [[ ! -d "$SKILL_ARG" ]]; then
        echo "Error: '$SKILL_ARG' is not a directory in this repo"
        exit 1
      fi
      wire_skill "$SKILL_ARG"
    else
      echo "Error: specify a skill directory or --all"
      exit 1
    fi
    ;;
  unwire)
    if [[ "$SKILL_ARG" == "--all" ]]; then
      for d in */; do
        [[ -d "$d" ]] && unwire_skill "${d%/}"
      done
    elif [[ -n "$SKILL_ARG" ]]; then
      if [[ ! -d "$SKILL_ARG" ]]; then
        echo "Error: '$SKILL_ARG' is not a directory in this repo"
        exit 1
      fi
      unwire_skill "$SKILL_ARG"
    else
      echo "Error: specify a skill directory or --all"
      exit 1
    fi
    ;;
esac
