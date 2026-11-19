"""Schema checks for this repository's permissions manifest.

The schema and the invalid fixtures come from the Copilot Agent Experiments
catalogue. They are copied here so validation does not need the rest of the hub.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft7Validator, ValidationError, validate

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "agent-manifest.schema.json"
MANIFEST_PATH = ROOT / "agent-manifest.yaml"
FIXTURES = ROOT / "tests" / "fixtures"

HIGH_RISK = (
    "approve_reject",
    "regulated_decision",
    "production_record_change",
    "external_send",
    "spend_transact",
)


@pytest.fixture
def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_schema_is_valid_draft7(schema):
    Draft7Validator.check_schema(schema)


def test_manifest_validates_against_schema(schema, manifest):
    validate(instance=manifest, schema=schema)


def test_manifest_is_a1_and_cannot_act(manifest):
    assert manifest["agent"]["id"] == "exp-02-consumer-duty-complaint-intake"
    assert manifest["autonomy"]["level"] == "A1"
    assert manifest["autonomy"]["human_in_the_loop"] is True
    assert manifest["autonomy"]["auto_actions_enabled"] is False
    assert manifest["tools"]["writes"]["enabled"] is False
    assert manifest["tools"]["sends"]["enabled"] is False
    for action in HIGH_RISK:
        assert manifest["high_risk_actions"][action]["enabled"] is False
    assert manifest["high_risk_actions"]["additional_high_risk"]
    assert all(item["enabled"] is False for item in manifest["high_risk_actions"]["additional_high_risk"])
    assert manifest["agent"]["repository"] == (
        "https://github.com/rahul-bachina/consumer-duty-complaints-copilot-agent"
    )
    assert manifest["agent"]["experiment_path"] == "."
    assert manifest["$schema"] == "schemas/agent-manifest.schema.json"


def test_invalid_fixtures_are_rejected(schema):
    invalid = sorted(FIXTURES.glob("invalid-*.yaml"))
    assert len(invalid) >= 2
    for path in invalid:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        with pytest.raises(ValidationError):
            validate(instance=document, schema=schema)


def test_valid_a2_fixture_is_accepted(schema):
    document = yaml.safe_load(
        (FIXTURES / "valid-manifest-a2-with-approval.yaml").read_text(encoding="utf-8")
    )
    validate(instance=document, schema=schema)
    assert document["autonomy"]["level"] == "A2"
