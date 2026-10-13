"""Tools database stored as JSON and validated by pydantic."""

import json
import os
from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, RootModel, ValidationError


class ToolRecord(BaseModel):
    """
    One tool stored in the tools database.

    ``name`` and ``tooldia`` identify the tool. ``data`` holds the parameters for its target
    operation. Parameters differ by target, so they stay a dictionary.
    """

    model_config = ConfigDict(extra="allow", validate_assignment=True)

    name: str = ""
    tooldia: float = 0.0
    data: dict[str, Any] = Field(default_factory=dict)


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

        :param filename: path to the tools database
        :raises OSError: the file could not be written
        """
        from camlib import to_dict

        with open(filename, "w", encoding="utf-8") as database_file:
            json.dump(self.model_dump(), database_file, default=to_dict, indent=2)
