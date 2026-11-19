#!/usr/bin/env python3
"""Copy the public hub experiment onto this repository, then fix standalone paths.

Usage:
    python scripts/sync_from_hub.py /path/to/experiments/02-consumer-duty-complaint-intake .
    python scripts/sync_from_hub.py /path/to/experiment . --dry-run

Files listed in .sync-ignore are never overwritten. The copy does not delete
files that exist only in this repository. After a real copy,
apply_standalone_paths puts the schema path, repository URL and package import
back so the tree still runs on its own.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

from apply_standalone_paths import apply

SKIP_PARTS = {"__pycache__", ".pytest_cache", ".git"}


def load_ignore(root: Path) -> list[str]:
    ignore_file = root / ".sync-ignore"
    if not ignore_file.is_file():
        raise SystemExit(f"Missing {ignore_file}")
    patterns: list[str] = []
    for line in ignore_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        patterns.append(stripped.rstrip("/"))
    return patterns


def is_ignored(relative: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if relative == pattern or relative.startswith(pattern + "/"):
            return True
    return False


def iter_source_files(source: Path):
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_PARTS for part in path.relative_to(source).parts):
            continue
        if path.suffix == ".pyc":
            continue
        yield path.relative_to(source).as_posix(), path


def sync(source: Path, destination: Path, dry_run: bool) -> int:
    source = source.resolve()
    destination = destination.resolve()
    if not source.is_dir():
        raise SystemExit(f"Source is not a directory: {source}")
    patterns = load_ignore(destination)
    copied: list[str] = []
    unchanged: list[str] = []
    skipped: list[str] = []

    for relative, src_file in iter_source_files(source):
        if is_ignored(relative, patterns):
            skipped.append(relative)
            continue
        target = destination / relative
        if target.is_file() and filecmp.cmp(src_file, target, shallow=False):
            unchanged.append(relative)
            continue
        copied.append(relative)
        if dry_run:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, target)

    print(f"Source: {source}")
    print(f"Would copy {len(copied)} file(s)." if dry_run else f"Copied {len(copied)} file(s).")
    for relative in copied:
        print(f"  copy {relative}")
    print(f"Unchanged: {len(unchanged)}. Ignored: {len(skipped)}.")
    if skipped:
        print("Ignored:")
        for relative in skipped:
            print(f"  skip {relative}")

    if dry_run:
        print("Dry run. No files written and standalone paths not re-applied.")
        return 0

    changed = apply(destination)
    if changed:
        print("Re-applied standalone paths:")
        for path in changed:
            print(f"  rewrite {path}")
    else:
        print("Standalone paths already applied.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Hub experiment directory")
    parser.add_argument("destination", type=Path, help="This repository root")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    return sync(args.source, args.destination, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
