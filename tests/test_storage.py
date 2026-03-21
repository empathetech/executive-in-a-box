"""Tests for the local file storage layer."""

import os
import stat

import pytest

from exec_in_a_box import storage


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Use a temporary directory for all storage operations."""
    monkeypatch.setenv("EXEC_DATA_DIR", str(tmp_path))
    return tmp_path


def test_ensure_data_dir_creates_subdirs(data_dir):
    result = storage.ensure_data_dir()
    assert result == data_dir
    for subdir in storage.SUBDIRS:
        assert (data_dir / subdir).is_dir()


def test_is_initialized_false_when_fresh(data_dir):
    assert storage.is_initialized() is False


def test_is_initialized_true_after_config(data_dir):
    storage.ensure_data_dir()
    storage.write_file("board/config.md", "# Config\n")
    assert storage.is_initialized() is True


def test_read_file_returns_none_for_missing(data_dir):
    assert storage.read_file("nonexistent.md") is None


def test_write_and_read_file(data_dir):
    storage.ensure_data_dir()
    storage.write_file("org/profile.md", "# My Org\n")
    content = storage.read_file("org/profile.md")
    assert content == "# My Org\n"


def test_config_file_no_longer_restricted(data_dir):
    """API keys are in OS keychain now, not config files."""
    storage.ensure_data_dir()
    path = storage.write_file("board/config.md", "no secrets here")
    mode = os.stat(path).st_mode
    # File should have normal permissions (not 600)
    assert stat.S_IMODE(mode) != 0o600


def test_append_file(data_dir):
    storage.ensure_data_dir()
    storage.write_file("org/decisions.md", "# Decisions\n")
    storage.append_file("org/decisions.md", "\n## Decision 1\nDid a thing.\n")
    content = storage.read_file("org/decisions.md")
    assert "Decision 1" in content
    assert content.startswith("# Decisions")


def test_json_round_trip(data_dir):
    storage.ensure_data_dir()
    data = {"name": "Test Org", "values": ["transparency", "equity"]}
    storage.write_json("org/data.json", data)
    result = storage.read_json("org/data.json")
    assert result == data


def test_read_json_returns_none_for_missing(data_dir):
    assert storage.read_json("missing.json") is None


def test_list_sessions_empty(data_dir):
    storage.ensure_data_dir()
    assert storage.list_sessions() == []


def test_next_session_path_first_of_day(data_dir):
    storage.ensure_data_dir()
    path = storage.next_session_path()
    assert path.name.endswith("-001.md")


def test_next_session_path_increments(data_dir):
    storage.ensure_data_dir()
    first = storage.next_session_path()
    first.write_text("session 1")
    second = storage.next_session_path()
    assert second.name.endswith("-002.md")
