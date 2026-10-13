"""Tools database stored as JSON and validated by pydantic."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, RootModel, ValidationError


class ToolData(BaseModel):
    """
    Parameters of one tool.

    The values come from the tool's target operation. A field that was not in the file stays unset
    and is left out when the database is saved.
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    plot: Any = None
    tool_target: Any = 0
    tol_min: Any = 0.0
    tol_max: Any = 0.0
    job: Any = None

    tools_mill_tool_shape: Any = None
    tools_mill_job_type: Any = None
    tools_mill_offset_type: Any = None
    tools_mill_offset_value: Any = None
    tools_mill_cutz: Any = None
    tools_mill_multidepth: Any = None
    tools_mill_depthperpass: Any = None
    tools_mill_vtipdia: Any = None
    tools_mill_vtipangle: Any = None
    tools_mill_travelz: Any = None
    tools_mill_feedrate: Any = None
    tools_mill_feedrate_z: Any = None
    tools_mill_feedrate_rapid: Any = None
    tools_mill_spindlespeed: Any = None
    tools_mill_dwell: Any = None
    tools_mill_dwelltime: Any = None
    tools_mill_ppname_g: Any = None
    tools_mill_extracut: Any = None
    tools_mill_extracut_length: Any = None
    tools_mill_toolchange: Any = None
    tools_mill_toolchangexy: Any = None
    tools_mill_toolchangez: Any = None
    tools_mill_startz: Any = None
    tools_mill_endz: Any = None
    tools_mill_endxy: Any = None
    tools_mill_search_time: Any = None
    tools_mill_z_p_depth: Any = None
    tools_mill_f_plunge: Any = None
    tools_mill_spindledir: Any = None
    tools_mill_optimization_type: Any = None
    tools_mill_feedrate_probe: Any = None
    seg_x: Any = None
    seg_y: Any = None
    tools_mill_area_exclusion: Any = None
    tools_mill_area_shape: Any = None
    tools_mill_area_strategy: Any = None
    tools_mill_area_overz: Any = None
    tools_mill_polish: Any = None
    tools_mill_polish_margin: Any = None
    tools_mill_polish_overlap: Any = None
    tools_mill_polish_method: Any = None

    tools_ncc_operation: Any = None
    tools_ncc_milling_type: Any = None
    tools_ncc_overlap: Any = None
    tools_ncc_margin: Any = None
    tools_ncc_method: Any = None
    tools_ncc_connect: Any = None
    tools_ncc_contour: Any = None
    tools_ncc_offset_choice: Any = None
    tools_ncc_offset_value: Any = None

    tools_paint_overlap: Any = None
    tools_paint_offset: Any = None
    tools_paint_method: Any = None
    tools_paint_connect: Any = None
    tools_paint_contour: Any = None

    tools_iso_passes: Any = None
    tools_iso_overlap: Any = None
    tools_iso_milling_type: Any = None
    tools_iso_isotype: Any = None

    tools_drill_cutz: Any = None
    tools_drill_multidepth: Any = None
    tools_drill_depthperpass: Any = None
    tools_drill_travelz: Any = None
    tools_drill_feedrate_z: Any = None
    tools_drill_feedrate_rapid: Any = None
    tools_drill_spindlespeed: Any = None
    tools_drill_dwell: Any = None
    tools_drill_dwelltime: Any = None
    tools_drill_offset: Any = None
    tools_drill_drill_slots: Any = None
    tools_drill_drill_overlap: Any = None
    tools_drill_last_drill: Any = None

    tools_cutout_margin: Any = None
    tools_cutout_gapsize: Any = None
    tools_cutout_gaps_ff: Any = None
    tools_cutout_convexshape: Any = None
    tools_cutout_gap_type: Any = None
    tools_cutout_gap_depth: Any = None
    tools_cutout_mb_dia: Any = None
    tools_cutout_mb_spacing: Any = None

    def parameters(self) -> dict[str, Any]:
        """
        Returns the parameters that were stored for this tool.

        :return: parameter names and values, without fields left at their default
        """
        return self.model_dump(exclude_unset=True)

    def copy_into(self, target: dict[str, Any], prefix: str) -> None:
        """
        Copies parameters that belong to one operation into a tool table entry.

        Names that start with ``tools_`` are copied only when they start with ``prefix``.
        Every other stored parameter is copied.

        :param target: destination parameter dictionary
        :param prefix: operation prefix to keep, such as ``tools_drill_``
        """
        for name, value in self.parameters().items():
            if name.startswith("tools_") and not name.startswith(prefix):
                continue
            target[name] = value

    def omit_where(self, drop: Callable[[str], bool]) -> ToolData:
        """
        Returns these parameters without the names ``drop`` selects.

        :param drop: returns True for a parameter name that should be removed
        :return: parameters that remain
        """
        kept = {key: value for key, value in self.parameters().items() if not drop(key)}
        return ToolData.model_validate(kept)


class ToolRecord(BaseModel):
    """
    One tool stored in the tools database.

    ``name`` and ``tooldia`` identify the tool. ``data`` holds the parameters for its target
    operation.
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    name: str = ""
    tooldia: float = 0.0
    data: ToolData = Field(default_factory=ToolData)


class ToolsDatabase(RootModel[dict[str, ToolRecord]]):
    """
    The tools database file.

    The file is a JSON object whose keys are tool ids and whose values are tool records.
    """

    root: dict[str, ToolRecord] = Field(default_factory=dict)

    def __bool__(self) -> bool:
        return bool(self.root)

    def __len__(self) -> int:
        return len(self.root)

    def __getitem__(self, tool_id: str) -> ToolRecord:
        return self.root[tool_id]

    def __setitem__(self, tool_id: str, tool: ToolRecord | dict[str, Any]) -> None:
        if not isinstance(tool, ToolRecord):
            tool = ToolRecord.model_validate(tool)
        self.root[tool_id] = tool

    def items(self):
        """
        Returns the tool id and record pairs.

        :return: pairs stored in the database
        """
        return self.root.items()

    def values(self):
        """
        Returns the stored tool records.

        :return: tool records
        """
        return self.root.values()

    def keys(self):
        """
        Returns the stored tool ids.

        :return: tool ids
        """
        return self.root.keys()

    def pop(self, tool_id: str, default: ToolRecord | None = None) -> ToolRecord | None:
        """
        Removes a tool and returns it.

        :param tool_id: id of the tool to remove
        :param default: value returned when the id is absent
        :return: removed tool, or ``default``
        """
        return self.root.pop(tool_id, default)

    def update(self, tools: dict[str, ToolRecord | dict[str, Any]]) -> None:
        """
        Adds or replaces tools.

        :param tools: tool ids mapped to records or dictionaries
        """
        for tool_id, tool in tools.items():
            self[tool_id] = tool

    @classmethod
    def loads(cls, content: str) -> Self:
        """
        Builds a database from a JSON string.

        :param content: JSON object of tool records
        :return: validated database
        :raises ValueError: the text is not a JSON object of tool records
        """
        try:
            loaded = json.loads(content)
            if not isinstance(loaded, dict):
                raise ValueError("Tools database must be a JSON object.")
            return cls.model_validate(loaded)
        except (ValidationError, ValueError) as error:
            raise ValueError("Could not parse the tools database.") from error

    @classmethod
    def load(cls, filename: str | os.PathLike[str]) -> Self:
        """
        Loads a database from a JSON file.

        :param filename: path to the tools database
        :return: validated database
        :raises OSError: the file could not be read
        :raises ValueError: the file is not a JSON object of tool records
        """
        with open(filename, encoding="utf-8") as database_file:
            return cls.loads(database_file.read())

    def write(self, filename: str | os.PathLike[str]) -> None:
        """
        Writes the database to a JSON file.

        Fields that were not stored are left out of the file.

        :param filename: path to the tools database
        :raises OSError: the file could not be written
        """
        from camlib import to_dict

        with open(filename, "w", encoding="utf-8") as database_file:
            json.dump(self.model_dump(exclude_unset=True), database_file, default=to_dict, indent=2)
