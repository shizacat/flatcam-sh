"""Tests for the rectangle preview in the geometry editor."""

from types import SimpleNamespace

from shapely import box

from appEditors.appGeoEditor import FCRectangle
from settings.st_types import PointXY
from tests.app_geo_editor.conftest import Stored, bare


def _rectangle(corner="s", radius=0.0, steps=8):
    tool = bare(
        FCRectangle,
        points=[PointXY(0, 0)],
        cursor_data_control=True,
        rect_tool=SimpleNamespace(
            ui=SimpleNamespace(
                corner_radio=Stored(corner),
                radius_entry=Stored(radius),
            )
        ),
        draw_app=SimpleNamespace(
            snap_pos=PointXY(0, 0),
            app=SimpleNamespace(options=SimpleNamespace(geometry_circle_steps=steps)),
        ),
    )
    return tool


def test_square_corners_follow_the_two_clicks() -> None:
    """Verify a rectangle with square corners is the box between the two points."""
    preview = _rectangle().utility_geometry(PointXY(4, 2))

    assert list(preview.geo.coords)[0] == (0.0, 0.0)
    assert preview.geo.bounds == (0.0, 0.0, 4.0, 2.0)


def test_zero_radius_forces_square_corners() -> None:
    """Verify a corner radius of zero draws a square corner even when round was selected."""
    preview = _rectangle(corner="r", radius=0.0).utility_geometry(PointXY(4, 2))

    assert preview.geo.bounds == (0.0, 0.0, 4.0, 2.0)
    assert len(list(preview.geo.coords)) == 5


def test_round_corners_keep_the_outer_size() -> None:
    """Verify a rounded rectangle still reaches the two clicked corners."""
    preview = _rectangle(corner="r", radius=0.5).utility_geometry(PointXY(4, 2))

    assert preview.geo.bounds == (0.0, 0.0, 4.0, 2.0)


def test_a_radius_larger_than_the_side_falls_back_to_square_corners() -> None:
    """Verify the rectangle stays square when the radius no longer fits."""
    preview = _rectangle(corner="r", radius=3.0).utility_geometry(PointXY(4, 2))

    assert len(list(preview.geo.coords)) == 5


def test_rectangle_preview_waits_for_the_first_corner() -> None:
    """Verify no rectangle is drawn before the first click."""
    tool = _rectangle()
    tool.points = []

    assert tool.utility_geometry(PointXY(1, 1)) is None


def test_deleting_the_cursor_detaches_the_readout() -> None:
    """Verify the 3D cursor text is removed when the tool finishes."""
    tool = _rectangle()
    text_cursor = SimpleNamespace(text="X", parent="scene")
    camera = SimpleNamespace(zoom_callback=tool.draw_cursor_data)
    tool.draw_app.app.use_3d_engine = True
    tool.draw_app.app.plotcanvas = SimpleNamespace(
        text_cursor=text_cursor,
        view=SimpleNamespace(camera=camera),
    )

    tool.draw_cursor_data(delete=True)

    assert text_cursor.parent is None
    assert camera.zoom_callback(1, 2) is None
