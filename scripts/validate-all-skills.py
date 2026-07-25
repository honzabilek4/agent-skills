#!/usr/bin/env python3
"""
Validate all skills in the repo against the skill-creator standard.

Usage:
  python scripts/validate-all-skills.py [--repo-root /path/to/repo]
  python scripts/validate-all-skills.py --json          # machine-readable output

Checks (per skill):
  1. SKILL.md exists with valid YAML frontmatter (name, description required)
  2. Directory name matches frontmatter `name`
  3. Name is kebab-case, ≤64 chars
  4. Description includes trigger contexts ("when to use" language)
  5. SKILL.md body non-empty, under 500 lines
  6. Bundled resources use standard directory names only
  7. No recursive / self-referencing symlinks
  8. Referenced bundled paths in SKILL.md actually exist
  9. No illegal files (.DS_Store, __pycache__, etc.)
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML required — pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# ── Constants ──────────────────────────────────────────────────────────
STANDARD_DIRS = {"scripts", "references", "assets", "agents", "eval-viewer", "evals"}
SKILL_REQUIRED_FILES = {"SKILL.md"}
MAX_DESCRIPTION_CHARS = 1024
MAX_NAME_CHARS = 64
MAX_BODY_LINES = 500
TRIGGER_PATTERNS = [
    r"use\s+(this\s+skill\s+)?(when|whenever|if|for)",
    r"apply\s+(this\s+skill\s+)?(when|whenever|for|to)",
    r"trigger\b",
    r"(suitable|appropriate|useful)\s+for",
    r"load\s+(this\s+skill\s+)?(when|for)",
]


# ── Helpers ────────────────────────────────────────────────────────────
def kebab_case(s: str) -> bool:
    return bool(re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", s))


def has_trigger_language(desc: str) -> bool:
    """Check if description includes trigger context (pushy per skill-creator spec)."""
    desc_lower = desc.lower()
    return any(re.search(p, desc_lower) for p in TRIGGER_PATTERNS)


def is_recursive_symlink(path: Path) -> bool:
    """Check if a symlink points to an ancestor or itself."""
    if not path.is_symlink():
        return False
    target = path.resolve()
    return target == path.parent.resolve() or str(path.resolve()).startswith(
        str(target) + os.sep
    )


def extract_frontmatter(content: str):
    """Return (frontmatter_dict, body_text) or raise."""
    if not content.startswith("---"):
        raise ValueError("No YAML frontmatter — must start with '---'")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
    if not match:
        raise ValueError("Invalid frontmatter format — unclosed '---'")
    fm_text, body = match.group(1), match.group(2)
    fm = yaml.safe_load(fm_text)
    if not isinstance(fm, dict):
        raise ValueError("Frontmatter must be a YAML dictionary")
    return fm, body


# ── Validation ─────────────────────────────────────────────────────────
def validate_skill(skill_dir: Path) -> list[dict]:
    """
    Validate one skill directory. Returns a list of issue dicts.
    Empty list = clean.
    """
    issues: list[dict] = []
    skill_name = skill_dir.name

    def issue(level: str, msg: str):
        issues.append({"skill": skill_name, "level": level, "message": msg})

    # ── 1. SKILL.md exists ──
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        issue("error", "Missing SKILL.md")
        return issues  # can't continue

    # ── 2. Frontmatter ──
    content = skill_md.read_text()
    try:
        fm, body = extract_frontmatter(content)
    except ValueError as e:
        issue("error", str(e))
        return issues

    name = fm.get("name", "")
    description = fm.get("description", "")

    if not name:
        issue("error", "Missing 'name' in frontmatter")
    if not description:
        issue("error", "Missing 'description' in frontmatter")

    # ── 3. Directory name matches frontmatter name ──
    if name and name != skill_name:
        issue("warning", f"Directory name '{skill_name}' ≠ frontmatter name '{name}'")

    # ── 4. Name kebab-case ──
    if name and not kebab_case(str(name)):
        issue("error", f"Name '{name}' is not kebab-case")
    if name and len(str(name)) > MAX_NAME_CHARS:
        issue("error", f"Name '{name}' exceeds {MAX_NAME_CHARS} chars")

    # ── 5. Description quality ──
    if description:
        desc = str(description)
        if len(desc) > MAX_DESCRIPTION_CHARS:
            issue("error", f"Description exceeds {MAX_DESCRIPTION_CHARS} chars")
        if "<" in desc or ">" in desc:
            issue("error", "Description contains angle brackets")
        if not has_trigger_language(desc):
            issue(
                "warning",
                "Description lacks trigger context — add 'use when', "
                "'apply whenever', etc. (skill-creator spec: descriptions "
                "must be 'pushy' with trigger contexts)",
            )

    # ── 6. Body ──
    if not body.strip():
        issue("warning", "SKILL.md body is empty after frontmatter")
    body_lines = body.count("\n") + 1
    if body_lines > MAX_BODY_LINES:
        issue("warning", f"SKILL.md body is {body_lines} lines (ideal: ≤{MAX_BODY_LINES})")

    # ── 7. Standard directories only ──
    for entry in skill_dir.iterdir():
        if entry.name.startswith("."):
            continue
        if entry.is_dir() and entry.name not in STANDARD_DIRS:
            issue(
                "warning",
                f"Non-standard directory: '{entry.name}/' — "
                f"allowed: {', '.join(sorted(STANDARD_DIRS))}",
            )
        # Check for illegal files
        if entry.is_file() and entry.name not in {"SKILL.md", "LICENSE.txt", "LICENSE", ".gitkeep"}:
            issue(
                "warning",
                f"Unexpected file at skill root: '{entry.name}' — "
                "only SKILL.md (+ optional LICENSE) expected at top level",
            )

    # ── 8. No recursive symlinks ──
    for entry in skill_dir.rglob("*"):
        if is_recursive_symlink(entry):
            issue("error", f"Recursive/self-referencing symlink: {entry}")

    # ── 9. Illegal files anywhere in skill tree ──
    for illegal in skill_dir.rglob(".DS_Store"):
        issue("error", f"Illegal file tracked: {illegal}")
    for illegal in skill_dir.rglob("__pycache__"):
        issue("error", f"Illegal file tracked: {illegal}")

    # ── 10. Referenced bundled paths exist ──
    # Check if SKILL.md references scripts/assets/references that don't exist
    for ref_pattern, dir_name in [
        (r"`(scripts/[\w./-]+)`", "scripts"),
        (r"`(assets/[\w./-]+)`", "assets"),
        (r"`(references/[\w./-]+)`", "references"),
    ]:
        for match in re.finditer(ref_pattern, content):
            ref_path = match.group(1)
            full_path = skill_dir / ref_path
            if not full_path.exists():
                issue("error", f"SKILL.md references missing file: {ref_path}")

    return issues


def find_skills(repo_root: Path) -> list[Path]:
    """Find all skill directories (containing SKILL.md) in the repo."""
    skills = []
    for skill_md in repo_root.rglob("SKILL.md"):
        skill_dir = skill_md.parent
        # Skip symlinks (prevents recursive self-symlink ghost skills)
        if skill_dir.is_symlink():
            continue
        # Skip nested (e.g. inside another skill's bundled dirs)
        if any(d in skill_dir.parts for d in STANDARD_DIRS):
            continue
        # Skip repo-root itself and repo-level scripts/
        if skill_dir == repo_root or skill_dir == repo_root / "scripts":
            continue
        skills.append(skill_dir)
    return sorted(skills)


# ── Main ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Validate all skills in the repo")
    parser.add_argument("--repo-root", default=None, help="Path to repo root (default: auto-detect)")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    args = parser.parse_args()

    if args.repo_root:
        repo_root = Path(args.repo_root).resolve()
    else:
        # Auto-detect: find the closest git root
        repo_root = Path(__file__).resolve().parent.parent

    if not repo_root.is_dir():
        print(f"ERROR: {repo_root} is not a directory", file=sys.stderr)
        sys.exit(1)

    skills = find_skills(repo_root)

    if not skills:
        print("No skills found (no SKILL.md files detected).", file=sys.stderr)
        sys.exit(1)

    all_issues: list[dict] = []
    errors = warnings = 0

    for skill_dir in skills:
        issues = validate_skill(skill_dir)
        all_issues.extend(issues)
        for i in issues:
            if i["level"] == "error":
                errors += 1
            else:
                warnings += 1

    if args.json:
        print(json.dumps({"skills": len(skills), "errors": errors, "warnings": warnings, "issues": all_issues}, indent=2))
    else:
        rel_root = str(repo_root)
        for issue in all_issues:
            level = issue["level"].upper()
            print(f"[{level}] {issue['skill']}: {issue['message']}")

        total = errors + warnings
        if total == 0:
            print(f"\n✅ All {len(skills)} skills pass validation.")
        else:
            print(f"\n{len(skills)} skills checked — {errors} error(s), {warnings} warning(s).")
            if errors:
                print("❌ Validation FAILED.")
            else:
                print("⚠️  Validation passed with warnings.")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
