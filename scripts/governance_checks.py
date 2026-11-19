#!/usr/bin/env python3
"""Manifest, brand, secret and licence checks for this repository.

Run from the repository root:

    python scripts/governance_checks.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, ValidationError, validate

ROOT = Path(__file__).resolve().parents[1]
BANNED_BRAND = "Azure AI" + " Foundry"
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".txt",
    ".html",
    ".cff",
    ".toml",
    ".css",
    ".js",
}
EXTRA_NAMES = {"LICENSE", ".sync-ignore", ".gitignore"}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", ".jekyll-cache", "_site"}

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)(api[_-]?key|client[_-]?secret|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
)


def iter_text_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in EXTRA_NAMES:
            yield path


def check_brand() -> list[str]:
    failures: list[str] = []
    for path in iter_text_files():
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if BANNED_BRAND in line and "formerly" not in line.lower():
                relative = path.relative_to(ROOT)
                failures.append(
                    f"{relative}:{number}: '{BANNED_BRAND}' is only allowed in a 'formerly' note"
                )
    return failures


def check_secrets() -> list[str]:
    failures: list[str] = []
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"Possible secret in {path.relative_to(ROOT)}")
                break
    return failures


def check_licence() -> list[str]:
    failures: list[str] = []
    licence = ROOT / "LICENSE"
    readme = ROOT / "README.md"
    if not licence.is_file():
        failures.append("LICENSE is missing")
    elif "MIT" not in licence.read_text(encoding="utf-8"):
        failures.append("LICENSE does not mention MIT")
    if not readme.is_file():
        failures.append("README.md is missing")
    elif "MIT" not in readme.read_text(encoding="utf-8"):
        failures.append("README.md does not mention the MIT licence")
    return failures


def check_manifest() -> list[str]:
    failures: list[str] = []
    schema_path = ROOT / "schemas" / "agent-manifest.schema.json"
    manifest_path = ROOT / "agent-manifest.yaml"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft7Validator.check_schema(schema)
    except Exception as exc:  # noqa: BLE001 — report the validator's own message
        return [f"Schema is not valid Draft-07: {exc}"]

    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    try:
        validate(instance=manifest, schema=schema)
    except ValidationError as exc:
        failures.append(f"agent-manifest.yaml failed schema validation: {exc.message}")

    if manifest.get("$schema", "").startswith(".."):
        failures.append("agent-manifest.yaml still points at a hub-relative schema path")

    fixtures = sorted((ROOT / "tests" / "fixtures").glob("invalid-*.yaml"))
    if len(fixtures) < 2:
        failures.append("Expected at least two invalid manifest fixtures")
    for path in fixtures:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        try:
            validate(instance=document, schema=schema)
        except ValidationError:
            continue
        failures.append(f"{path.name} should have been rejected by the schema")

    valid = ROOT / "tests" / "fixtures" / "valid-manifest-a2-with-approval.yaml"
    document = yaml.safe_load(valid.read_text(encoding="utf-8"))
    try:
        validate(instance=document, schema=schema)
    except ValidationError as exc:
        failures.append(f"valid A2 fixture was rejected: {exc.message}")
    return failures


def main() -> int:
    checks = (
        ("Brand", check_brand()),
        ("Secrets", check_secrets()),
        ("Licence", check_licence()),
        ("Manifest", check_manifest()),
    )
    failed = False
    for name, failures in checks:
        if failures:
            failed = True
            print(f"{name} check failed:")
            for failure in failures:
                print(f"  {failure}")
        else:
            print(f"{name} check passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
