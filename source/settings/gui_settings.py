"""Process-wide access to the GUI settings stored by Qt."""

from __future__ import annotations

import threading
from typing import Any, ClassVar, Self

from PyQt6 import sip
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QStyleFactory

from settings.st_types import Theme


class GuiSettings:
    """
    Shared handle for ``QSettings("Open Source", "FlatCAM_EVO")``.

    Qt keeps this store outside the FlatConfig file. One instance serves the whole
    process, so a later read sees an earlier write without constructing ``QSettings`` again.
    The Qt store is opened on the first read or write. A store opened before
    ``QApplication`` exists is replaced, because Qt deletes it when the application starts.

    Writes are synced immediately. The instance lives for the process and would otherwise
    keep the new value in memory until it is destroyed.
    """

    organization: ClassVar[str] = "Open Source"
    application: ClassVar[str] = "FlatCAM_EVO"

    _instance: ClassVar[GuiSettings | None] = None
    _lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls) -> Self:
        """
        Returns the shared instance, creating it on the first call.

        :return: the process-wide GUI settings
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._store = None
                    cls._instance = instance
        return cls._instance

    def _qsettings(self) -> QSettings:
        """
        Returns the Qt store, opening it on the first use.

        :return: the ``QSettings`` object for this application
        """
        store = self._store
        if store is None or sip.isdeleted(store):
            self._store = QSettings(type(self).organization, type(self).application)
        return self._store

    def contains(self, key: str) -> bool:
        """
        Reports whether a key is present.

        :param key: setting name
        :return:    True when the key has a stored value
        """
        return self._qsettings().contains(key)

    def value(self, key: str, default: Any = None, *, value_type: type | None = None) -> Any:
        """
        Reads a stored value.

        ``value_type`` asks Qt to convert the stored value. A missing key then yields
        the default constructed value of that type, such as ``""`` for ``str``.

        :param key:        setting name
        :param default:    value used when the key is absent and ``value_type`` is omitted
        :param value_type: type Qt should convert the stored value to
        :return:           stored value, or ``default`` when the key is absent
        """
        if value_type is None:
            if default is None:
                return self._qsettings().value(key)
            return self._qsettings().value(key, default)
        if default is None:
            return self._qsettings().value(key, type=value_type)
        return self._qsettings().value(key, default, type=value_type)

    def set_value(self, key: str, value: Any) -> None:
        """
        Stores a value and writes it to the platform store.

        :param key:   setting name
        :param value: value to store
        """
        self._qsettings().setValue(key, value)
        self.sync()

    def remove(self, key: str) -> None:
        """
        Deletes one key and writes the store.

        :param key: setting name
        """
        self._qsettings().remove(key)
        self.sync()

    def keys(self) -> list[str]:
        """
        Lists the stored key names.

        :return: key names
        """
        return list(self._qsettings().allKeys())

    def clear(self) -> None:
        """
        Deletes every key and writes the store.
        """
        self._qsettings().clear()
        self.sync()

    def sync(self) -> None:
        """
        Writes pending values to the platform store.
        """
        self._qsettings().sync()

    @staticmethod
    def resolve_style(saved: str | None, available: list[str]) -> str | None:
        """
        Resolves a style name to one of the styles available in this process.

        :param saved:     style name; None when the setting is absent
        :param available: style names reported by the toolkit
        :return:          a name from ``available``, or None when nothing matches
        """
        if not saved or not available:
            return None
        for name in available:
            if name.lower() == saved.lower():
                return name
        return None

    @staticmethod
    def set_widget_style(app: QApplication, name: str) -> None:
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

    def style_name(self, app: QApplication) -> str | None:
        """
        Returns the style name to show as the current choice.

        The stored name is used when this process provides it. Otherwise the name of
        the style already set on ``app`` is used.

        :param app: the ``QApplication``
        :return:    a name from ``QStyleFactory.keys()``, or None when neither matches
        """
        name = self._stored_style()
        if name is not None:
            return name
        return self.resolve_style(app.style().objectName(), QStyleFactory.keys())

    def _stored_style(self) -> str | None:
        """
        Returns the stored style when this process provides it.

        :return: a name from ``QStyleFactory.keys()``, or None
        """
        saved = self.value("style", value_type=str) if self.contains("style") else None
        return self.resolve_style(saved, QStyleFactory.keys())

    def save_style(self, app: QApplication, name: str) -> str | None:
        """
        Stores a widget style name and applies it.

        A name this process does not provide is ignored.

        :param app:  the ``QApplication``
        :param name: style name chosen in the interface
        :return:     the stored name, or None when ``name`` is not available
        """
        resolved = self.resolve_style(name, QStyleFactory.keys())
        if resolved is None:
            return None
        self.set_value("style", resolved)
        self.set_widget_style(app, resolved)
        return resolved

    def apply_style(self, app: QApplication) -> None:
        """
        Applies the stored widget style when this process provides that style.

        A missing key, or a name that is not in ``QStyleFactory.keys()``, leaves the
        current style in place.

        :param app: the ``QApplication``
        """
        name = self._stored_style()
        if name is not None:
            self.set_widget_style(app, name)

    def font_size(self) -> int | None:
        """
        Returns the stored application font size.

        :return: size in points, or None when the key is absent
        """
        if not self.contains("font_size"):
            return None
        return int(self.value("font_size", value_type=str))

    def save_font_size(self, size: int) -> None:
        """
        Stores the application font size.

        The new size is applied on the next start.

        :param size: size in points
        """
        self.set_value("font_size", str(size))

    def hud_font_size(self, default: int = 8) -> int:
        """
        Returns the stored HUD font size.

        :param default: size in points used when the key is absent
        :return:        size in points
        """
        return self._stored_int("hud_font_size", default)

    def save_hud_font_size(self, size: int) -> None:
        """
        Stores the HUD font size.

        :param size: size in points
        """
        self.set_value("hud_font_size", size)

    def notebook_font_size(self, default: int = 12) -> int:
        """
        Returns the stored notebook font size.

        :param default: size in pixels used when the key is absent
        :return:        size in pixels
        """
        return self._stored_int("notebook_font_size", default)

    def save_notebook_font_size(self, size: int) -> None:
        """
        Stores the notebook font size.

        :param size: size in pixels
        """
        self.set_value("notebook_font_size", size)

    def axis_font_size(self, default: int = 8) -> int:
        """
        Returns the stored canvas axis font size.

        :param default: size in points used when the key is absent
        :return:        size in points
        """
        return self._stored_int("axis_font_size", default)

    def save_axis_font_size(self, size: int) -> None:
        """
        Stores the canvas axis font size.

        :param size: size in points
        """
        self.set_value("axis_font_size", size)

    def textbox_font_size(self, default: int = 10) -> int:
        """
        Returns the stored text box font size.

        :param default: size in points used when the key is absent
        :return:        size in points
        """
        return self._stored_int("textbox_font_size", default)

    def save_textbox_font_size(self, size: int) -> None:
        """
        Stores the text box font size.

        :param size: size in points
        """
        self.set_value("textbox_font_size", size)

    def theme(self) -> Theme:
        """
        Returns the stored plot theme.

        A missing key and the retired name ``default`` are the light theme.

        :return: the light or dark theme
        """
        if self._stored_text("theme") == Theme.DARK:
            return Theme.DARK
        return Theme.LIGHT

    def save_theme(self, theme: Theme) -> None:
        """
        Stores the plot theme.

        :param theme: light or dark theme
        """
        self.set_value("theme", str(theme))

    def dark_canvas(self) -> bool | None:
        """
        Returns whether the plot canvas is forced dark.

        :return: the stored flag, or None when the key is absent
        """
        return self._stored_bool("dark_canvas")

    def save_dark_canvas(self, enabled: bool) -> None:
        """
        Stores whether the plot canvas is forced dark.

        :param enabled: True to draw the canvas dark
        """
        self.set_value("dark_canvas", enabled)

    def appearance(self) -> str | None:
        """
        Returns the stored color appearance.

        :return: ``system``, ``light``, ``dark``, or None when the key is absent
        """
        return self._stored_text("appearance")

    def save_appearance(self, appearance: object) -> None:
        """
        Stores the color appearance chosen for this session.

        :param appearance: appearance name or enum stored as Qt left it
        """
        self.set_value("appearance", appearance)

    def language(self) -> str | None:
        """
        Returns the stored interface language.

        :return: language name, or None when the key is absent
        """
        return self._stored_text("language")

    def save_language(self, name: str) -> None:
        """
        Stores the interface language.

        :param name: language name shown in Preferences
        """
        self.set_value("language", name)

    def layout(self) -> str | None:
        """
        Returns the stored window layout.

        :return: ``standard``, ``compact``, ``minimal``, or None when the key is absent
        """
        return self._stored_text("layout")

    def save_layout(self, name: str) -> None:
        """
        Stores the window layout.

        :param name: layout name
        """
        self.set_value("layout", name)

    def splash_screen(self) -> bool | None:
        """
        Returns whether the splash screen is shown at startup.

        :return: the stored flag, or None when the key is absent
        """
        if not self.contains("splash_screen"):
            return None
        return bool(self.value("splash_screen"))

    def save_splash_screen(self, enabled: bool) -> None:
        """
        Stores whether the splash screen is shown at startup.

        The value is ``1`` or ``0``, matching the existing preference checkbox.

        :param enabled: True to show the splash screen
        """
        self.set_value("splash_screen", 1 if enabled else 0)

    def maximized_gui(self) -> bool | None:
        """
        Returns whether the main window was maximized.

        :return: the stored flag, or None when the key is absent
        """
        return self._stored_bool("maximized_gui")

    def save_maximized_gui(self, maximized: bool) -> None:
        """
        Stores whether the main window is maximized.

        :param maximized: True when the window is maximized
        """
        self.set_value("maximized_gui", maximized)

    def saved_gui_state(self) -> Any | None:
        """
        Returns the stored main-window state.

        :return: the ``QByteArray`` from ``saveState``, or None when the key is absent
        """
        if not self.contains("saved_gui_state"):
            return None
        return self.value("saved_gui_state")

    def save_gui_state(self, state: Any) -> None:
        """
        Stores the main-window state.

        :param state: value returned by ``QMainWindow.saveState``
        """
        self.set_value("saved_gui_state", state)

    def toolbar_lock(self) -> Any:
        """
        Returns the stored toolbar lock.

        A missing key is the string ``true``. A stored bool is returned as Qt stored it.

        :return: the stored lock
        """
        return self.value("toolbar_lock", "true")

    def save_toolbar_lock(self, locked: Any) -> None:
        """
        Stores the toolbar lock.

        :param locked: checked state of the lock action
        """
        self.set_value("toolbar_lock", locked)

    def menu_show_text(self) -> Any:
        """
        Returns whether toolbar buttons show text.

        A missing key is the string ``true``.

        :return: the stored flag
        """
        return self.value("menu_show_text", "true")

    def save_menu_show_text(self, show_text: Any) -> None:
        """
        Stores whether toolbar buttons show text.

        :param show_text: checked state of the show-text action
        """
        self.set_value("menu_show_text", show_text)

    def window_geometry(self) -> Any:
        """
        Returns the stored window geometry.

        A missing key is ``(100, 100, 800, 400)``.

        :return: ``(x, y, width, height)``
        """
        return self.value("window_geometry", (100, 100, 800, 400))

    def save_window_geometry(self, geometry: tuple[int, int, int, int]) -> None:
        """
        Stores the window geometry.

        :param geometry: ``(x, y, width, height)``
        """
        self.set_value("window_geometry", geometry)

    def splitter_left(self) -> int:
        """
        Returns the stored width of the left splitter pane.

        :return: width in pixels; ``1`` when the key is absent
        """
        return int(self.value("splitter_left", 1))

    def save_splitter_left(self, width: int) -> None:
        """
        Stores the width of the left splitter pane.

        :param width: width in pixels
        """
        self.set_value("splitter_left", width)

    def _stored_int(self, key: str, default: int) -> int:
        """
        Returns a stored integer.

        :param key:     settings key
        :param default: value used when the key is absent
        :return:        the stored integer, or ``default``
        """
        if not self.contains(key):
            return default
        return int(self.value(key, value_type=int))

    def _stored_text(self, key: str, default: str | None = None) -> str | None:
        """
        Returns a stored string.

        :param key:     settings key
        :param default: value used when the key is absent
        :return:        the stored string, or ``default``
        """
        if not self.contains(key):
            return default
        return self.value(key, value_type=str)

    def _stored_bool(self, key: str) -> bool | None:
        """
        Returns a stored flag.

        :param key: settings key
        :return:    the stored flag, or None when the key is absent
        """
        if not self.contains(key):
            return None
        return bool(self.value(key, value_type=bool))

    def apply_font_size(self, app: QApplication) -> None:
        """
        Applies the stored application font size.

        A missing key leaves the current font in place.

        :param app: the ``QApplication``
        """
        size = self.font_size()
        if size is None:
            return
        font = QFont()
        font.setPointSize(size)
        app.setFont(font)

    @classmethod
    def reset(cls, store: QSettings | None = None) -> GuiSettings | None:
        """
        Drops the shared instance.

        Pass a store to install another one. Tests use a temporary file so they do not
        write the user preferences.

        :param store: replacement ``QSettings``, or None to leave the singleton unset
        :return:      the new instance, or None when no store is given
        """
        with cls._lock:
            current = cls._instance
            if current is not None and current._store is not None and not sip.isdeleted(current._store):
                current.sync()
            if store is None:
                cls._instance = None
                return None
            instance = super().__new__(cls)
            instance._store = store
            cls._instance = instance
            return instance
