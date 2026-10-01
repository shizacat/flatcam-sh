"""Session options derived from saved application settings."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Self

from pydantic import ConfigDict

from .shared import SHARED
from ..tracking import BaseModelChangeTrack

if TYPE_CHECKING:
    from .settings import Settings


class Options(BaseModelChangeTrack, *SHARED):
    """
    Store the session values used by tools and by the open project.

    Options start from the saved settings and may then diverge.
    A theme choice or a loaded project changes options.
    Changing options does not write the settings file.
    The settings-file version and usage counters stay on settings.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

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
