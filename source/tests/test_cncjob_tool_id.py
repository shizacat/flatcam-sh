"""Tests for CNC job tool ids restored from a project file."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from appObjects.CNCJobObject import CNCJobObject


def test_loaded_tool_id_converts_a_project_string() -> None:
    """Verify a tool id saved as JSON text comes back as an integer."""
    assert CNCJobObject.loaded_tool_id("2") == 2
    assert CNCJobObject.loaded_tool_id(2) == 2


def test_loaded_tool_id_rejects_a_non_integer() -> None:
    """Verify a diameter string is not accepted as a tool id."""
    with pytest.raises(ValueError):
        CNCJobObject.loaded_tool_id("0.8")


def test_loaded_tool_key_keeps_a_diameter() -> None:
    """Verify an older diameter key does not stop project loading."""
    assert CNCJobObject._loaded_tool_key("0.8") == "0.8"
    assert CNCJobObject._loaded_tool_key("2") == 2
