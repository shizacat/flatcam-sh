"""Tests for resolving and applying the stored Qt widget style."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PyQt6.QtCore import Qt

from appGUI.widget_style import apply_color_scheme, color_scheme_name


def test_color_scheme_name_maps_choices_and_retired_names() -> None:
    assert color_scheme_name("light") == "light"
    assert color_scheme_name("dark") == "dark"
    assert color_scheme_name("system") == "system"
    assert color_scheme_name("default") == "system"
    assert color_scheme_name("auto") == "system"


class _Hints:
    def __init__(self) -> None:
        self.scheme = None

    def setColorScheme(self, scheme) -> None:
        self.scheme = scheme


class _ColorApp:
    def __init__(self) -> None:
        self.hints = _Hints()

    def styleHints(self) -> _Hints:
        return self.hints


def test_apply_color_scheme_sets_the_qt_scheme() -> None:
    app = _ColorApp()

    apply_color_scheme(app, "dark")
    assert app.hints.scheme is Qt.ColorScheme.Dark

    apply_color_scheme(app, "system")
    assert app.hints.scheme is Qt.ColorScheme.Unknown
