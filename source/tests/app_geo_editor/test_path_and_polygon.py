"""Tests for the open path and closed polygon previews."""

from types import SimpleNamespace

import pytest

from appEditors.appGeoEditor import FCPath, FCPolygon
from settings.st_types import PointXY
from tests.app_geo_editor.conftest import bare


class _Signal:
    def disconnect(self, slot=None):
        return None


class _Inform:
    def emit(self, message):
        return None


def _no_modifier(monkeypatch):
    from PyQt6.QtCore import Qt

    from appEditors import appGeoEditor

    monkeypatch.setattr(
        appGeoEditor.QtWidgets.QApplication,
        "keyboardModifiers",
        staticmethod(lambda: Qt.KeyboardModifier.NoModifier),
    )


def _shift(monkeypatch):
    from PyQt6.QtCore import Qt

    from appEditors import appGeoEditor

    monkeypatch.setattr(
        appGeoEditor.QtWidgets.QApplication,
        "keyboardModifiers",
        staticmethod(lambda: Qt.KeyboardModifier.ShiftModifier),
    )


def test_path_preview_is_a_line_through_the_clicked_points(monkeypatch) -> None:
    """Verify the path preview follows the clicks and the current cursor."""
    _no_modifier(monkeypatch)
    tool = bare(FCPath, points=[PointXY(0, 0), PointXY(1, 0)])

    preview = tool.utility_geometry(PointXY(1, 2))

    assert preview.geo.geom_type == "LineString"
    assert list(preview.geo.coords) == [(0.0, 0.0), (1.0, 0.0), (1.0, 2.0)]


def test_path_preview_waits_for_the_first_point(monkeypatch) -> None:
    """Verify no path is drawn before the first click."""
    _no_modifier(monkeypatch)

    assert bare(FCPath, points=[]).utility_geometry(PointXY(1, 1)) is None


def test_shift_holds_a_nearly_horizontal_segment(monkeypatch) -> None:
    """Verify Shift keeps a shallow segment on the horizontal through the last point."""
    _shift(monkeypatch)
    tool = bare(FCPath, points=[PointXY(0, 1)])

    preview = tool.utility_geometry(PointXY(5, 1.2))

    assert list(preview.geo.coords)[-1] == (5.0, 1.0)


def test_shift_holds_a_nearly_vertical_segment(monkeypatch) -> None:
    """Verify Shift keeps a steep segment on the vertical through the last point."""
    _shift(monkeypatch)
    tool = bare(FCPath, points=[PointXY(2, 0)])

    preview = tool.utility_geometry(PointXY(2.2, 4))

    assert list(preview.geo.coords)[-1] == (2.0, 4.0)


def test_shift_snaps_a_diagonal_segment_to_45_degrees(monkeypatch) -> None:
    """Verify Shift pulls a near-diagonal segment onto the 45 degree line."""
    _shift(monkeypatch)
    tool = bare(FCPath, points=[PointXY(0, 0)])

    preview = tool.utility_geometry(PointXY(2, 2.2))
    end_x, end_y = list(preview.geo.coords)[-1]

    assert end_x == pytest.approx(end_y)


def test_closest_45_degree_point_stays_on_the_axis_when_that_is_nearer() -> None:
    """Verify a shallow vector is projected onto the horizontal axis."""
    end_x, end_y = FCPath.closest_point_to_45_degrees(PointXY(1, 1), PointXY(4, 2))

    assert end_y == pytest.approx(1)
    assert end_x == pytest.approx(1 + (3 ** 2 + 1 ** 2) ** 0.5)


def test_closest_45_degree_point_keeps_an_exact_diagonal() -> None:
    """Verify a vector that is already at 45 degrees is left in place."""
    assert FCPath.closest_point_to_45_degrees(PointXY(0, 0), PointXY(2, 2)) == pytest.approx((2, 2))


def test_update_angle_reports_the_absolute_direction() -> None:
    """Verify the segment angle is measured from the horizontal in degrees."""
    tool = bare(FCPath)

    assert tool.update_angle(1, 0) == 0
    assert tool.update_angle(0, 2) == 90
    assert tool.update_angle(1, 1) == 45


def test_update_angle_returns_nothing_when_the_vector_is_unusable() -> None:
    """Verify a vector that cannot be measured is reported as missing."""
    tool = bare(FCPath, app=SimpleNamespace(log=SimpleNamespace(error=lambda *args: None)))

    assert tool.update_angle("wide", 1) is None


def test_finished_path_is_the_clicked_line() -> None:
    """Verify finishing the path stores the clicked points as a line."""
    tool = bare(
        FCPath,
        points=[PointXY(0, 0), PointXY(2, 0), PointXY(2, 1)],
        cursor_data_control=False,
        draw_app=SimpleNamespace(
            in_action=True,
            app=SimpleNamespace(
                jump_signal=_Signal(),
                inform=_Inform(),
                plotcanvas=SimpleNamespace(text_cursor=SimpleNamespace(text="")),
            ),
        ),
    )

    tool.make()

    assert tool.complete is True
    assert tool.draw_app.in_action is False
    assert tool.geometry.data["type"] == "Path"
    assert list(tool.geometry.geo.coords) == [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0)]


def test_polygon_preview_is_open_after_one_click() -> None:
    """Verify the first polygon side is a line to the cursor."""
    tool = bare(FCPolygon, points=[PointXY(0, 0)])

    preview = tool.utility_geometry(PointXY(1, 0))

    assert preview.geo.geom_type == "LineString"


def test_polygon_preview_closes_after_the_second_click() -> None:
    """Verify a second click turns the preview into a closed ring."""
    tool = bare(FCPolygon, points=[PointXY(0, 0), PointXY(2, 0)])

    preview = tool.utility_geometry(PointXY(1, 2))

    assert preview.geo.geom_type == "LinearRing"
    assert preview.geo.is_closed


def test_polygon_preview_waits_for_the_first_corner() -> None:
    """Verify no polygon is drawn before the first click."""
    assert bare(FCPolygon, points=[]).utility_geometry(PointXY(1, 1)) is None


def test_finished_polygon_drops_a_repeated_last_point() -> None:
    """Verify a double click on the last corner is not stored twice."""
    tool = bare(
        FCPolygon,
        points=[PointXY(0, 0), PointXY(1, 0), PointXY(0, 1), PointXY(0, 0), PointXY(0, 0)],
        plugin_name="Polygon",
        cursor_data_control=False,
        draw_app=SimpleNamespace(
            in_action=True,
            app=SimpleNamespace(
                jump_signal=_Signal(),
                inform=_Inform(),
                plotcanvas=SimpleNamespace(text_cursor=SimpleNamespace(text="")),
            ),
        ),
    )

    tool.make()

    assert tool.points == [PointXY(0, 0), PointXY(1, 0), PointXY(0, 1), PointXY(0, 0)]
    assert tool.geometry.geo.geom_type == "LinearRing"
    assert tool.geometry.data["type"] == "Polygon"
