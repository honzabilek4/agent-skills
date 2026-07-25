# AGENTS.md — agent-skills repo

## When adding or modifying a skill

Always load the `skill-creator` skill first (`skill_view(name='skill-creator')`). It defines the standard:
- SKILL.md with `name` + `description` in YAML frontmatter
- Description must be "pushy" — include trigger contexts ("Use this skill whenever…")
- Name must be kebab-case, directory name must match frontmatter `name`
- Body under 500 lines
- Bundled resources in standard dirs only: `scripts/`, `references/`, `assets/`, `agents/`, `eval-viewer/`, `evals/`
- No recursive/self-referencing symlinks

## After adding or modifying a skill — update README

The README.md Skills table must be kept in sync. If you add a skill, add its row to the table. If you add evals, update the Evals column. The README is the public face of this repo — stale tables break discovery.

## Before committing

```bash
just precommit
```

This runs `validate-all-skills.py` (10 checks per skill) + broken symlink check + recursive symlink check. Must pass clean — 0 errors. Warnings are advisory but fix them.

## After committing — wire to agents

```bash
just wire-all
```

Or for a single skill: `just wire <skill-dir> --hermes-category <cat>`. This symlinks the skill into all agent directories (Hermes, Claude, Codex, Gemini, Pi, OpenCode).

## Evals

To run evals for a skill:
```bash
just eval-list <skill>          # see what's available
just eval-show <skill> <id>     # read one in detail
just eval-prompt <skill> <id>   # generate delegate_task input
```
Then use `delegate_task` with the output of `eval-prompt` to execute the eval.

## No drift

This repo is the canonical source of truth. All edits happen here. Never edit the symlinked copy in `~/.hermes/skills/`, `~/.claude/skills/`, etc. — those are read-only mirrors.
