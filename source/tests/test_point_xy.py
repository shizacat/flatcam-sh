"""Tests for coordinate arithmetic on PointXY."""

import pytest

from settings.st_types import PointXY


def test_addition_returns_the_sum_of_coordinates() -> None:
    """Verify adding two points adds X and Y separately."""
    assert PointXY(1, 2) + PointXY(3, 4) == PointXY(4, 6)


def test_subtraction_returns_the_offset() -> None:
    """Verify subtracting two points returns the vector between them."""
    assert PointXY(5, 1) - PointXY(2, 4) == PointXY(3, -3)


def test_multiplication_scales_both_coordinates() -> None:
    """Verify a number on either side scales X and Y."""
    assert PointXY(2, -3) * 2 == PointXY(4, -6)
    assert 0.5 * PointXY(2, -3) == PointXY(1, -1.5)


def test_division_scales_both_coordinates() -> None:
    """Verify dividing by a number scales X and Y."""
    assert PointXY(4, -2) / 2 == PointXY(2, -1)


def test_absolute_value_is_the_distance_from_the_origin() -> None:
    """Verify the length of a 3-4-5 vector."""
    assert abs(PointXY(3, 4)) == 5


def test_step_along_a_segment_lands_at_the_requested_length() -> None:
    """Verify moving from one point toward another by a fixed length."""
    start = PointXY(1, 1)
    end = PointXY(4, 5)
    delta = end - start
    step = start + delta * (2.5 / abs(delta))

    assert abs(step - start) == pytest.approx(2.5)
    assert step == pytest.approx(PointXY(2.5, 3))
