"""Tests for the vertex index and the geometry storage built on it."""

import sys
from pathlib import Path

import pytest
from shapely import LinearRing, LineString, Polygon

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from camlib import AppRTree, AppRTreeStorage
from settings.st_types import PointXY


def test_insert_records_each_vertex_under_its_object() -> None:
    """Verify one rtree entry per vertex and the reverse link back to the object."""
    index = AppRTree()

    index.insert(0, LineString([(0, 0), (2, 0)]))

    assert index.obj2points == [[0, 1]]
    assert index.points2obj == [0, 0]


def test_insert_grows_the_object_list_up_to_the_given_id() -> None:
    """Verify an object id past the end leaves empty slots for the missing ids."""
    index = AppRTree()

    index.insert(2, LineString([(1, 1), (2, 2)]))

    assert index.obj2points[0] == []
    assert index.obj2points[1] == []
    assert index.obj2points[2] == [0, 1]
    assert index.points2obj == [2, 2]


def test_nearest_returns_the_closest_vertex() -> None:
    """Verify the query point selects the vertex stored nearest to it."""
    index = AppRTree()
    index.insert(0, LineString([(0, 0), (10, 0)]))
    index.insert(1, LineString([(0, 5), (1, 5)]))

    item = index.nearest((0.2, 0.1))

    assert item.object == 0
    assert (item.bbox[0], item.bbox[1]) == (0.0, 0.0)


def test_nearest_accepts_a_named_point() -> None:
    """Verify a PointXY query uses the same vertex lookup as a pair."""
    index = AppRTree()
    index.insert(0, LineString([(4, 5), (8, 5)]))

    item = index.nearest(PointXY(4.1, 5.2))

    assert item.object == 0
    assert (item.bbox[0], item.bbox[1]) == (4.0, 5.0)


def test_nearest_on_an_empty_index_stops() -> None:
    """Verify a query with nothing indexed reports that the search is exhausted."""
    with pytest.raises(StopIteration):
        AppRTree().nearest((0, 0))


def test_intersection_returns_the_vertex_at_the_query() -> None:
    """Verify a query on a stored vertex returns the object that owns it."""
    index = AppRTree()
    index.insert(3, LineString([(1, 2), (8, 9)]))

    item = index.intersection((8, 9))

    assert item.object == 3
    assert (item.bbox[0], item.bbox[1]) == (8.0, 9.0)


def test_intersection_miss_stops() -> None:
    """Verify a query that touches no vertex reports that the search is exhausted."""
    index = AppRTree()
    index.insert(0, LineString([(0, 0), (1, 0)]))

    with pytest.raises(StopIteration):
        index.intersection((5, 5))


def test_remove_obj_drops_the_vertices_from_the_index() -> None:
    """Verify a removed object's vertices are no longer found."""
    index = AppRTree()
    line = LineString([(0, 0), (1, 0)])
    index.insert(0, line)

    index.remove_obj(0, line)

    with pytest.raises(StopIteration):
        index.nearest((0, 0))


def test_custom_get_points_indexes_only_the_returned_vertices() -> None:
    """Verify the point hook decides which vertices enter the index."""
    index = AppRTree()
    index.get_points = lambda line: [line.coords[0], line.coords[-1]]
    index.insert(0, LineString([(0, 0), (10, 0), (20, 0)]))

    assert len(index.obj2points[0]) == 2
    with pytest.raises(StopIteration):
        index.intersection((10, 0))


def test_storage_nearest_returns_the_stored_object() -> None:
    """Verify the storage hands back the object that owns the nearest vertex."""
    storage = AppRTreeStorage()
    line = LineString([(0, 0), (5, 0)])
    other = LineString([(0, 4), (1, 4)])
    storage.insert(line)
    storage.insert(other)

    point, owner = storage.nearest((0.2, 0.1))

    assert owner is line
    assert point == (0.0, 0.0)
    assert list(storage.get_objects()) == [line, other]


def test_storage_remove_leaves_a_hole_and_keeps_the_other_object() -> None:
    """Verify removal clears the slot without shifting the objects that remain."""
    storage = AppRTreeStorage()
    first = LineString([(0, 0), (1, 0)])
    second = LineString([(0, 3), (1, 3)])
    storage.insert(first)
    storage.insert(second)

    storage.remove(first)

    assert storage.objects[0] is None
    assert storage.objects[1] is second
    assert list(storage.get_objects()) == [second]
    point, owner = storage.nearest((0, 0))
    assert owner is second
    assert point == (0.0, 3.0)


def test_storage_nearest_on_an_empty_storage_stops() -> None:
    """Verify a query with no stored geometry reports that the search is exhausted."""
    with pytest.raises(StopIteration):
        AppRTreeStorage().nearest((0, 0))


def test_remove_leaves_the_id_maps_in_place() -> None:
    """Verify one removal drops the geometry but keeps the id maps that pointed at it."""
    storage = AppRTreeStorage()
    line = LineString([(0, 0), (1, 0)])
    storage.insert(line)

    storage.remove(line)

    assert storage.indexes[id(line)] == 0
    assert storage.objects[0] is None
    assert storage.obj2points[0] == [0, 1]
    assert storage.points2obj == [0, 0]
    assert list(storage.get_objects()) == []


def test_default_hook_indexes_every_coordinate_of_a_ring() -> None:
    """Verify a polygon outline is stored through its ring, including the repeated closing vertex."""
    index = AppRTree()
    ring = LinearRing([(0, 0), (2, 0), (1, 1)])

    index.insert(0, ring)

    assert index.points2obj == [0, 0, 0, 0]
    assert index.intersection((0, 0)).object == 0


def test_default_hook_rejects_a_polygon() -> None:
    """Verify a polygon has no coordinate sequence, so the default hook cannot index it."""
    index = AppRTree()

    with pytest.raises(NotImplementedError):
        index.insert(0, Polygon([(0, 0), (4, 0), (4, 3), (0, 3)]))


def test_polygon_hook_indexes_the_outer_ring_and_the_hole() -> None:
    """Verify a caller-supplied hook can index both rings of a polygon."""
    polygon = Polygon([(0, 0), (6, 0), (6, 6), (0, 6)], [[(1, 1), (2, 1), (2, 2), (1, 2)]])
    storage = AppRTreeStorage()
    storage.get_points = lambda geom: list(geom.exterior.coords) + [
        point for hole in geom.interiors for point in hole.coords
    ]

    storage.insert(polygon)

    outer = storage.intersection((0, 0))
    hole = storage.intersection((1, 1))
    assert storage.objects[outer.object] is polygon
    assert storage.objects[hole.object] is polygon
