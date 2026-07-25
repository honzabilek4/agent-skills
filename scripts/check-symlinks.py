#!/usr/bin/env python3
"""Check for broken and recursive symlinks in the repo."""
import os
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
errors = 0

for p in repo.rglob("*"):
    if not p.is_symlink():
        continue
    # Broken?
    if not p.exists():
        print(f"  ❌ Broken: {p.relative_to(repo)} → {os.readlink(p)}")
        errors += 1
    # Recursive?
    target = os.path.realpath(p)
    parent = str(p.parent.resolve())
    if target == parent or str(p.resolve()).startswith(target + os.sep):
        print(f"  ❌ Recursive: {p.relative_to(repo)} → {target}")
        errors += 1

if errors:
    print(f"  ❌ {errors} symlink issue(s)")
    sys.exit(1)
print("  ✅ No broken or recursive symlinks")
