"""Tests for expanding editor geometry into a flat list."""

from shapely import LineString, MultiLineString, Polygon, box

from appEditors.appGeoEditor import AppGeoEditor


def _editor():
    editor = AppGeoEditor.__new__(AppGeoEditor)
    editor.flat_geo = []
    return editor


def test_flatten_keeps_a_line_as_one_item() -> None:
    """Verify a line is stored without being split."""
    line = LineString([(0, 0), (1, 0)])

    assert _editor().flatten(line) == [line]


def test_flatten_expands_a_list_and_a_multiline() -> None:
    """Verify grouped lines are stored as separate items."""
    first = LineString([(0, 0), (1, 0)])
    second = LineString([(0, 1), (1, 1)])

    flat = _editor().flatten([first, MultiLineString([second, second])])

    assert flat == [first, second, second]


def test_path_only_replaces_a_polygon_with_its_rings() -> None:
    """Verify a filled polygon becomes its exterior and its hole."""
    polygon = Polygon([(0, 0), (4, 0), (4, 4), (0, 4)], [[(1, 1), (2, 1), (2, 2), (1, 2)]])

    flat = _editor().flatten(polygon, pathonly=True)

    assert len(flat) == 2
    assert flat[0].geom_type == "LinearRing"
    assert flat[1].geom_type == "LinearRing"


def test_flatten_can_append_to_geometry_already_collected() -> None:
    """Verify a later call keeps what an earlier call stored."""
    editor = _editor()
    first = box(0, 0, 1, 1)
    second = box(2, 2, 3, 3)

    editor.flatten(first)
    editor.flatten(second, reset=False)

    assert editor.flat_geo == [first, second]
