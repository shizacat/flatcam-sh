"""Tests for resolving a stored milling tool shape to a combo index."""

import importlib.util
from pathlib import Path


def _load_mill_tool_shape():
    path = Path(__file__).resolve().parents[1] / "appPlugins" / "mill_tool_shape.py"
    spec = importlib.util.spec_from_file_location("mill_tool_shape", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mill_tool_shape = _load_mill_tool_shape()
mill_tool_shape_index = mill_tool_shape.mill_tool_shape_index
milling_tool_diameter = mill_tool_shape.milling_tool_diameter
fill_missing_mill_fields = mill_tool_shape.fill_missing_mill_fields
SHAPES = mill_tool_shape.MILL_TOOL_SHAPES


def test_label_from_the_tools_database_maps_to_its_combo_index() -> None:
    """Verify a shape label stored by the Tools Database selects that shape."""
    assert mill_tool_shape_index("V", SHAPES) == SHAPES.index("V")
    assert mill_tool_shape_index("C1", SHAPES) == 0
    assert mill_tool_shape_index(" L ", SHAPES) == SHAPES.index("L")


def test_numeric_index_is_kept() -> None:
    """Verify a combo index stored by session defaults is left unchanged."""
    assert mill_tool_shape_index(0, SHAPES) == 0
    assert mill_tool_shape_index(5, SHAPES) == 5
    assert mill_tool_shape_index("5", SHAPES) == 5


def test_milling_diameter_uses_the_tool_diameter_when_the_milling_field_is_missing() -> None:
    """Verify a Tools Database tool can create a CNC job without tools_mill_tooldia."""
    tool = {'tooldia': 0.8, 'data': {'tools_mill_cutz': -0.1}}

    assert milling_tool_diameter(tool) == 0.8


def test_milling_diameter_prefers_the_stored_milling_field() -> None:
    """Verify a milling geometry keeps the diameter stored on its tool data."""
    tool = {'tooldia': 0.8, 'data': {'tools_mill_tooldia': 1.2}}

    assert milling_tool_diameter(tool) == 1.2


def test_milling_diameter_uses_the_fallback_when_the_tool_has_neither_value() -> None:
    """Verify a tool with no diameter uses the supplied fallback."""
    assert milling_tool_diameter({'data': {}}, fallback=2.4) == 2.4


def test_missing_milling_fields_are_copied_from_defaults() -> None:
    """Verify a tool without laser settings receives them from preferences."""
    data = {'tools_mill_cutz': -0.2}
    defaults = {'tools_mill_min_power': 0.0, 'tools_mill_laser_on': 'M3', 'tools_mill_cutz': -2.4}

    fill_missing_mill_fields(data, defaults)

    assert data['tools_mill_min_power'] == 0.0
    assert data['tools_mill_laser_on'] == 'M3'
    assert data['tools_mill_cutz'] == -0.2


def test_a_stored_diameter_is_not_replaced_by_defaults() -> None:
    """Verify filling missing fields leaves the tool diameter already stored on the tool."""
    data = {'tools_mill_tooldia': 0.8}

    fill_missing_mill_fields(data, {'tools_mill_tooldia': '2.4', 'tools_mill_min_power': 0.0})

    assert data['tools_mill_tooldia'] == 0.8
    assert data['tools_mill_min_power'] == 0.0


def test_earlier_milling_defaults_win_over_later_ones() -> None:
    """Verify the first source supplies a missing field and a later source fills the rest."""
    data = {}

    fill_missing_mill_fields(
        data,
        {'tools_mill_min_power': 10.0},
        {'tools_mill_min_power': 0.0, 'tools_mill_laser_on': 'M3'},
    )

    assert data == {'tools_mill_min_power': 10.0, 'tools_mill_laser_on': 'M3'}


def test_unknown_shape_falls_back_to_the_first_entry() -> None:
    """Verify an unrecognized shape does not raise and selects the first entry."""
    assert mill_tool_shape_index("DN", SHAPES) == 0
    assert mill_tool_shape_index(None, SHAPES) == 0
    assert mill_tool_shape_index(99, SHAPES) == 0
