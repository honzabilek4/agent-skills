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

# ── Evals ────────────────────────────────────────────────────────────

# List all evals for a skill (usage: just eval-list <skill>)
eval-list skill:
    python3 scripts/evals.py list {{skill}}

# Show details of one eval (usage: just eval-show <skill> <id>)
eval-show skill id:
    python3 scripts/evals.py show {{skill}} {{id}}

# Generate a delegate_task prompt for one eval (usage: just eval-prompt <skill> <id>)
eval-prompt skill id:
    python3 scripts/evals.py run-prompt {{skill}} {{id}}

# Run all evals for a skill via delegate_task subagents
# Usage: just eval-run <skill>
# (This requires an agent session — it prints instructions for the agent)
eval-run skill:
    @echo "To run evals for '{{skill}}', the agent in this session should:"
    @echo ""
    python3 scripts/evals.py list {{skill}}
    @echo ""
    @echo "For each eval above, use delegate_task with the prompt from 'just eval-prompt {{skill}} <id>'"
    @echo "Review results qualitatively against expected_output in evals/evals.json"

# Launch eval viewer for a skill's workspace (usage: just eval-view <skill>)
eval-view skill:
    python3.12 skill-creator/eval-viewer/generate_review.py {{skill}}-workspace/iteration-1 --skill-name {{skill}} --static /tmp/{{skill}}-eval-viewer.html
    @echo ""
    @echo "Viewer written to /tmp/{{skill}}-eval-viewer.html"
    @open /tmp/{{skill}}-eval-viewer.html
