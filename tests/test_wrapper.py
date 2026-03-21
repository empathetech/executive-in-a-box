"""Tests for the wrapper layer — secret scanning, context injection, validation."""

import json

from exec_in_a_box import storage
from exec_in_a_box.archetypes import OPERATOR
from exec_in_a_box.wrapper import (
    ValidatedResponse,
    build_prompt,
    redact_secrets,
    scan_for_secrets,
    validate_response,
)

# --- Secret Scanner Tests ---


def test_scan_detects_anthropic_key():
    text = "my key is sk-ant-abc123def456ghi789jkl012"
    matches = scan_for_secrets(text)
    assert len(matches) >= 1
    assert any("Anthropic" in m.pattern_name for m in matches)


def test_scan_detects_aws_key():
    text = "AWS_KEY=AKIAIOSFODNN7EXAMPLE"
    matches = scan_for_secrets(text)
    assert any("AWS" in m.pattern_name for m in matches)


def test_scan_detects_private_key():
    text = "-----BEGIN RSA PRIVATE KEY-----"
    matches = scan_for_secrets(text)
    assert any("Private key" in m.pattern_name for m in matches)


def test_scan_detects_password():
    text = "password = mysupersecretpass123"
    matches = scan_for_secrets(text)
    assert any("Password" in m.pattern_name for m in matches)


def test_scan_clean_text():
    text = "Our org builds tools for freelancers. We value transparency."
    matches = scan_for_secrets(text)
    assert matches == []


def test_scan_includes_line_number():
    text = "line one\npassword = hunter2\nline three"
    matches = scan_for_secrets(text)
    assert matches[0].line_number == 2


def test_redact_secrets():
    text = "key is sk-ant-abc123def456ghi789jkl012 and that's it"
    result = redact_secrets(text)
    assert "sk-ant-" not in result
    assert "[REDACTED]" in result


# --- Context Injection Tests ---


def test_build_prompt_returns_three_parts(tmp_path, monkeypatch):
    monkeypatch.setenv("EXEC_DATA_DIR", str(tmp_path))
    storage.ensure_data_dir()
    storage.write_file("org/profile.md", "# Test Org\nWe build things.")

    system, user_msg, secrets = build_prompt(OPERATOR, "Should we hire?")
    assert "ROLE:" in system
    assert "Test Org" in system
    assert "Should we hire?" in user_msg
    assert secrets == []


def test_build_prompt_detects_secrets_in_context(tmp_path, monkeypatch):
    monkeypatch.setenv("EXEC_DATA_DIR", str(tmp_path))
    storage.ensure_data_dir()
    storage.write_file(
        "org/profile.md", "# Org\napi_key = sk-ant-abc123def456ghi789jkl012"
    )

    system, user_msg, secrets = build_prompt(OPERATOR, "What should we do?")
    assert len(secrets) >= 1
    assert "[REDACTED]" in system


def test_build_prompt_detects_secrets_in_question(tmp_path, monkeypatch):
    monkeypatch.setenv("EXEC_DATA_DIR", str(tmp_path))
    storage.ensure_data_dir()

    _, _, secrets = build_prompt(
        OPERATOR, "My password = supersecret123 what do I do?"
    )
    assert len(secrets) >= 1


# --- Post-Call Validation Tests ---

VALID_RESPONSE = {
    "archetype": "The Operator",
    "position": "Do the simple thing first.",
    "reasoning": "Because it's cheaper and faster.",
    "confidence": "high",
    "ambition_level": "cautious",
    "pros": ["Fast", "Cheap"],
    "cons": ["Might not scale"],
    "flags": ["Check capacity first"],
    "questions_for_user": ["What's your timeline?"],
}


def test_validate_valid_response():
    result = validate_response(json.dumps(VALID_RESPONSE))
    assert isinstance(result, ValidatedResponse)
    assert result.archetype == "The Operator"
    assert result.confidence == "high"
    assert len(result.pros) == 2


def test_validate_strips_code_fences():
    wrapped = f"```json\n{json.dumps(VALID_RESPONSE)}\n```"
    result = validate_response(wrapped)
    assert isinstance(result, ValidatedResponse)


def test_validate_rejects_invalid_json():
    result = validate_response("this is not json")
    assert isinstance(result, list)
    assert result[0].field == "_root"


def test_validate_rejects_missing_field():
    bad = {**VALID_RESPONSE}
    del bad["confidence"]
    result = validate_response(json.dumps(bad))
    assert isinstance(result, list)
    assert any(e.field == "confidence" for e in result)


def test_validate_rejects_invalid_confidence():
    bad = {**VALID_RESPONSE, "confidence": "maybe"}
    result = validate_response(json.dumps(bad))
    assert isinstance(result, list)
    assert any(e.field == "confidence" for e in result)


def test_validate_rejects_invalid_ambition():
    bad = {**VALID_RESPONSE, "ambition_level": "yolo"}
    result = validate_response(json.dumps(bad))
    assert isinstance(result, list)
    assert any(e.field == "ambition_level" for e in result)


def test_validate_rejects_empty_pros():
    bad = {**VALID_RESPONSE, "pros": []}
    result = validate_response(json.dumps(bad))
    assert isinstance(result, list)
    assert any(e.field == "pros" for e in result)


def test_validate_rejects_empty_cons():
    bad = {**VALID_RESPONSE, "cons": []}
    result = validate_response(json.dumps(bad))
    assert isinstance(result, list)
    assert any(e.field == "cons" for e in result)


def test_validate_rejects_empty_position():
    bad = {**VALID_RESPONSE, "position": "  "}
    result = validate_response(json.dumps(bad))
    assert isinstance(result, list)
    assert any(e.field == "position" for e in result)


def test_validate_rejects_wrong_type():
    bad = {**VALID_RESPONSE, "pros": "not a list"}
    result = validate_response(json.dumps(bad))
    assert isinstance(result, list)
    assert any(e.field == "pros" for e in result)
