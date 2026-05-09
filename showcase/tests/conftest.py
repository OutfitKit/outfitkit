"""Shared fixtures for the OutfitKit tests."""
from __future__ import annotations

from pathlib import Path

import pytest

UI_DIR = Path(__file__).resolve().parents[1] / "src" / "outfitkit" / "templates" / "ui"


@pytest.fixture(scope="session")
def ui_dir() -> Path:
    return UI_DIR


@pytest.fixture(scope="session")
def component_files(ui_dir: Path) -> list[Path]:
    """All public component files under templates/ui/."""
    files = sorted(ui_dir.glob("*.jinja"))
    assert files, f"No component files found in {ui_dir}"
    return files
