"""Tests for editor selection and the live preview hook."""

from types import SimpleNamespace

from shapely import Point

from appEditors.appGeoEditor import AppGeoEditor, DrawTool, DrawToolShape, DrawToolUtilityShape
from settings.st_types import PointXY


def test_selecting_a_shape_moves_it_to_the_end() -> None:
    """Verify selecting an item again makes it the last selected shape."""
    editor = AppGeoEditor.__new__(AppGeoEditor)
    editor.selected = []
    first = DrawToolShape(Point(0, 0))
    second = DrawToolShape(Point(1, 1))

    editor.set_selected(first)
    editor.set_selected(second)
    editor.set_selected(first)

    assert editor.get_selected() == [second, first]


def test_unselect_removes_only_that_shape() -> None:
    """Verify clearing one shape leaves the rest of the selection."""
    editor = AppGeoEditor.__new__(AppGeoEditor)
    first = DrawToolShape(Point(0, 0))
    second = DrawToolShape(Point(1, 1))
    editor.selected = [first, second]

    editor.set_unselected(first)

    assert editor.get_selected() == [second]


def test_unselect_ignores_a_shape_that_is_not_selected() -> None:
    """Verify removing a missing shape leaves the selection unchanged."""
    editor = AppGeoEditor.__new__(AppGeoEditor)
    kept = DrawToolShape(Point(0, 0))
    editor.selected = [kept]

    editor.set_unselected(DrawToolShape(Point(1, 1)))

    assert editor.get_selected() == [kept]


def test_utility_hook_turns_a_pair_into_a_point() -> None:
    """Verify a jump location stored as a pair reaches the tool as a point."""
    editor = AppGeoEditor.__new__(AppGeoEditor)
    seen = {}

    def utility_geometry(data=None):
        seen["data"] = data
        return DrawToolUtilityShape(None)

    editor.active_tool = SimpleNamespace(utility_geometry=utility_geometry)

    editor.update_utility_geometry((1.5, 2.5))

    assert seen["data"] == PointXY(1.5, 2.5)


def test_utility_hook_keeps_a_point_that_is_already_named() -> None:
    """Verify a point passed to the preview is not rebuilt."""
    editor = AppGeoEditor.__new__(AppGeoEditor)
    seen = {}
    point = PointXY(1, 2)

    def utility_geometry(data=None):
        seen["data"] = data
        return None

    editor.active_tool = SimpleNamespace(utility_geometry=utility_geometry)

    editor.update_utility_geometry(point)

    assert seen["data"] is point


def test_base_tool_click_does_nothing() -> None:
    """Verify the empty tool reports no geometry and no click result."""
    tool = DrawTool(draw_app=None)

    assert tool.click(PointXY(0, 0)) == ""
    assert tool.click_release(PointXY(0, 0)) == ""
    assert tool.utility_geometry(PointXY(0, 0)) is None
    assert tool.points == []


def test_jump_key_asks_the_application_for_a_coordinate() -> None:
    """Verify the J key opens the jump-to dialog."""
    opened = []
    tool = DrawTool(draw_app=SimpleNamespace(app=SimpleNamespace(on_jump_to=lambda: opened.append(True))))

    tool.on_key("J")

    assert opened == [True]
