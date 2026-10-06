"""Qt widget style stored in application settings."""


def resolve_widget_style(saved: str | None, available: list[str]) -> str | None:
    """
    Resolves a stored Qt style to one of the styles available in this process.

    A stored value is either a style name or a legacy combo index.

    :param saved:     text read from settings; None when the setting is absent
    :param available: style names reported by the toolkit
    :return:          a name from ``available``, or None when nothing matches
    """
    if not saved or not available:
        return None
    for name in available:
        if name.lower() == saved.lower():
            return name
    if saved.isdigit():
        index = int(saved)
        if 0 <= index < len(available):
            return available[index]
    return None


def apply_widget_style(app, name: str) -> None:
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
