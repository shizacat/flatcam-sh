"""Tests for the shape wrapper used by every drawing tool."""

from shapely import LineString, Point, Polygon, box

from appEditors.appGeoEditor import DrawToolShape, DrawToolUtilityShape


def test_empty_geometry_has_zero_bounds() -> None:
    """Verify a shape that has not been drawn yet reports an empty extent."""
    assert DrawToolShape(None).bounds() == (0.0, 0.0, 0.0, 0.0)


def test_bounds_follow_the_stored_geometry() -> None:
    """Verify the wrapper reports the extent of its Shapely geometry."""
    assert DrawToolShape(box(1, 2, 4, 6)).bounds() == (1, 2, 4, 6)


def test_bounds_cover_a_nested_list_of_shapes() -> None:
    """Verify bounds walk nested lists instead of stopping at the first group."""
    shape = DrawToolShape([box(0, 0, 1, 1), [box(3, 4, 5, 6)]])

    assert shape.bounds() == (0, 0, 5, 6)


def test_get_pts_returns_nothing_for_a_missing_shape() -> None:
    """Verify a missing object does not invent coordinates."""
    assert DrawToolShape.get_pts(None) is None


def test_get_pts_lists_the_vertices_of_a_line() -> None:
    """Verify a line contributes each of its coordinates."""
    points = DrawToolShape.get_pts(LineString([(0, 0), (2, 0), (2, 3)]))

    assert points == [(0.0, 0.0), (2.0, 0.0), (2.0, 3.0)]


def test_get_pts_includes_a_polygon_hole() -> None:
    """Verify the outer ring and the hole are both collected."""
    polygon = Polygon([(0, 0), (6, 0), (6, 6), (0, 6)], [[(1, 1), (2, 1), (2, 2), (1, 2)]])

    points = DrawToolShape.get_pts(polygon)

    assert (0.0, 0.0) in points
    assert (1.0, 1.0) in points


def test_get_pts_descends_into_a_wrapped_shape() -> None:
    """Verify a DrawToolShape is read through its geometry."""
    wrapped = DrawToolShape(Point(4, 5))

    assert DrawToolShape.get_pts(wrapped) == [(4.0, 5.0)]


def test_get_all_points_uses_the_shape_itself() -> None:
    """Verify the instance method reads the geometry stored on the shape."""
    assert DrawToolShape(Point(1, 2)).get_all_points() == [(1.0, 2.0)]


def test_mirror_across_x_flips_the_vertical_coordinate() -> None:
    """Verify mirroring through the X axis swaps the sign of Y."""
    shape = DrawToolShape(LineString([(0, 1), (2, 3)]))

    shape.mirror("X", (0, 0))

    assert list(shape.geo.coords) == [(0.0, -1.0), (2.0, -3.0)]


def test_mirror_across_y_flips_the_horizontal_coordinate() -> None:
    """Verify mirroring through the Y axis swaps the sign of X."""
    shape = DrawToolShape(Point(3, 1))

    shape.mirror("Y", (0, 0))

    assert shape.geo.x == -3
    assert shape.geo.y == 1


def test_mirror_of_a_list_transforms_each_member() -> None:
    """Verify a group of shapes is mirrored one by one."""
    shape = DrawToolShape([Point(1, 2), Point(3, 4)])

    shape.mirror("X", (0, 0))

    assert [(item.x, item.y) for item in shape.geo] == [(1.0, -2.0), (3.0, -4.0)]


def test_rotate_quarter_turn_around_the_origin() -> None:
    """Verify a positive quarter turn moves a point from the X axis to the Y axis."""
    shape = DrawToolShape(Point(1, 0))

    shape.rotate(90, (0, 0))

    assert shape.geo.x == 0
    assert shape.geo.y == 1


def test_offset_moves_the_shape_by_the_vector() -> None:
    """Verify both coordinates are shifted by the given vector."""
    shape = DrawToolShape(box(0, 0, 1, 1))

    shape.offset((2, 3))

    assert shape.geo.bounds == (2, 3, 3, 4)


def test_offset_ignores_a_single_number() -> None:
    """Verify a vector that is not a pair leaves the shape where it was."""
    shape = DrawToolShape(Point(1, 1))

    shape.offset(5)

    assert (shape.geo.x, shape.geo.y) == (1, 1)


def test_scale_uses_the_same_factor_on_both_axes_when_y_is_omitted() -> None:
    """Verify one factor enlarges X and Y together."""
    shape = DrawToolShape(box(0, 0, 2, 1))

    shape.scale(2)

    assert shape.geo.bounds == (0, 0, 4, 2)


def test_scale_can_use_a_separate_vertical_factor() -> None:
    """Verify X and Y can be enlarged by different amounts."""
    shape = DrawToolShape(box(0, 0, 2, 2))

    shape.scale(2, 3, (0, 0))

    assert shape.geo.bounds == (0, 0, 4, 6)


def test_scale_rejects_a_factor_that_is_not_a_number() -> None:
    """Verify a bad factor does not change the geometry."""
    shape = DrawToolShape(box(0, 0, 1, 1))

    shape.scale("wide")

    assert shape.geo.bounds == (0, 0, 1, 1)


def test_buffer_grows_a_point_into_an_area() -> None:
    """Verify buffering a point produces a disk of that radius."""
    shape = DrawToolShape(Point(0, 0))

    shape.buffer(1, join=1)

    assert shape.geo.area > 3
    minx, miny, maxx, maxy = shape.geo.bounds
    assert minx == -1 and maxx == 1
    assert miny == -1 and maxy == 1


def test_buffer_factor_scales_about_the_center() -> None:
    """Verify the factor path enlarges the shape instead of offsetting its outline."""
    shape = DrawToolShape(box(-1, -1, 1, 1))

    shape.buffer(2, factor=1)

    assert shape.geo.bounds == (-2, -2, 2, 2)


def test_skew_shears_the_top_of_a_square() -> None:
    """Verify a horizontal shear moves the upper edge sideways."""
    shape = DrawToolShape(box(0, 0, 1, 1))

    shape.skew(45, 0, (0, 0))

    assert shape.geo.bounds[2] > 1


def test_utility_shape_is_marked_temporary() -> None:
    """Verify a preview shape is distinguished from a finished one."""
    assert DrawToolShape(Point(0, 0)).utility is False
    assert DrawToolUtilityShape(Point(0, 0)).utility is True
