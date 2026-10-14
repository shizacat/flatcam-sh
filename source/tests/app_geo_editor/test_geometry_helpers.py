"""Tests for the geometry helpers at the bottom of the editor module."""

from shapely import Point, Polygon, box

from appEditors.appGeoEditor import distance, get_shapely_list_bounds, mag, poly2rings
from settings.st_types import PointXY


def test_distance_is_the_length_between_two_points() -> None:
    """Verify a 3-4-5 triangle gives a distance of 5."""
    assert distance(PointXY(0, 0), PointXY(3, 4)) == 5


def test_distance_reads_a_plain_pair() -> None:
    """Verify a stored pair of numbers is measured the same way as a point."""
    assert distance((1, 1), (1, 2)) == 1


def test_mag_is_the_length_of_a_vector() -> None:
    """Verify the length of a vector from the origin."""
    assert mag((5, 12)) == 13


def test_poly2rings_keeps_the_exterior_and_then_the_holes() -> None:
    """Verify a polygon with one hole reports the outer ring first."""
    outer = box(0, 0, 10, 10)
    hole = box(2, 2, 4, 4)
    polygon = Polygon(outer.exterior.coords, [hole.exterior.coords])

    rings = poly2rings(polygon)

    assert len(rings) == 2
    assert list(rings[0].coords) == list(polygon.exterior.coords)
    assert list(rings[1].coords) == list(polygon.interiors[0].coords)


def test_bounds_of_several_shapes_cover_every_shape() -> None:
    """Verify the combined bounds reach the outermost coordinates."""
    bounds = get_shapely_list_bounds([box(0, 0, 2, 3), Point(5, 1)])

    assert bounds == [0, 0, 5, 3]


def test_bounds_skip_a_shape_that_has_no_extent() -> None:
    """Verify one unusable shape does not discard the shapes that do have bounds."""
    bounds = get_shapely_list_bounds([object(), box(1, 2, 3, 4)])

    assert bounds == [1, 2, 3, 4]


def test_bounds_of_an_empty_list_stay_unbounded() -> None:
    """Verify no shapes leave the bounds at the unset extremes."""
    xmin, ymin, xmax, ymax = get_shapely_list_bounds([])

    assert xmin > 0 and ymin > 0
    assert xmax < 0 and ymax < 0
