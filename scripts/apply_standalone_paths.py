#!/usr/bin/env python3
"""Rewrite hub-relative paths so the experiment runs at the repository root.

The weekly sync copies experiments/02-consumer-duty-complaint-intake/ from
https://github.com/rahul-bachina/copilot-agent-experiments over this tree.
That copy puts the catalogue's schema path and repository URL back. This
script puts the standalone paths back afterwards. It is idempotent.
"""

from __future__ import annotations

import sys
from pathlib import Path

HUB_REPOSITORY = "https://github.com/rahul-bachina/copilot-agent-experiments"
STANDALONE_REPOSITORY = (
    "https://github.com/rahul-bachina/consumer-duty-complaints-copilot-agent"
)
HUB_SCHEMA = '$schema: "../../../schemas/agent-manifest.schema.json"'
STANDALONE_SCHEMA = '$schema: "schemas/agent-manifest.schema.json"'
HUB_EXPERIMENT_PATH = 'experiment_path: "experiments/02-consumer-duty-complaint-intake"'
STANDALONE_EXPERIMENT_PATH = 'experiment_path: "."'

PACKAGE_IMPORT = """\
# Standalone import: script (`python src/intake.py`) and package (`python -m src.intake`).
if __package__:
    from .disp_clock import ROUTES, calculate_disp_clock
else:
    from disp_clock import ROUTES, calculate_disp_clock
"""
HUB_IMPORT = "from disp_clock import ROUTES, calculate_disp_clock\n"


def apply(root: Path) -> list[str]:
    """Return the paths whose contents changed."""
    changed: list[str] = []

    manifest_path = root / "agent-manifest.yaml"
    if manifest_path.is_file():
        original = manifest_path.read_text(encoding="utf-8")
        text = original.replace(HUB_SCHEMA, STANDALONE_SCHEMA)
        text = text.replace(
            f'repository: "{HUB_REPOSITORY}"',
            f'repository: "{STANDALONE_REPOSITORY}"',
        )
        text = text.replace(HUB_EXPERIMENT_PATH, STANDALONE_EXPERIMENT_PATH)
        if text != original:
            manifest_path.write_text(text, encoding="utf-8")
            changed.append(manifest_path.relative_to(root).as_posix())

    intake_path = root / "src" / "intake.py"
    if intake_path.is_file():
        original = intake_path.read_text(encoding="utf-8")
        text = original
        if "if __package__:" not in text and HUB_IMPORT in text:
            text = text.replace(HUB_IMPORT, PACKAGE_IMPORT, 1)
        if text != original:
            intake_path.write_text(text, encoding="utf-8")
            changed.append(intake_path.relative_to(root).as_posix())

    return changed


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]).resolve() if argv else Path(__file__).resolve().parents[1]
    changed = apply(root)
    if changed:
        print("Updated standalone paths:")
        for path in changed:
            print(f"  {path}")
    else:
        print("Standalone paths already applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
