"""Process-wide access to the GUI settings stored by Qt."""

from __future__ import annotations

import threading
from typing import Any, ClassVar, Self

from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QStyleFactory


class GuiSettings:
    """
    Shared handle for ``QSettings("Open Source", "FlatCAM_EVO")``.

    Qt keeps this store outside the FlatConfig file. One instance serves the whole
    process, so a later read sees an earlier write without constructing ``QSettings`` again.

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
                    instance._store = QSettings(cls.organization, cls.application)
                    cls._instance = instance
        return cls._instance

    def contains(self, key: str) -> bool:
        """
        Reports whether a key is present.

        :param key: setting name
        :return:    True when the key has a stored value
        """
        return self._store.contains(key)

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
                return self._store.value(key)
            return self._store.value(key, default)
        if default is None:
            return self._store.value(key, type=value_type)
        return self._store.value(key, default, type=value_type)

    def set_value(self, key: str, value: Any) -> None:
        """
        Stores a value and writes it to the platform store.

        :param key:   setting name
        :param value: value to store
        """
        self._store.setValue(key, value)
        self.sync()

    def remove(self, key: str) -> None:
        """
        Deletes one key and writes the store.

        :param key: setting name
        """
        self._store.remove(key)
        self.sync()

    def keys(self) -> list[str]:
        """
        Lists the stored key names.

        :return: key names
        """
        return list(self._store.allKeys())

    def clear(self) -> None:
        """
        Deletes every key and writes the store.
        """
        self._store.clear()
        self.sync()

    def sync(self) -> None:
        """
        Writes pending values to the platform store.
        """
        self._store.sync()

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

    def style_name(self) -> str | None:
        """
        Returns the style name to show as the current choice.

        The stored name is used when this process provides it. Otherwise the name of
        the style already set on the application is used.

        :return: a name from ``QStyleFactory.keys()``, or None when neither matches
        """
        name = self._stored_style()
        if name is not None:
            return name
        app = QApplication.instance()
        if app is None:
            return None
        return self.resolve_style(app.style().objectName(), QStyleFactory.keys())

    def _stored_style(self) -> str | None:
        """
        Returns the stored style when this process provides it.

        :return: a name from ``QStyleFactory.keys()``, or None
        """
        saved = self.value("style", value_type=str) if self.contains("style") else None
        return self.resolve_style(saved, QStyleFactory.keys())

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

    def apply_font_size(self, app: QApplication) -> None:
        """
        Applies the stored application font size.

        A missing key leaves the current font in place.

        :param app: the ``QApplication``
        """
        if not self.contains("font_size"):
            return
        font = QFont()
        font.setPointSize(int(self.value("font_size", value_type=str)))
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
            if cls._instance is not None:
                cls._instance.sync()
            if store is None:
                cls._instance = None
                return None
            instance = super().__new__(cls)
            instance._store = store
            cls._instance = instance
            return instance
