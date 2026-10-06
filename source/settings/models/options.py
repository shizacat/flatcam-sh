"""Session options derived from saved application settings."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Self

import darkdetect
from pydantic import ConfigDict, Field

from settings.st_types import Appearance, Theme

from .shared import SHARED
from ..tracking import BaseModelChangeTrack

if TYPE_CHECKING:
    from .settings import Settings


class Options(BaseModelChangeTrack, *SHARED):
    """
    Store the session values used by tools and by the open project.

    Options start from the saved settings and may then diverge.
    A loaded project changes options.
    Changing options does not write the settings file.
    The settings-file version and usage counters stay on settings.
    The session color is resolved from the appearance preference at startup
    and is not stored in the settings file.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    global_theme: Theme = Field(
        default=Theme.LIGHT,
        description="Session color resolved from the appearance preference.",
    )

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        """
        Builds session options from saved settings.

        Nested values are copied, so a later edit stays on the session object.

        :param settings: saved application settings
        :return:         session options
        """
        values = {
            name: getattr(settings, name)
            for name in cls.model_fields
            if name in type(settings).model_fields
        }
        return cls.model_validate(copy.deepcopy(values))

    def theme_from_appearance(self) -> Theme:
        """
        Resolves the session color from ``global_appearance``.

        ``Appearance.SYSTEM`` follows the operating-system color scheme.

        :return: session color, light or dark
        """
        if self.global_appearance is Appearance.DARK:
            return Theme.DARK
        if self.global_appearance is Appearance.LIGHT:
            return Theme.LIGHT
        if darkdetect.isDark():
            return Theme.DARK
        return Theme.LIGHT
