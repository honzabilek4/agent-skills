# Agent Skills

Canonical source for agent skills, principles, and rules — consumed by multiple AI coding agents via symlinks.

## Pattern

Each skill lives here as a single Markdown file with optional YAML frontmatter. Individual agents symlink their skill/rule files to these canonical sources:

```
~/.hermes/skills/<category>/<skill>/SKILL.md  →  ~/Projects/agent-skills/<category>/<skill>.md
~/.claude/skills/<skill>.md                    →  ~/Projects/agent-skills/<category>/<skill>.md
# etc.
```

One source of truth, many consumers. Edit here, all agents pick it up.

## Skills

| Skill | Category | Consumers |
|-------|----------|-----------|
| [software-design/principles.md](software-design/principles.md) | software-design | Hermes, Claude Code |
