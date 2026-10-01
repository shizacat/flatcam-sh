"""Saved application settings loaded from and written to the settings file."""

import json
import os
from typing import Self

from pydantic import ConfigDict, Field, ValidationError

from exceptions import SettingsError

from .shared import SHARED
from ..tracking import BaseModelChangeTrack


class Settings(BaseModelChangeTrack, *SHARED):
    """
    Store the saved application settings.

    These values are loaded from the settings file and written back when preferences are saved.
    Field defaults are the values assigned when no settings file exists.
    Every setting must declare a default value.
    Session values live on Options and do not write this file by themselves.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

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
            known = {
                name: value
                for name, value in loaded.items()
                if name in cls.model_fields
            }
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
