"""Qt color scheme applied over the selected widget style."""

from PyQt6.QtWidgets import QApplication


def color_scheme_name(appearance: str) -> str:
    """
    Maps a saved color choice onto a Qt color scheme name.

    ``system`` follows the operating system. Retired names ``default`` and ``auto`` do too.

    :param appearance: ``system``, ``light``, ``dark``, or a retired name
    :return:           ``light``, ``dark``, or ``system``
    """
    if appearance == "light":
        return "light"
    if appearance == "dark":
        return "dark"
    return "system"


def apply_color_scheme(app: QApplication, appearance: str) -> None:
    """
    Sets the application color scheme and leaves the widget style in place.

    :param app:        the ``QApplication``
    :param appearance: ``system``, ``light``, ``dark``, or a retired name
    """
    from PyQt6.QtCore import Qt

    scheme = {
        "light": Qt.ColorScheme.Light,
        "dark": Qt.ColorScheme.Dark,
    }.get(color_scheme_name(appearance), Qt.ColorScheme.Unknown)
    app.styleHints().setColorScheme(scheme)
