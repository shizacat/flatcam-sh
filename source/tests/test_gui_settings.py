"""Tests for the shared GUI settings store."""

import sys
from pathlib import Path

import pytest
from PyQt6.QtCore import QSettings

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from settings.gui_settings import GuiSettings


@pytest.fixture(scope="module", autouse=True)
def qapplication():
    """Create the Qt application before any QSettings object.

    A QSettings created first is deleted when QApplication is constructed.
    """
    from PyQt6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


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


def test_resolve_style_matches_a_name_ignoring_case() -> None:
    """Verify a stored style name matches the toolkit name without regard to case."""
    keys = ["macOS", "Windows", "Fusion"]

    assert GuiSettings.resolve_style("fusion", keys) == "Fusion"


def test_resolve_style_rejects_an_unknown_value() -> None:
    """Verify a missing or unknown style name is left unresolved."""
    keys = ["macOS", "Windows", "Fusion"]

    assert GuiSettings.resolve_style(None, keys) is None
    assert GuiSettings.resolve_style("", keys) is None
    assert GuiSettings.resolve_style("0", keys) is None
    assert GuiSettings.resolve_style("2", keys) is None
    assert GuiSettings.resolve_style("windowsvista", keys) is None


class _StyleApp:
    def __init__(self, sheet: str = "") -> None:
        self.sheet = sheet
        self.style_name = ""
        self.events: list[tuple[str, str]] = []

    def styleSheet(self) -> str:
        return self.sheet

    def setStyleSheet(self, sheet: str) -> None:
        self.events.append(("sheet", sheet))
        self.sheet = sheet

    def setStyle(self, name: str) -> None:
        self.events.append(("style", name))
        self.style_name = name


def test_set_widget_style_keeps_an_existing_sheet() -> None:
    """Verify the widget style changes underneath a stylesheet that is then restored."""
    app = _StyleApp("QWidget { color: red; }")

    GuiSettings.set_widget_style(app, "Fusion")

    assert app.style_name == "Fusion"
    assert app.sheet == "QWidget { color: red; }"
    assert app.events == [
        ("sheet", ""),
        ("style", "Fusion"),
        ("sheet", "QWidget { color: red; }"),
    ]


def test_set_widget_style_sets_the_style_when_there_is_no_sheet() -> None:
    """Verify the widget style is set directly when no stylesheet is active."""
    app = _StyleApp()

    GuiSettings.set_widget_style(app, "Windows")

    assert app.events == [("style", "Windows")]


def test_style_name_uses_the_stored_name(gui_settings: GuiSettings) -> None:
    """Verify the stored style is the name reported for the current choice."""
    from PyQt6.QtWidgets import QApplication, QStyleFactory

    app = QApplication.instance()
    assert app is not None
    available = QStyleFactory.keys()
    assert available
    gui_settings.set_value("style", available[0].swapcase())

    assert gui_settings.style_name(app) == available[0]


def test_style_name_falls_back_to_the_application_style(gui_settings: GuiSettings) -> None:
    """Verify an unknown stored name falls back to the style already in use."""
    from PyQt6.QtWidgets import QApplication, QStyleFactory

    app = QApplication.instance()
    assert app is not None
    gui_settings.set_value("style", "not-a-style")

    assert gui_settings.style_name(app) == GuiSettings.resolve_style(
        app.style().objectName(),
        QStyleFactory.keys(),
    )


def test_apply_style_sets_a_stored_style_name(gui_settings: GuiSettings) -> None:
    """Verify a stored style name is applied when this process provides it."""
    from PyQt6.QtWidgets import QApplication, QStyleFactory

    available = QStyleFactory.keys()
    assert available
    app = QApplication.instance()
    assert app is not None
    gui_settings.set_value("style", available[0])

    gui_settings.apply_style(app)

    assert app.style().objectName().lower() == available[0].lower()


def test_apply_style_ignores_an_unknown_name(gui_settings: GuiSettings) -> None:
    """Verify an unknown style name leaves the current style in place."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance()
    assert app is not None
    current = app.style().objectName()
    gui_settings.set_value("style", "not-a-style")

    gui_settings.apply_style(app)

    assert app.style().objectName() == current


def test_apply_font_size_sets_the_stored_size(gui_settings: GuiSettings) -> None:
    """Verify a stored font size is applied, and a missing key leaves the font alone."""

    class _FontApp:
        def __init__(self) -> None:
            self.font = None

        def setFont(self, font) -> None:
            self.font = font

    untouched = _FontApp()
    gui_settings.apply_font_size(untouched)
    assert untouched.font is None

    gui_settings.set_value("font_size", "14")
    app = _FontApp()
    gui_settings.apply_font_size(app)

    assert app.font is not None
    assert app.font.pointSize() == 14


def test_gui_settings_reset_installs_another_store(tmp_path: Path) -> None:
    """Verify reset replaces the shared store and can leave it unset."""
    first = GuiSettings.reset(QSettings(str(tmp_path / "first.ini"), QSettings.Format.IniFormat))
    second = GuiSettings.reset(QSettings(str(tmp_path / "second.ini"), QSettings.Format.IniFormat))

    assert first is not second
    assert GuiSettings() is second

    assert GuiSettings.reset() is None
