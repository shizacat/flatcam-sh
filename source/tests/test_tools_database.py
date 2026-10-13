"""Tests for the tools database model."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools_database import ToolRecord, ToolsDatabase


def test_tools_database_loads_records_and_keeps_extra_fields() -> None:
    """Verify a saved database comes back with tool fields and extra keys."""
    database = ToolsDatabase.loads(
        json.dumps(
            {
                "1": {
                    "name": "endmill",
                    "tooldia": 1.5,
                    "data": {"tool_target": 1, "tol_min": 0.1},
                    "tools_mill_offset_value": 0.2,
                }
            }
        )
    )

    tool = database["1"]

    assert tool.name == "endmill"
    assert tool.tooldia == 1.5
    assert tool.data["tool_target"] == 1
    assert tool.model_extra["tools_mill_offset_value"] == 0.2
    assert database
    assert len(database) == 1


def test_tools_database_round_trip_writes_the_same_object(tmp_path: Path) -> None:
    """Verify writing a database and loading it preserves the tool."""
    path = tmp_path / "tools.json"
    database = ToolsDatabase({})
    database["2"] = ToolRecord(name="drill", tooldia=0.8, data={"tool_target": 2})
    database["2"].data["tol_max"] = 0.3

    database.write(path)
    loaded = ToolsDatabase.load(path)

    assert loaded["2"].name == "drill"
    assert loaded["2"].tooldia == 0.8
    assert loaded["2"].data["tol_max"] == 0.3


def test_tools_database_rejects_a_non_object() -> None:
    """Verify a JSON list is not a tools database."""
    with pytest.raises(ValueError):
        ToolsDatabase.loads("[1, 2]")


def test_empty_tools_database_is_false() -> None:
    """Verify a database with no tools is empty."""
    assert not ToolsDatabase({})
