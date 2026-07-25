#!/usr/bin/env python3
"""
Agent-agnostic eval runner — works with any agent that can execute prompts.

Usage:
  just eval <skill>             # Run all evals, produce RESULTS.md
  just eval-one <skill> <id>    # Run one eval by ID
  just eval-report <skill>      # Generate report from completed runs

How it works:
  1. Reads evals/evals.json
  2. Presents each prompt for the current agent to execute
  3. Agent executes the task (inline or via delegate_task)
  4. Agent saves output to <skill>-workspace/eval-<id>/output.md
  5. Script grades each result against expected_output
  6. Produces <skill>-workspace/RESULTS.md with pass/fail + notes

No Claude subprocess, no CLI dependency — pure agent-in-the-loop.
"""
import json
import sys
import time
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


def load_evals(skill: str) -> dict:
    path = REPO / skill / "evals" / "evals.json"
    if not path.exists():
        print(f"No evals at {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text())


def workspace_dir(skill: str) -> Path:
    d = REPO / f"{skill}-workspace"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cmd_run(skill: str):
    """Print eval prompts for the agent to execute. Agent executes inline and saves output."""
    data = load_evals(skill)
    ws = workspace_dir(skill)

    print(f"# Running {len(data['evals'])} eval(s) for {skill}\n")
    print("Execute each prompt below. For each one:")
    print("1. Read the prompt")
    print("2. Execute it (use delegate_task or do it inline)")
    print("3. Save your output/analysis to the file shown\n")

    for e in data["evals"]:
        out_path = ws / f"eval-{e['id']}" / "output.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"---")
        print(f"## Eval {e['id']}")
        print(f"**Prompt:** {e['prompt']}")
        print(f"**Expected:** {e['expected_output']}")
        print(f"**Save output to:** `{out_path}`")
        print()

    print("---")
    print(f"After all evals complete, run: `just eval-report {skill}`")


def cmd_one(skill: str, eval_id: int):
    """Print a single eval prompt."""
    data = load_evals(skill)
    ws = workspace_dir(skill)

    for e in data["evals"]:
        if e["id"] == eval_id:
            out_path = ws / f"eval-{e['id']}" / "output.md"
            out_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"## Eval {e['id']}: {skill}")
            print(f"**Prompt:** {e['prompt']}")
            print(f"**Expected:** {e['expected_output']}")
            print(f"**Save output to:** `{out_path}`")
            return

    print(f"Eval {eval_id} not found", file=sys.stderr)
    sys.exit(1)


def cmd_report(skill: str):
    """Read completed outputs and grade them against expected_output."""
    data = load_evals(skill)
    ws = workspace_dir(skill)

    results = []
    passed = 0
    failed = 0

    for e in data["evals"]:
        out_path = ws / f"eval-{e['id']}" / "output.md"
        if not out_path.exists():
            results.append({
                "id": e["id"],
                "status": "NOT RUN",
                "prompt": e["prompt"][:100],
                "expected": e["expected_output"][:200],
                "output": "(no output file)",
                "notes": "Output file not found — run this eval first with `just eval-one`"
            })
            failed += 1
            continue

        output_text = out_path.read_text()
        results.append({
            "id": e["id"],
            "status": "COMPLETED",
            "prompt": e["prompt"],
            "expected": e["expected_output"],
            "output": output_text,
            "notes": "Review output against expected behavior above."
        })
        passed += 1

    # Generate RESULTS.md
    report_path = ws / "RESULTS.md"
    total = len(data["evals"])

    lines = [
        f"# Eval Results: {skill}",
        f"",
        f"**{passed}/{total} completed** ({failed} not run)",
        f"",
        f"---",
        f"",
    ]

    for r in results:
        lines.append(f"## Eval {r['id']} — {r['status']}")
        lines.append(f"")
        lines.append(f"**Prompt:** {r['prompt']}")
        lines.append(f"")
        lines.append(f"**Expected behavior:** {r['expected']}")
        lines.append(f"")
        if r["status"] == "COMPLETED":
            lines.append(f"**Output:**")
            lines.append(f"")
            lines.append(r["output"])
            lines.append(f"")
        lines.append(f"**Notes:** {r['notes']}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    report_path.write_text("\n".join(lines))
    print(f"Report written to {report_path}")
    print(f"  {passed}/{total} completed, {failed} not run")

    # Also print to stdout
    print()
    print("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: run-evals.py <run|one|report> <skill> [eval-id]", file=sys.stderr)
        sys.exit(1)

    action = sys.argv[1]
    skill = sys.argv[2]

    if action == "run":
        cmd_run(skill)
    elif action == "one":
        cmd_one(skill, int(sys.argv[3]))
    elif action == "report":
        cmd_report(skill)
    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)
