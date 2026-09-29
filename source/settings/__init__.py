"""Saved application settings loaded from and written to the settings file."""

import json
import os
from collections.abc import Callable
from typing import Self

from pydantic import ConfigDict, Field, PrivateAttr, ValidationError

from exceptions import SettingsError

from .options import Options
from .shared import SHARED

__all__ = ["Options", "Settings"]


class Settings(*SHARED):
    """
    Store the saved application settings.

    These values are loaded from the settings file and written back when preferences are saved.
    Field defaults are the values assigned when no settings file exists.
    Every setting must declare a default value.
    Session values live on Options and do not write this file by themselves.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    _change_callbacks: list[Callable[[str], None]] = PrivateAttr(default_factory=list)

    version: str = Field(default="8.992", description="Settings data-format version.")
    global_stats: dict[str, int] = Field(
        default_factory=dict,
        description="Application usage counters keyed by statistic name.",
    )

    @classmethod
    def load(cls, filename: str | os.PathLike[str]) -> Self:
        """
        Loads settings from a JSON file.

        Keys absent from the file keep their default values.

        :param filename:        path to the JSON settings file

        :return:                validated settings

        :raises SettingsError:  the file could not be read or does not contain valid settings
        """
        try:
            with open(filename, encoding="utf-8") as settings_file:
                loaded = json.loads(settings_file.read())
            if not isinstance(loaded, dict):
                raise SettingsError(f"Could not load settings from {filename}.")
            known = {name: value for name, value in loaded.items() if name in cls.model_fields}
            return cls.model_validate(known)
        except SettingsError:
            raise
        except (OSError, ValidationError, ValueError) as error:
            raise SettingsError(f"Could not load settings from {filename}.") from error

    def write(self, filename: str | os.PathLike[str]) -> None:
        """
        Writes the settings to a JSON file.

        :param filename:        path to the JSON settings file

        :raises SettingsError:  the file could not be written
        """
        try:
            with open(filename, "w", encoding="utf-8") as settings_file:
                json.dump(self.model_dump(), settings_file, indent=2, sort_keys=True)
        except (OSError, TypeError, ValueError) as error:
            raise SettingsError(f"Could not write settings to {filename}.") from error

    def report_usage(self, resource: str) -> None:
        """
        Increments the usage counter for a resource.

        :param resource: name of the resource
        """
        if resource in self.global_stats:
            self.global_stats[resource] += 1
        else:
            self.global_stats[resource] = 1

    def bind(self, callback: Callable[[str], None]) -> None:
        """
        Binds a callback invoked when a setting value changes.

        The callback receives the name of the changed setting. Assigning the current value does not call it.

        :param callback: function called with the changed setting name
        """
        self._change_callbacks.append(callback)

    def unbind(self, callback: Callable[[str], None]) -> None:
        """
        Removes a callback previously bound with bind.

        :param callback:        function previously passed to bind

        :raises SettingsError:  the callback is not bound
        """
        try:
            self._change_callbacks.remove(callback)
        except ValueError as error:
            raise SettingsError("Callback is not bound.") from error

    def __setattr__(self, name: str, value: object) -> None:
        """
        Sets an attribute and notifies bound callbacks when a setting changes.

        :param name:  attribute name
        :param value: attribute value
        """
        if name in type(self).model_fields and name in self.__dict__:
            previous = self.__dict__[name]
            super().__setattr__(name, value)
            if previous != self.__dict__[name]:
                for callback in tuple(self._change_callbacks):
                    callback(name)
            return

        super().__setattr__(name, value)
