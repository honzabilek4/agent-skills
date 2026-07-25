#!/usr/bin/env python3
"""Display and manage evals for a skill.

Usage:
  python3 scripts/evals.py list <skill-dir>     # List all evals
  python3 scripts/evals.py show <skill-dir> <id> # Show one eval in detail
  python3 scripts/evals.py run-prompt <skill-dir> <id>  # Output the run prompt for delegate_task
"""
import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent


def load_evals(skill_dir: str) -> dict:
    path = repo / skill_dir / "evals" / "evals.json"
    if not path.exists():
        print(f"No evals found at {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text())


def cmd_list(skill_dir: str):
    data = load_evals(skill_dir)
    print(f"{data['skill_name']} — {len(data['evals'])} eval(s):")
    for e in data["evals"]:
        prompt_preview = e["prompt"][:120].replace("\n", " ")
        print(f"  [{e['id']}] {prompt_preview}…")


def cmd_show(skill_dir: str, eval_id: int):
    data = load_evals(skill_dir)
    for e in data["evals"]:
        if e["id"] == eval_id:
            print(f"## Eval {e['id']}: {data['skill_name']}\n")
            print(f"**Prompt:**\n{e['prompt']}\n")
            print(f"**Expected:**\n{e['expected_output']}\n")
            if e.get("files"):
                print(f"**Files:** {', '.join(e['files'])}")
            return
    print(f"Eval {eval_id} not found", file=sys.stderr)
    sys.exit(1)


def cmd_run_prompt(skill_dir: str, eval_id: int):
    """Output a prompt suitable for delegate_task subagent."""
    data = load_evals(skill_dir)
    skill_path = repo / skill_dir
    for e in data["evals"]:
        if e["id"] == eval_id:
            print(
                f"Execute this task using the skill at {skill_path}:\n\n"
                f"Task: {e['prompt']}\n\n"
                f"Expected behavior: {e['expected_output']}\n\n"
                f"Save any output files and report what you produced."
            )
            return
    print(f"Eval {eval_id} not found", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: evals.py <list|show|run-prompt> <skill-dir> [eval-id]", file=sys.stderr)
        sys.exit(1)

    action, skill_dir = sys.argv[1], sys.argv[2]
    eval_id = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    if action == "list":
        cmd_list(skill_dir)
    elif action == "show" and eval_id:
        cmd_show(skill_dir, eval_id)
    elif action == "run-prompt" and eval_id:
        cmd_run_prompt(skill_dir, eval_id)
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)
