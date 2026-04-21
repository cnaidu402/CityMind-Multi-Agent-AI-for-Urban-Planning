"""Application settings and lightweight environment loading."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(slots=True)
class AppSettings:
    """Project-wide runtime settings."""

    openai_api_key: str | None
    openai_model: str


def _read_dotenv_file() -> dict[str, str]:
    """
    Read a simple repo-root `.env` file without adding a dependency.

    This parser intentionally supports just `KEY=value` lines, which is enough
    for local development secrets like `OPENAI_API_KEY=...`.
    """
    repo_root = Path(__file__).resolve().parents[2]
    dotenv_path = repo_root / ".env"
    if not dotenv_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Load settings from environment variables with optional `.env` fallback."""
    dotenv_values = _read_dotenv_file()

    openai_api_key = (
        os.getenv("OPENAI_API_KEY")
        or dotenv_values.get("OPENAI_API_KEY")
    )
    openai_model = (
        os.getenv("OPENAI_MODEL")
        or dotenv_values.get("OPENAI_MODEL")
        or "gpt-4.1"
    )
    return AppSettings(
        openai_api_key=openai_api_key,
        openai_model=openai_model,
    )
