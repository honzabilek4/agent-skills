# AGENTS.md — agent-skills repo

## When adding or modifying a skill

Always load the `skill-creator` skill first (`skill_view(name='skill-creator')`). It defines the standard:
- SKILL.md with `name` + `description` in YAML frontmatter
- Description must be "pushy" — include trigger contexts ("Use this skill whenever…")
- Name must be kebab-case, directory name must match frontmatter `name`
- Body under 500 lines
- Bundled resources in standard dirs only: `scripts/`, `references/`, `assets/`, `agents/`, `eval-viewer/`
- No recursive/self-referencing symlinks

## Before committing

```bash
python3 scripts/validate-all-skills.py
```

Must pass clean — 0 errors. Warnings are advisory but fix them.

## After adding a skill

```bash
./scripts/wire-skill.sh <skill-dir> --hermes-category <cat>
```

This symlinks the skill into all agent directories (Hermes, Claude, Codex, Gemini, Pi, OpenCode).

## No drift

This repo is the canonical source of truth. All edits happen here. Never edit the symlinked copy in `~/.hermes/skills/`, `~/.claude/skills/`, etc. — those are read-only mirrors.
