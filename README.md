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

### Add a new skill to all agents

```bash
# 1. Create the skill in this repo
mkdir -p ~/Projects/agent-skills/my-skill
cat > ~/Projects/agent-skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: What this skill does and when to use it
---
# My Skill
...
EOF

# 2. Wire it to the standard hub
ln -s ~/Projects/agent-skills/my-skill ~/.agents/skills/my-skill

# 3. Wire it to Hermes
mkdir -p ~/.hermes/skills/general/my-skill
ln -s ~/Projects/agent-skills/my-skill/SKILL.md ~/.hermes/skills/general/my-skill/SKILL.md

# 4. Wire it to Claude Code
ln -s ~/Projects/agent-skills/my-skill/SKILL.md ~/.claude/skills/my-skill.md

# 5. Wire it to Codex (real dir + file symlink avoids symlink bug)
mkdir -p ~/.codex/skills/my-skill
ln -s ~/Projects/agent-skills/my-skill/SKILL.md ~/.codex/skills/my-skill/SKILL.md

# 6. Wire it to Gemini CLI (real dir + file symlink avoids symlink bug)
mkdir -p ~/.gemini/skills/my-skill
ln -s ~/Projects/agent-skills/my-skill/SKILL.md ~/.gemini/skills/my-skill/SKILL.md

# 7. Wire it to Pi
mkdir -p ~/.pi/agent/skills/my-skill
ln -s ~/Projects/agent-skills/my-skill/SKILL.md ~/.pi/agent/skills/my-skill/SKILL.md

# 8. OpenCode — auto-discovered via ~/.claude/skills/ and ~/.agents/skills/ (no extra step)
```

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
