# Agent Skills — Canonical Source

Shared skills repository following the [Agent Skills open standard](https://agentskills.io). One source of truth, consumed by multiple AI coding agents via symlinks.

## Format

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter:

```
skill-name/
├── SKILL.md          # Required: name + description in frontmatter, then markdown instructions
├── scripts/          # Optional: executable scripts the agent can run
├── references/       # Optional: reference docs loaded on demand
└── assets/           # Optional: templates, images, etc.
```

## Skills

| Skill | Description |
|-------|-------------|
| [software-design-principles](software-design-principles/SKILL.md) | Design principles & red flags (Ousterhout's "A Philosophy of Software Design") |

## Architecture

```
~/Projects/agent-skills/          ← THIS REPO (source of truth)
├── software-design-principles/
│   └── SKILL.md                  ← canonical file

~/.agents/skills/                 ← Agent Skills standard hub (global tier)
├── software-design-principles/ → ../../Projects/agent-skills/software-design-principles/

~/.hermes/skills/software-development/software-design-principles/
├── SKILL.md → ../../../../Projects/agent-skills/software-design-principles/SKILL.md

~/.claude/skills/
├── software-design-principles.md → ../../Projects/agent-skills/software-design-principles/SKILL.md

~/.codex/skills/
├── software-design-principles/
│   └── SKILL.md → ../../../Projects/agent-skills/software-design-principles/SKILL.md

~/.gemini/skills/
├── software-design-principles/
│   └── SKILL.md → ../../../Projects/agent-skills/software-design-principles/SKILL.md
```

## Per-Agent Setup

## Adding a New Skill

```bash
# 1. Create the skill directory
mkdir -p ~/Projects/agent-skills/my-skill
cat > ~/Projects/agent-skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: What this skill does and when to use it
---
# My Skill
...
EOF

# 2. Wire it to all agents
cd ~/Projects/agent-skills
./scripts/wire-skill.sh my-skill --hermes-category general

# 3. Commit
git add my-skill/ && git commit -m "Add my-skill"
```

Or use `./scripts/wire-skill.sh --all --hermes-category <cat>` to re-wire everything.

See `./scripts/wire-skill.sh --help` for all options (`--list`, `--unwire`, `--dry-run`).

### Agent Discovery Paths Reference

| Agent | Path | Symlink Strategy |
|-------|------|-----------------|
| **Hermes** | `~/.hermes/skills/<cat>/<name>/SKILL.md` | File symlink |
| **Claude Code** | `~/.claude/skills/<name>.md` | File symlink |
| **Codex** | `~/.codex/skills/<name>/SKILL.md` | Real dir + file symlink |
| **Gemini CLI** | `~/.gemini/skills/<name>/SKILL.md` | Real dir + file symlink |
| **Pi** | `~/.pi/agent/skills/<name>/SKILL.md` | Real dir + file symlink |
| **OpenCode** | `~/.claude/skills/` or `~/.agents/skills/` | Auto-covered |
| **Standard hub** | `~/.agents/skills/<name>/` | Directory symlink |

### Known Limitations

- **Codex CLI**: [Doesn't follow symlinked `.agents/skills/` directories](https://github.com/openai/codex/issues/11314). Workaround: use `~/.codex/skills/` with a real directory + symlinked `SKILL.md` inside.
- **Gemini CLI**: [Doesn't follow symlinked skill directories](https://github.com/google-gemini/gemini-cli/issues/16247). Workaround: use `~/.gemini/skills/` with a real directory + symlinked `SKILL.md` inside.

## Adding a New Consumer Agent

1. Find the agent's skill discovery path (check their docs or `agentskills.io`)
2. Create the appropriate symlink following the pattern above
3. If they have a directory-symlink bug, use the "real dir + file symlink" pattern
4. Add to the table in this README
5. Commit

## Why Not Just Copy?

Symlinks mean a single edit propagates instantly to all agents. No sync scripts, no stale copies, no drift.
