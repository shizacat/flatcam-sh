"""Tests for the shared GUI settings store."""

import sys
from pathlib import Path

import pytest
from PyQt6.QtCore import QSettings

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from settings.gui_settings import GuiSettings


@pytest.fixture
def gui_settings(tmp_path: Path):
    """Point the singleton at a temporary file and drop it afterwards."""
    store = QSettings(str(tmp_path / "gui.ini"), QSettings.Format.IniFormat)
    settings = GuiSettings.reset(store)
    assert settings is not None
    yield settings
    GuiSettings.reset()


def test_gui_settings_returns_the_same_instance(gui_settings: GuiSettings) -> None:
    """Verify every call returns the shared instance."""
    assert GuiSettings() is gui_settings


def test_gui_settings_reads_and_writes_a_value(gui_settings: GuiSettings) -> None:
    """Verify a written value is readable and typed as requested."""
    assert gui_settings.contains("style") is False

    gui_settings.set_value("style", "Fusion")

    assert gui_settings.contains("style") is True
    assert gui_settings.value("style") == "Fusion"
    assert gui_settings.value("style", value_type=str) == "Fusion"
    assert gui_settings.value("missing", "compact") == "compact"
    assert gui_settings.keys() == ["style"]


def test_gui_settings_removes_one_key_and_clears_the_rest(gui_settings: GuiSettings) -> None:
    """Verify one key can be removed and the remaining keys can be cleared."""
    gui_settings.set_value("style", "Fusion")
    gui_settings.set_value("font_size", "12")

    gui_settings.remove("style")

    assert gui_settings.contains("style") is False
    assert gui_settings.value("font_size") == "12"

    gui_settings.clear()

    assert gui_settings.keys() == []


def test_gui_settings_reset_installs_another_store(tmp_path: Path) -> None:
    """Verify reset replaces the shared store and can leave it unset."""
    first = GuiSettings.reset(QSettings(str(tmp_path / "first.ini"), QSettings.Format.IniFormat))
    second = GuiSettings.reset(QSettings(str(tmp_path / "second.ini"), QSettings.Format.IniFormat))

    assert first is not second
    assert GuiSettings() is second

    assert GuiSettings.reset() is None
