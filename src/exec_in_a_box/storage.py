"""Local file storage layer.

All persistent data is stored as plain markdown and JSON files on the user's
machine. Files are human-readable and human-editable.

Reference: hacky-hours/02-design/ARCHITECTURE.md § Context / Memory Store
"""

import json
import os
import stat
from pathlib import Path

# Default data directory
DEFAULT_DATA_DIR = Path.home() / ".executive-in-a-box"

# Subdirectories created on first run
SUBDIRS = ["org", "board", "board/archetypes", "sessions", "memory", "jobs", "artifacts"]

# Files with restricted permissions (owner read/write only)
# Note: API keys are stored in the OS keychain, not in files.
# Config files no longer contain secrets.
RESTRICTED_FILES: set[str] = set()


def get_data_dir() -> Path:
    """Return the data directory, respecting EXEC_DATA_DIR env var."""
    custom = os.environ.get("EXEC_DATA_DIR")
    if custom:
        return Path(custom).expanduser().resolve()
    return DEFAULT_DATA_DIR


def ensure_data_dir() -> Path:
    """Create the data directory and subdirectories if they don't exist.

    Returns the data directory path.
    """
    data_dir = get_data_dir()
    for subdir in SUBDIRS:
        (data_dir / subdir).mkdir(parents=True, exist_ok=True)
    return data_dir


def is_initialized() -> bool:
    """Check if the data directory exists and has a board config."""
    data_dir = get_data_dir()
    return (data_dir / "board" / "config.md").exists()


def read_file(relative_path: str) -> str | None:
    """Read a file from the data directory. Returns None if it doesn't exist."""
    path = get_data_dir() / relative_path
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def write_file(relative_path: str, content: str) -> Path:
    """Write a file to the data directory. Creates parent dirs as needed.

    Sets restricted permissions for sensitive files (config).
    """
    path = get_data_dir() / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

    if relative_path in RESTRICTED_FILES:
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 600

    return path


def append_file(relative_path: str, content: str) -> Path:
    """Append content to a file in the data directory. Creates it if needed."""
    path = get_data_dir() / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)
    return path


def read_json(relative_path: str) -> dict | None:
    """Read a JSON file from the data directory. Returns None if missing."""
    text = read_file(relative_path)
    if text is None:
        return None
    return json.loads(text)


def write_json(relative_path: str, data: dict) -> Path:
    """Write a dict as JSON to the data directory."""
    content = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    return write_file(relative_path, content)


SESSION_INDEX = "sessions/index.json"


def read_session_index() -> list[dict]:
    """Read the session index. Returns an empty list if it doesn't exist yet."""
    path = get_data_dir() / SESSION_INDEX
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def append_session_index(entry: dict) -> None:
    """Append a session entry to the index. Creates the index if needed."""
    index = read_session_index()
    index.append(entry)
    path = get_data_dir() / SESSION_INDEX
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def list_sessions() -> list[Path]:
    """List session transcript files, sorted newest first."""
    sessions_dir = get_data_dir() / "sessions"
    if not sessions_dir.exists():
        return []
    files = sorted(sessions_dir.glob("*.md"), reverse=True)
    return files


def next_session_path() -> Path:
    """Generate the next session file path for today."""
    from datetime import date

    today = date.today().isoformat()
    sessions_dir = get_data_dir() / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(sessions_dir.glob(f"{today}-*.md"))
    if existing:
        last_num = int(existing[-1].stem.split("-")[-1])
        next_num = last_num + 1
    else:
        next_num = 1

    return sessions_dir / f"{today}-{next_num:03d}.md"
