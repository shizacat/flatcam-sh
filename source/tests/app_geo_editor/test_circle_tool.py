"""Tests for the circle and ellipse preview in the geometry editor."""

from types import SimpleNamespace

from shapely import Point

from appEditors.appGeoEditor import FCCircle
from settings.st_types import PointXY
from tests.app_geo_editor.conftest import Stored, bare


def _circle(linked=True):
    tool = bare(
        FCCircle,
        points=[],
        steps_per_circ=8,
        cursor_data_control=True,
        ui=SimpleNamespace(
            radius_link_btn=Stored(linked),
            radius_x_entry=Stored(),
            radius_y_entry=Stored(),
            angle_entry=Stored(),
        ),
    )
    return tool


def test_circle_preview_uses_the_distance_to_the_cursor() -> None:
    """Verify the preview disk reaches from the center to the cursor."""
    tool = _circle()
    tool.points = [PointXY(0, 0)]

    preview = tool.utility_geometry(PointXY(3, 4))

    assert tool.ui.radius_x_entry.get_value() == 5
    assert preview.geo.equals(Point(0, 0).buffer(5, 8))


def test_circle_preview_waits_for_the_center() -> None:
    """Verify no disk is drawn before the first click."""
    assert _circle().utility_geometry(PointXY(1, 1)) is None


def test_ellipse_preview_sets_the_angle_and_caps_the_short_axis() -> None:
    """Verify a long first radius keeps the short axis at its upper limit."""
    tool = _circle(linked=False)
    tool.points = [PointXY(0, 0)]

    preview = tool.utility_geometry(PointXY(10, 0))

    assert tool.ui.angle_entry.get_value() == 0
    assert tool.ui.radius_x_entry.get_value() == 10
    assert tool.ui.radius_y_entry.get_value() == 3
    assert preview.geo.bounds[2] == 10
    assert preview.geo.bounds[3] == 3


def test_ellipse_second_click_replaces_the_short_axis() -> None:
    """Verify the second perimeter click sets the minor radius from the cursor."""
    tool = _circle(linked=False)
    tool.points = [PointXY(0, 0), PointXY(4, 0)]
    tool.ui.angle_entry.set_value(0)
    tool.ui.radius_x_entry.set_value(4)

    preview = tool.utility_geometry(PointXY(0, 2))

    assert tool.ui.radius_y_entry.get_value() == 2
    minx, miny, maxx, maxy = preview.geo.bounds
    assert (minx, miny, maxx, maxy) == (-4, -2, 4, 2)


def test_cursor_readout_is_cleared_when_it_is_switched_off() -> None:
    """Verify the coordinate text is removed while the readout is disabled."""
    tool = _circle()
    tool.cursor_data_control = False
    text_cursor = SimpleNamespace(text="X")
    tool.draw_app = SimpleNamespace(app=SimpleNamespace(plotcanvas=SimpleNamespace(text_cursor=text_cursor)))

    tool.draw_cursor_data(PointXY(1, 1))

    assert text_cursor.text == ""
