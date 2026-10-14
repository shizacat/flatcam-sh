"""Tests for moving a selection in the geometry editor."""

from types import SimpleNamespace

from shapely import box

from appEditors.appGeoEditor import DrawToolShape, FCMove
from settings.st_types import PointXY
from tests.app_geo_editor.conftest import bare


def _move(selected, origin=PointXY(0, 0), sel_limit=10, selection_shape=None):
    draw_app = SimpleNamespace(
        selected=list(selected),
        get_selected=lambda: draw_app.selected,
        select_tool=lambda name: selected_calls.append(name),
    )
    tool = bare(
        FCMove,
        origin=origin,
        sel_limit=sel_limit,
        selection_shape=selection_shape,
        draw_app=draw_app,
    )
    return tool, draw_app


selected_calls = []


def test_move_preview_waits_for_an_origin() -> None:
    """Verify nothing is drawn before the move origin is chosen."""
    tool, _draw_app = _move([DrawToolShape(box(0, 0, 1, 1))], origin=None)

    assert tool.utility_geometry(PointXY(1, 1)) is None


def test_move_preview_waits_for_a_selection() -> None:
    """Verify an origin without selected shapes draws nothing."""
    tool, _draw_app = _move([])

    assert tool.utility_geometry(PointXY(1, 1)) is None


def test_move_preview_shifts_each_selected_shape() -> None:
    """Verify a small selection is translated by the cursor offset from the origin."""
    shape = DrawToolShape(box(0, 0, 1, 1))
    tool, _draw_app = _move([shape])

    preview = tool.utility_geometry(PointXY(2, 3))

    assert preview.geo[0].bounds == (2.0, 3.0, 3.0, 4.0)
    assert shape.geo.bounds == (0.0, 0.0, 1.0, 1.0)


def test_large_selection_moves_the_bounding_shape() -> None:
    """Verify a selection past the limit is previewed as one translated outline."""
    tool, _draw_app = _move(
        [DrawToolShape(box(0, 0, 1, 1))],
        sel_limit=0,
        selection_shape=box(0, 0, 4, 1),
    )

    preview = tool.utility_geometry(PointXY(1, 0))

    assert preview.geo.bounds == (1.0, 0.0, 5.0, 1.0)


def test_a_shape_without_geometry_cancels_the_move() -> None:
    """Verify a broken selection returns the editor to the select tool."""
    selected_calls.clear()
    tool, draw_app = _move([SimpleNamespace()])

    assert tool.utility_geometry(PointXY(1, 1)) is None
    assert selected_calls == ["select"]
    assert draw_app.selected == []


def test_selection_bbox_covers_every_selected_shape() -> None:
    """Verify the move outline reaches the outermost selected geometry."""
    tool, _draw_app = _move([DrawToolShape(box(0, 0, 1, 2)), DrawToolShape(box(3, 1, 4, 1.5))])

    assert tool.selection_bbox().bounds == (0.0, 0.0, 4.0, 2.0)
