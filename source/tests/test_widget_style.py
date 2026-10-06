"""Tests for resolving and applying the stored Qt widget style."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from appGUI.widget_style import apply_widget_style, resolve_widget_style

KEYS = ["macOS", "Windows", "Fusion"]


def test_resolve_widget_style_matches_a_name_ignoring_case() -> None:
    assert resolve_widget_style("fusion", KEYS) == "Fusion"


def test_resolve_widget_style_accepts_a_legacy_index() -> None:
    assert resolve_widget_style("2", KEYS) == "Fusion"
    assert resolve_widget_style("0", KEYS) == "macOS"


def test_resolve_widget_style_rejects_an_unknown_value() -> None:
    assert resolve_widget_style(None, KEYS) is None
    assert resolve_widget_style("", KEYS) is None
    assert resolve_widget_style("9", KEYS) is None
    assert resolve_widget_style("windowsvista", KEYS) is None


class _App:
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


def test_apply_widget_style_sets_the_style_under_an_existing_sheet() -> None:
    app = _App("QWidget { color: red; }")

    apply_widget_style(app, "Fusion")

    assert app.style_name == "Fusion"
    assert app.sheet == "QWidget { color: red; }"
    assert app.events == [
        ("sheet", ""),
        ("style", "Fusion"),
        ("sheet", "QWidget { color: red; }"),
    ]


def test_apply_widget_style_sets_the_style_when_there_is_no_sheet() -> None:
    app = _App()

    apply_widget_style(app, "Windows")

    assert app.events == [("style", "Windows")]
