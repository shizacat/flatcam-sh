"""Tests for snapping a canvas point to the grid or a nearby corner."""

from appEditors.appGeoEditor import AppGeoEditor
from settings.st_types import PointXY
from tests.app_geo_editor.conftest import Stored


class _Storage:
    def __init__(self, nearest=None, error=None):
        self._nearest = nearest
        self._error = error

    def nearest(self, point):
        if self._error is not None:
            raise self._error
        return self._nearest


def _editor(options, linked=False, nearest=None, error=None):
    editor = AppGeoEditor.__new__(AppGeoEditor)
    editor.editor_options = options
    editor.storage = _Storage(nearest, error)
    editor.app = type("App", (), {})()
    editor.app.ui = type("Ui", (), {"grid_gap_link_cb": Stored(linked)})()
    return editor


def test_snap_returns_the_same_point_when_both_snaps_are_off() -> None:
    """Verify a click is left unchanged while the grid and corners are disabled."""
    editor = _editor({"corner_snap": False, "grid_snap": False})

    assert editor.snap(1.2, 3.4) == PointXY(1.2, 3.4)


def test_grid_snap_rounds_to_the_nearest_grid_point() -> None:
    """Verify X and Y land on the linked grid spacing."""
    editor = _editor(
        {"corner_snap": False, "grid_snap": True, "global_gridx": 1, "global_gridy": 1},
        linked=True,
    )

    assert editor.snap(1.4, 2.6) == PointXY(1, 3)


def test_unlinked_grid_uses_a_separate_vertical_spacing() -> None:
    """Verify Y follows its own spacing when the axes are not linked."""
    editor = _editor(
        {"corner_snap": False, "grid_snap": True, "global_gridx": 1, "global_gridy": 0.5},
        linked=False,
    )

    assert editor.snap(1.4, 2.6) == PointXY(1, 2.5)


def test_zero_grid_spacing_leaves_the_coordinate() -> None:
    """Verify a zero spacing does not divide the coordinate."""
    editor = _editor(
        {"corner_snap": False, "grid_snap": True, "global_gridx": 0, "global_gridy": 0},
        linked=False,
    )

    assert editor.snap(1.4, 2.6) == PointXY(1.4, 2.6)


def test_corner_snap_wins_when_it_is_closer_than_the_grid() -> None:
    """Verify a nearby vertex is preferred to a farther grid point."""
    editor = _editor(
        {
            "corner_snap": True,
            "grid_snap": True,
            "global_gridx": 1,
            "global_gridy": 1,
            "global_snap_max": 0.2,
        },
        linked=True,
        nearest=((0.35, 0.0), None),
    )

    assert editor.snap(0.4, 0.0) == PointXY(0.35, 0.0)


def test_grid_snap_is_used_when_the_corner_is_too_far() -> None:
    """Verify a distant vertex is ignored and the grid point is kept."""
    editor = _editor(
        {
            "corner_snap": True,
            "grid_snap": True,
            "global_gridx": 1,
            "global_gridy": 1,
            "global_snap_max": 0.2,
        },
        linked=True,
        nearest=((10.0, 10.0), None),
    )

    assert editor.snap(0.4, 0.0) == PointXY(0.0, 0.0)


def test_missing_corner_falls_back_to_the_grid() -> None:
    """Verify an empty shape index still snaps to the grid."""
    editor = _editor(
        {
            "corner_snap": True,
            "grid_snap": True,
            "global_gridx": 1,
            "global_gridy": 1,
            "global_snap_max": 1,
        },
        linked=True,
        error=StopIteration,
    )

    assert editor.snap(0.4, 0.2) == PointXY(0.0, 0.0)
