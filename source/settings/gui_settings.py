"""Process-wide access to the GUI settings stored by Qt."""

from __future__ import annotations

import threading
from typing import Any, ClassVar, Self

from PyQt6.QtCore import QSettings


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
