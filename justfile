# agent-skills repo — self-documenting commands via just
# Run `just` to see all available commands.

default:
    @just --list

# ── Validation ───────────────────────────────────────────────────────

# Validate all skills against the skill-creator standard
validate:
    python3 scripts/validate-all-skills.py

# Validate with machine-readable JSON output (for CI)
validate-json:
    python3 scripts/validate-all-skills.py --json

# ── Wiring ───────────────────────────────────────────────────────────

# Wire all skills to all installed agents (Hermes, Claude, Codex, Gemini, Pi)
wire-all:
    ./scripts/wire-skill.sh --all

# Wire a single skill (usage: just wire <skill-dir>)
wire skill:
    ./scripts/wire-skill.sh {{skill}}

# Wire with Hermes category (usage: just wire-cat <skill-dir> <cat>)
wire-cat skill cat:
    ./scripts/wire-skill.sh {{skill}} --hermes-category {{cat}}

# Unwire all skills from all agents
unwire-all:
    ./scripts/wire-skill.sh --unwire --all

# Unwire a single skill (usage: just unwire <skill-dir>)
unwire skill:
    ./scripts/wire-skill.sh --unwire {{skill}}

# List current wiring state
list:
    ./scripts/wire-skill.sh --list

# Dry-run: show what wiring would do without touching anything
wire-dry:
    ./scripts/wire-skill.sh --all --dry-run

# ── Pre-commit check ─────────────────────────────────────────────────

# Run before committing: validate + verify no broken symlinks
precommit: validate
    @echo "Checking for broken symlinks..."
    @! find . -type l ! -exec test -e {} \; -print | grep . && echo "  ✅ No broken symlinks" || { echo "  ❌ Broken symlinks found above"; exit 1; }
    @echo "Checking for recursive symlinks..."
    python3 scripts/check-symlinks.py
    @echo "✅ Pre-commit checks pass"

# ── Git ──────────────────────────────────────────────────────────────

# Show repo status
status:
    git status --short

# Commit with pre-commit checks (usage: just commit "message")
commit msg: precommit
    git add -A
    git diff --cached --stat
    git commit -m "{{msg}}"
