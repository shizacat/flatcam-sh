"""Shared annotated types for settings fields."""

from __future__ import annotations

import math
from enum import StrEnum
from typing import Annotated, NamedTuple

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


class PointXY(NamedTuple):
    """
    A point on the plane: X then Y, in project units.

    ``x`` and ``y`` name the two coordinates. Index 0 and index 1 are the same numbers.
    Adding or subtracting two points returns another point. Multiplying or dividing by a
    number scales both coordinates. ``abs(point)`` is the distance from the origin.
    """

    x: float
    y: float

    def __add__(self, other: PointXY) -> PointXY:
        """
        Adds the coordinates of another point.

        :param other: point to add
        :return:      sum of the coordinates
        """
        return PointXY(self.x + other.x, self.y + other.y)

    def __sub__(self, other: PointXY) -> PointXY:
        """
        Subtracts the coordinates of another point.

        :param other: point to subtract
        :return:      difference of the coordinates
        """
        return PointXY(self.x - other.x, self.y - other.y)

    def __mul__(self, scale: float) -> PointXY:
        """
        Scales both coordinates by a number.

        :param scale: multiplier
        :return:      scaled point
        """
        return PointXY(self.x * scale, self.y * scale)

    def __rmul__(self, scale: float) -> PointXY:
        """
        Scales both coordinates by a number written on the left.

        :param scale: multiplier
        :return:      scaled point
        """
        return self * scale

    def __truediv__(self, scale: float) -> PointXY:
        """
        Divides both coordinates by a number.

        :param scale: divisor
        :return:      scaled point
        """
        return PointXY(self.x / scale, self.y / scale)

    def __abs__(self) -> float:
        """
        Measures the distance from the origin.

        :return: length of the point as a vector
        """
        return math.hypot(self.x, self.y)


def _xy_pair(value: object) -> object:
    """
    Turns a stored point into a :class:`PointXY`.

    Comma-separated X, Y text, and a list or tuple of two numbers, become that point.
    Other values are left for validation.

    :param value: stored position
    :return:      point, or the original value
    """
    if isinstance(value, PointXY):
        return value
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",") if part.strip()]
        if len(parts) != 2:
            return value
        return PointXY(float(parts[0]), float(parts[1]))
    if isinstance(value, (list, tuple)) and len(value) == 2:
        return PointXY(float(value[0]), float(value[1]))
    return value


# Same point as PointXY, read from settings or the tools database.
# Both name a point and may be merged later.
XYPair = Annotated[PointXY, BeforeValidator(_xy_pair)]


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
