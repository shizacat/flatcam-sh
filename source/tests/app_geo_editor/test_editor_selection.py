"""Tests for editor selection and the live preview hook."""

from types import SimpleNamespace

import pytest
from PyQt6 import QtWidgets
from shapely import LineString, Point

from appEditors.appGeoEditor import AppGeoEditor, DrawTool, DrawToolShape, DrawToolUtilityShape
from settings.st_types import PointXY


@pytest.fixture
def qapplication() -> QtWidgets.QApplication:
    """Provides one QApplication so the geometry table can be built in a test."""
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def _line(y: float) -> DrawToolShape:
    return DrawToolShape(LineString([(0, y), (1, y)]))


def _table_for(shapes: list[DrawToolShape]) -> tuple[QtWidgets.QTreeWidget, QtWidgets.QTreeWidgetItem]:
    tree = QtWidgets.QTreeWidget()
    tree.setColumnCount(3)
    tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
    tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
    parent = tree.invisibleRootItem()
    for shape in shapes:
        QtWidgets.QTreeWidgetItem(parent, [str(id(shape)), "Line", "Geo Elem"])
    return tree, parent


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


def test_delete_drops_the_selected_table_row(qapplication) -> None:
    """Verify deletion removes the selected row and leaves the table otherwise intact."""
    keep = _line(0)
    drop = _line(1)
    editor = AppGeoEditor.__new__(AppGeoEditor)
    editor.storage = AppGeoEditor.make_storage()
    editor.utility = []
    editor.selected = []
    editor.storage.insert(keep)
    editor.storage.insert(drop)
    tree, parent = _table_for([keep, drop])
    tree.topLevelItem(1).setSelected(True)
    editor.ui = SimpleNamespace(tw=tree, geo_parent=parent)
    rebuilt = []
    editor.build_ui = lambda: rebuilt.append(True)
    editor.plot_all = lambda: None
    editor.on_tree_selection = lambda: None

    editor.delete_selected()

    assert rebuilt == []
    assert list(editor.storage.get_objects()) == [keep]
    assert tree.topLevelItemCount() == 1
    assert tree.topLevelItem(0).text(0) == str(id(keep))
    assert editor.selected == []


def test_delete_removes_a_row_chosen_only_in_storage_selection(qapplication) -> None:
    """Verify a shape kept in self.selected loses its row even when the row is not selected."""
    keep = _line(0)
    drop = _line(1)
    editor = AppGeoEditor.__new__(AppGeoEditor)
    editor.storage = AppGeoEditor.make_storage()
    editor.utility = []
    editor.selected = [drop]
    editor.storage.insert(keep)
    editor.storage.insert(drop)
    tree, parent = _table_for([keep, drop])
    editor.ui = SimpleNamespace(tw=tree, geo_parent=parent)
    editor.plot_all = lambda: None
    editor.on_tree_selection = lambda: None

    editor.delete_selected()

    assert list(editor.storage.get_objects()) == [keep]
    assert tree.topLevelItemCount() == 1
    assert tree.topLevelItem(0).text(0) == str(id(keep))


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
