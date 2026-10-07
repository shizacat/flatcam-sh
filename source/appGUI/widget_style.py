"""Qt widget style stored in application settings."""

from PyQt6.QtWidgets import QApplication


def resolve_widget_style(saved: str | None, available: list[str]) -> str | None:
    """
    Resolves a stored Qt style name to one of the styles available in this process.

    :param saved:     style name read from settings; None when the setting is absent
    :param available: style names reported by the toolkit
    :return:          a name from ``available``, or None when nothing matches
    """
    if not saved or not available:
        return None
    for name in available:
        if name.lower() == saved.lower():
            return name
    return None


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


def apply_widget_style(app: QApplication, name: str) -> None:
    """
    Sets the application widget style and keeps an existing stylesheet on top of it.

    A stylesheet replaces the style object, so changing the style while it is set
    leaves the previous style in place. The sheet is cleared, the style is set,
    and the same sheet is put back.

    :param app:  the ``QApplication``
    :param name: a style name from ``QStyleFactory.keys()``
    """
    sheet = app.styleSheet()
    if sheet:
        app.setStyleSheet("")
    try:
        app.setStyle(name)
    finally:
        if sheet:
            app.setStyleSheet(sheet)
