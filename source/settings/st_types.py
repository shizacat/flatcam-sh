"""Shared annotated types for settings fields."""

from enum import StrEnum
from typing import Annotated

from pydantic import BeforeValidator


class Appearance(StrEnum):
    """Color scheme chosen in Preferences."""

    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


def _color_appearance(value: object) -> object:
    """
    Maps retired appearance names onto the system color scheme.

    ``default`` and ``auto`` were stored before color and widget style were split.

    :param value: stored appearance
    :return:      ``system`` for a retired name, otherwise the original value
    """
    if isinstance(value, str) and value in {"default", "auto"}:
        return Appearance.SYSTEM
    return value


ColorAppearance = Annotated[Appearance, BeforeValidator(_color_appearance)]


class Theme(StrEnum):
    """Session color resolved from the appearance preference."""

    LIGHT = "light"
    DARK = "dark"

    def is_light(self) -> bool:
        """
        Reports whether this color keeps dark text on a light background.

        :return: True for the light color
        """
        return self is Theme.LIGHT


def _xy_pair(value: object) -> object:
    """
    Turns a comma-separated X, Y text into two numbers.

    Lists and tuples of two numbers are returned as a pair.
    Other values are left for validation.

    :param value: stored position
    :return:      pair of numbers, or the original value
    """
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",") if part.strip()]
        if len(parts) != 2:
            return value
        return float(parts[0]), float(parts[1])
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return float(value[0]), float(value[1])
    return value


XYPair = Annotated[tuple[float, float], BeforeValidator(_xy_pair)]


def _tool_diameters(value: object) -> object:
    """
    Turns tool-diameter text into one number or a sequence of numbers.

    A single number stays a float. Several numbers become a tuple.
    Other values are left for validation.

    :param value: stored diameters
    :return:      one diameter, a tuple of diameters, or the original value
    """
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",") if part.strip()]
        if len(parts) == 1:
            return float(parts[0])
        if len(parts) > 1:
            return tuple(float(part) for part in parts)
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, (list, tuple)) and value:
        numbers = tuple(float(part) for part in value)
        if len(numbers) == 1:
            return numbers[0]
        return numbers
    return value


ToolDiameters = Annotated[float | tuple[float, ...], BeforeValidator(_tool_diameters)]
