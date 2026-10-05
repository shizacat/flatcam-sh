"""Resolve stored milling tool values that use more than one representation."""

from collections.abc import Iterator, Sequence
from copy import deepcopy

MILL_TOOL_SHAPES = ("C1", "C2", "C3", "C4", "B", "V", "L")


def mill_tool_shape_index(shape: int | str | None, shapes: Sequence[str] = MILL_TOOL_SHAPES) -> int:
    """
    Returns the combo index for a stored milling tool shape.

    The Tools Database stores the shape label, for example ``V``. Session
    defaults and other tools store the combo index.

    :param shape:  a combo index or a shape label
    :param shapes: shape labels in combo order
    :return:       an index into ``shapes``
    """
    if isinstance(shape, str):
        label = shape.strip()
        if label in shapes:
            return shapes.index(label)

    try:
        index = int(shape)
    except (TypeError, ValueError):
        return 0

    if index < 0 or index >= len(shapes):
        return 0
    return index


def milling_tool_diameter(
    tool: dict[str, object],
    fallback: float | int | str | None = None,
) -> float | int | str:
    """
    Returns the diameter stored on a milling tool.

    Geometry created for milling stores the diameter in ``data['tools_mill_tooldia']``.
    A tool taken from the Tools Database stores it as ``tooldia``.

    :param tool:     a tool dict with ``tooldia`` and ``data``
    :param fallback: diameter used when the tool stores neither value
    :return:         the tool diameter
    :raises KeyError: the tool has no diameter and ``fallback`` is missing
    """
    data = tool.get('data') if isinstance(tool, dict) else None
    if isinstance(data, dict):
        stored = data.get('tools_mill_tooldia')
        if stored not in (None, ''):
            return stored

    if isinstance(tool, dict):
        stored = tool.get('tooldia')
        if stored not in (None, ''):
            return stored

    if fallback not in (None, ''):
        return fallback
    raise KeyError('tools_mill_tooldia')


def _mill_field_items(source: object | None) -> Iterator[tuple[str, object]]:
    """
    Yields milling-field names and values from a mapping or a settings model.

    :param source: a dict or an object with ``model_fields``
    :return:       ``tools_mill_`` names and their values
    """
    if source is None:
        return

    fields = getattr(type(source), 'model_fields', None)
    if fields is not None and not isinstance(source, dict):
        pairs = ((name, getattr(source, name)) for name in fields)
    elif isinstance(source, dict):
        pairs = source.items()
    else:
        return

    for name, value in pairs:
        if isinstance(name, str) and name.startswith('tools_mill_'):
            yield name, value


def fill_missing_mill_fields(data: dict[str, object], *sources: object) -> dict[str, object]:
    """
    Copies milling fields that the tool data does not already store.

    Earlier sources win. A value already stored on ``data``, including ``0``
    and ``None``, is left unchanged.

    :param data:    tool data updated in place
    :param sources: mappings or settings models that provide milling fields
    :return:        ``data``
    """
    if not isinstance(data, dict):
        return data

    for source in sources:
        for name, value in _mill_field_items(source):
            if name not in data:
                data[name] = deepcopy(value)
    return data
