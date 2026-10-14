"""Tools database stored as JSON and validated by pydantic."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from enum import IntEnum
from typing import Any, ClassVar, Self

from pydantic import BaseModel, ConfigDict, Field, RootModel, ValidationError, model_validator

from settings.st_types import XYPair


class ToolTarget(IntEnum):
    """
    Operation a tool is stored for.

    The value is the combo index written in the tools database.
    """

    GENERAL = 0
    MILLING = 1
    DRILLING = 2
    ISOLATION = 3
    PAINT = 4
    NCC = 5
    CUTOUT = 6


class MillJobType(IntEnum):
    """
    Milling job stored for a tool.

    The value is the combo index written with the milling parameters.
    """

    ROUGHING = 0
    FINISHING = 1
    ISOLATION = 2
    POLISHING = 3


class OperationParameters(BaseModel):
    """
    Parameters of one operation.

    The database file stores each field under ``prefix`` plus the field name.
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    prefix: ClassVar[str] = ""

    def flat_parameters(self) -> dict[str, Any]:
        """
        Returns the stored parameters under the names used in the database file.

        :return: file field names and values, without fields left at their default
        """
        return {
            f"{self.prefix}{name}": value
            for name, value in self.model_dump(exclude_unset=True).items()
        }


class MillingTool(OperationParameters):
    """Milling parameters of one tool."""

    prefix: ClassVar[str] = "tools_mill_"

    # Shape and offset type are a combo index in defaults and a label in the database form.
    tool_shape: int | str = 0
    job_type: MillJobType = MillJobType.ROUGHING
    offset_type: int | str = 0
    offset_value: float = 0.0
    cutz: float = 0.0
    multidepth: bool = False
    depthperpass: float = 0.0
    vtipdia: float = 0.0
    vtipangle: float = 0.0
    travelz: float = 0.0
    feedrate: float = 0.0
    feedrate_z: float = 0.0
    feedrate_rapid: float = 0.0
    spindlespeed: float = 0.0
    dwell: bool = False
    dwelltime: float = 0.0
    ppname_g: str = ""
    extracut: bool = False
    extracut_length: float = 0.0
    toolchange: bool = False
    toolchangexy: XYPair = (0.0, 0.0)
    toolchangez: float = 0.0
    startz: float | None = None
    endz: float = 0.0
    endxy: XYPair | None = None
    search_time: int = 0
    z_p_depth: float = 0.0
    f_plunge: bool = False
    spindledir: str = ""
    optimization_type: str = ""
    feedrate_probe: int = 0
    area_exclusion: bool = False
    area_shape: str = ""
    area_strategy: str = ""
    area_overz: float = 0.0
    polish: bool = False
    polish_margin: float = 0.0
    polish_overlap: int = 0
    polish_method: int = 0


class NccTool(OperationParameters):
    """Non-copper clearing parameters of one tool."""

    prefix: ClassVar[str] = "tools_ncc_"

    operation: str = ""
    milling_type: str = ""
    overlap: float = 0.0
    margin: float = 0.0
    method: int = 0
    connect: bool = False
    contour: bool = False
    offset_choice: bool = False
    offset_value: float = 0.0


class PaintTool(OperationParameters):
    """Paint parameters of one tool."""

    prefix: ClassVar[str] = "tools_paint_"

    overlap: float = 0.0
    offset: float = 0.0
    method: int = 0
    connect: bool = False
    contour: bool = False


class IsolationTool(OperationParameters):
    """Isolation parameters of one tool."""

    prefix: ClassVar[str] = "tools_iso_"

    passes: int = 0
    overlap: float = 0.0
    milling_type: str = ""
    isotype: str = ""


class DrillingTool(OperationParameters):
    """Drilling parameters of one tool."""

    prefix: ClassVar[str] = "tools_drill_"

    cutz: float = 0.0
    multidepth: bool = False
    depthperpass: float = 0.0
    travelz: float = 0.0
    feedrate_z: float = 0.0
    feedrate_rapid: float = 0.0
    spindlespeed: int = 0
    dwell: bool = False
    dwelltime: float = 0.0
    offset: float = 0.0
    drill_slots: bool = False
    drill_overlap: float = 0.0
    last_drill: bool = False


class CutoutTool(OperationParameters):
    """Board cutout parameters of one tool."""

    prefix: ClassVar[str] = "tools_cutout_"

    margin: float = 0.0
    gapsize: float = 0.0
    gaps_ff: str = ""
    convexshape: bool = False
    # Gap type is an index in defaults and a radio value in the database form.
    gap_type: int | str = 0
    gap_depth: float = 0.0
    mb_dia: float = 0.0
    mb_spacing: float = 0.0


_OPERATIONS: tuple[tuple[str, type[OperationParameters]], ...] = (
    ("milling", MillingTool),
    ("ncc", NccTool),
    ("paint", PaintTool),
    ("isolation", IsolationTool),
    ("drilling", DrillingTool),
    ("cutout", CutoutTool),
)


class ToolData(BaseModel):
    """
    Parameters of one tool.

    Shared values sit on this object. Each operation has its own model. The database file still
    stores every parameter as a flat name. A field that was not in the file stays unset and is
    left out when the database is saved.
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    plot: bool = True
    tool_target: ToolTarget = ToolTarget.GENERAL
    tol_min: float = 0.0
    tol_max: float = 0.0
    # The job combo stores its label. Defaults do not fill this field.
    job: str = ""
    seg_x: float = 0.0
    seg_y: float = 0.0
    milling: MillingTool = Field(default_factory=MillingTool)
    ncc: NccTool = Field(default_factory=NccTool)
    paint: PaintTool = Field(default_factory=PaintTool)
    isolation: IsolationTool = Field(default_factory=IsolationTool)
    drilling: DrillingTool = Field(default_factory=DrillingTool)
    cutout: CutoutTool = Field(default_factory=CutoutTool)

    @model_validator(mode="before")
    @classmethod
    def nest_flat_fields(cls, value: Any) -> Any:
        """
        Groups flat database names into the operation models.

        A value that already contains an operation model is left unchanged.

        :param value: flat parameters, or parameters that are already nested
        :return: parameters whose operation fields sit on their models
        """
        if not isinstance(value, dict):
            return value
        operation_names = {name for name, _operation in _OPERATIONS}
        if operation_names.intersection(value):
            return value

        nested = {}
        operations = {name: {} for name, _operation in _OPERATIONS}
        for key, item in value.items():
            for name, operation in _OPERATIONS:
                prefix = operation.prefix
                if key.startswith(prefix):
                    operations[name][key.removeprefix(prefix)] = item
                    break
            else:
                nested[key] = item
        nested.update(operations)
        return nested

    def parameters(self) -> dict[str, Any]:
        """
        Returns the parameters that were stored for this tool.

        Operation fields are returned under their flat database names.

        :return: parameter names and values, without fields left at their default
        """
        operation_names = {name for name, _operation in _OPERATIONS}
        flat = self.model_dump(exclude_unset=True, exclude=operation_names)
        for name, _operation in _OPERATIONS:
            flat.update(getattr(self, name).flat_parameters())
        return flat

    def get_stored(self, name: str) -> Any:
        """
        Returns one parameter by its flat database name.

        :param name: name stored in the database file
        :return: stored value
        """
        operation, field = self._locate(name)
        if operation is None:
            return getattr(self, name)
        return getattr(operation, field)

    def set_stored(self, name: str, value: Any) -> None:
        """
        Stores one parameter addressed by its flat database name.

        :param name: name stored in the database file
        :param value: value to store
        """
        operation, field = self._locate(name)
        if operation is None:
            setattr(self, name, value)
            return
        setattr(operation, field, value)

    def copy_into(self, target: dict[str, Any], operation: OperationParameters) -> None:
        """
        Copies one operation and the shared parameters into a tool table entry.

        :param target: destination parameter dictionary
        :param operation: milling, drilling, or another operation of this tool
        """
        for name, value in self.parameters().items():
            if name.startswith("tools_"):
                continue
            target[name] = value
        target.update(operation.flat_parameters())

    def omit_where(self, drop: Callable[[str], bool]) -> ToolData:
        """
        Returns these parameters without the names ``drop`` selects.

        :param drop: returns True for a parameter name that should be removed
        :return: parameters that remain
        """
        kept = {key: value for key, value in self.parameters().items() if not drop(key)}
        return ToolData.model_validate(kept)

    def _locate(self, name: str) -> tuple[OperationParameters | None, str]:
        for operation_name, operation in _OPERATIONS:
            prefix = operation.prefix
            if name.startswith(prefix):
                return getattr(self, operation_name), name.removeprefix(prefix)
        return None, name


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

    def stored(self) -> dict[str, Any]:
        """
        Returns this record in the shape written to the database file.

        :return: record fields, with operation parameters under their flat names
        """
        dumped = self.model_dump(exclude_unset=True)
        if "data" in dumped:
            dumped["data"] = self.data.parameters()
        return dumped


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
            json.dump(
                {tool_id: record.stored() for tool_id, record in self.root.items()},
                database_file,
                default=to_dict,
                indent=2,
            )
