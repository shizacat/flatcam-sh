"""Tests for the arc tool modes in the geometry editor."""

from types import SimpleNamespace

import pytest
from shapely import Point

from appEditors.appGeoEditor import FCArc
from settings.st_types import PointXY
from tests.app_geo_editor.conftest import bare


class _Signal:
    def __init__(self):
        self.connected = 0
        self.disconnected = 0

    def connect(self, slot):
        self.connected += 1

    def disconnect(self, slot=None):
        self.disconnected += 1


class _Inform:
    def __init__(self):
        self.messages = []

    def emit(self, message):
        self.messages.append(message)


def _arc(mode="c12", direction="cw"):
    signal = _Signal()
    inform = _Inform()
    tool = bare(
        FCArc,
        points=[],
        mode=mode,
        direction=direction,
        steps_per_circ=16,
        draw_app=SimpleNamespace(
            app=SimpleNamespace(jump_signal=signal, inform=inform),
            delete_utility_geometry=lambda: None,
        ),
    )
    return tool


def test_one_point_shows_the_radius_line() -> None:
    """Verify the first click draws a line from the center to the cursor."""
    tool = _arc()
    tool.points = [PointXY(0, 0)]

    preview = tool.utility_geometry(PointXY(3, 0))

    assert list(preview.geo.coords) == [(0.0, 0.0), (3.0, 0.0)]


def test_center_mode_draws_the_arc_between_the_two_radii() -> None:
    """Verify a counter-clockwise center arc is the short quarter between the radii."""
    tool = _arc(direction="ccw")
    tool.points = [PointXY(0, 0), PointXY(1, 0)]

    preview = tool.utility_geometry(PointXY(0, 1))
    arc_line, center = preview.geo

    assert arc_line.geom_type == "LineString"
    assert center.equals(Point(0, 0))
    assert arc_line.length == pytest.approx(1.57079632679, abs=0.05)


def test_clockwise_center_arc_takes_the_long_way() -> None:
    """Verify a clockwise center arc runs the long way around the circle."""
    tool = _arc(direction="cw")
    tool.points = [PointXY(0, 0), PointXY(1, 0)]

    preview = tool.utility_geometry(PointXY(0, 1))

    assert preview.geo[0].length == pytest.approx(4.71238898038, abs=0.05)


def test_three_point_mode_finds_the_circle_through_the_points() -> None:
    """Verify the 1-3-2 mode places the center of the circle through the three points."""
    tool = _arc(mode="132")
    tool.points = [PointXY(0, 0), PointXY(0, 2)]

    preview = tool.utility_geometry(PointXY(2, 0))
    center = preview.geo[1]

    assert abs(center.x - 1) < 1e-6
    assert abs(center.y - 1) < 1e-6


def test_start_stop_center_mode_uses_the_cursor_as_the_center() -> None:
    """Verify the third mode puts the arc center on the cursor."""
    tool = _arc(mode="12c")
    tool.points = [PointXY(0, 0), PointXY(2, 0)]

    preview = tool.utility_geometry(PointXY(1, 1))

    assert abs(preview.geo[1].x - 1) < 1e-6
    assert abs(preview.geo[1].y - 1) < 1e-6


def test_direction_key_switches_between_clockwise_and_back() -> None:
    """Verify the D key flips the arc direction and reports the new one."""
    tool = _arc(direction="cw")

    first = tool.on_key("D")
    second = tool.on_key("D")

    assert tool.direction == "cw"
    assert first.endswith("CCW")
    assert second.split(": ")[-1] == "CW"


def test_mode_key_cycles_the_click_order() -> None:
    """Verify the M key walks through the three arc construction modes."""
    tool = _arc(mode="c12")

    tool.on_key("M")
    assert tool.mode == "12c"
    tool.on_key("M")
    assert tool.mode == "132"
    tool.on_key("M")
    assert tool.mode == "c12"


def test_third_click_finishes_a_center_arc() -> None:
    """Verify the third click stores the arc and marks the tool complete."""
    tool = _arc()

    assert "1st" in tool.click(PointXY(0, 0))
    assert "2nd" in tool.click(PointXY(1, 0))
    assert tool.click(PointXY(0, 1)) == "Done."
    assert tool.complete is True
    assert tool.geometry.data["type"] == "Arc"
    assert tool.geometry.geo.geom_type == "LineString"
    assert tool.draw_app.app.jump_signal.disconnected == 4
