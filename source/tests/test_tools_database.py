"""Tests for the tools database model."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools_database import MillJobType, ToolData, ToolRecord, ToolTarget, ToolsDatabase


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
    assert tool.data.tool_target is ToolTarget.MILLING
    assert tool.model_extra["tools_mill_offset_value"] == 0.2
    assert database
    assert len(database) == 1


def test_tools_database_round_trip_writes_the_same_object(tmp_path: Path) -> None:
    """Verify writing a database and loading it preserves the tool."""
    path = tmp_path / "tools.json"
    database = ToolsDatabase({})
    database["2"] = ToolRecord(name="drill", tooldia=0.8, data={"tool_target": ToolTarget.DRILLING})
    database["2"].data.tol_max = 0.3

    database.write(path)
    loaded = ToolsDatabase.load(path)

    assert loaded["2"].name == "drill"
    assert loaded["2"].tooldia == 0.8
    assert loaded["2"].data.tool_target is ToolTarget.DRILLING
    assert loaded["2"].data.tol_max == 0.3
    written = json.loads(path.read_text())
    assert written["2"]["data"]["tool_target"] == ToolTarget.DRILLING
    assert "milling" not in written["2"]["data"]
    assert "drilling" not in written["2"]["data"]
    assert "tools_mill_cutz" not in written["2"]["data"]


def test_tool_data_copy_into_keeps_only_the_requested_operation() -> None:
    """Verify copying a tool keeps its own operation and the shared parameters."""
    data = ToolData.model_validate(
        {
            "tool_target": ToolTarget.DRILLING,
            "tol_min": 0.1,
            "tools_drill_cutz": -1.5,
            "tools_mill_cutz": -0.2,
        }
    )
    target: dict = {}

    data.copy_into(target, data.drilling)

    assert data.drilling.cutz == -1.5
    assert data.milling.cutz == -0.2
    assert target["tool_target"] is ToolTarget.DRILLING
    assert target["tol_min"] == 0.1
    assert target["tools_drill_cutz"] == -1.5
    assert "tools_mill_cutz" not in target


def test_tool_data_coerces_stored_values_to_field_types() -> None:
    """Verify defaults, form values, and coordinates land in their declared types."""
    data = ToolData.model_validate(
        {
            "tol_min": 1,
            "tools_mill_job_type": 2,
            "tools_mill_tool_shape": "V",
            "tools_mill_offset_type": 0,
            "tools_mill_travelz": 2,
            "tools_mill_dwell": True,
            "tools_mill_toolchangexy": "1.5, 2",
            "tools_mill_startz": None,
            "tools_iso_passes": 3,
            "tools_cutout_gap_type": "b",
        }
    )

    assert data.tol_min == 1.0
    assert isinstance(data.tol_min, float)
    assert data.milling.job_type is MillJobType.ISOLATION
    assert data.milling.tool_shape == "V"
    assert data.milling.offset_type == 0
    assert data.milling.travelz == 2.0
    assert data.milling.dwell is True
    assert data.milling.toolchangexy == (1.5, 2.0)
    assert data.milling.startz is None
    assert data.isolation.passes == 3
    assert data.cutout.gap_type == "b"

    data.milling.tool_shape = 4
    assert data.milling.tool_shape == 4


def test_tools_database_rejects_a_non_object() -> None:
    """Verify a JSON list is not a tools database."""
    with pytest.raises(ValueError):
        ToolsDatabase.loads("[1, 2]")


def test_empty_tools_database_is_false() -> None:
    """Verify a database with no tools is empty."""
    assert not ToolsDatabase({})
