"""Helpers for applying application settings outside the settings model."""

import copy
from collections.abc import Iterator

from settings import Options, Settings

# Chosen in Preferences and applied to the window once, at startup.
# A project file must not replace them: the stylesheet and icon set stay as they were.
STARTUP_THEME_FIELDS = frozenset({
    "global_appearance",
    "global_theme",
    "global_dark_canvas",
})


def propagate_settings(settings: Settings) -> None:
    """
    Copies selected settings onto the parser class defaults.

    Excellon, Gerber, and Geometry read these values from their own class defaults.
    A setting name is shortened by removing the class prefix when the parser does not use the full name.

    :param settings: application settings to copy
    """
    from appParsers.ParseExcellon import Excellon
    from appParsers.ParseGerber import Gerber
    from camlib import Geometry

    routes = {
        "excellon_zeros": Excellon,
        "excellon_format_upper_in": Excellon,
        "excellon_format_lower_in": Excellon,
        "excellon_format_upper_mm": Excellon,
        "excellon_format_lower_mm": Excellon,
        "excellon_units": Excellon,
        "gerber_use_buffer_for_union": Gerber,
        "geometry_multidepth": Geometry,
    }

    for name, parser in routes.items():
        if name not in type(settings).model_fields:
            continue
        value = getattr(settings, name)
        if name in parser.defaults:
            parser.defaults[name] = value
            continue
        prefix = parser.__name__.lower() + "_"
        if name.startswith(prefix):
            short_name = name[len(prefix) :]
            if short_name in parser.defaults:
                parser.defaults[short_name] = value


def copy_shared(target, source) -> None:
    """
    Copies fields that exist on both objects.

    Nested values are copied, so the two objects do not share lists or dictionaries.
    Fields that exist on only one object are left unchanged.

    :param target: object that receives the values
    :param source: object that provides the values
    """
    source_fields = type(source).model_fields
    for name in type(target).model_fields:
        if name not in source_fields:
            continue
        setattr(target, name, copy.deepcopy(getattr(source, name)))


def option_items(storage) -> Iterator[tuple[str, object]]:
    """
    Yields names and values from session options or a dictionary.

    A settings model iterates as name and value pairs. A dictionary iterates as names.

    :param storage: session options or a mapping
    :return:        name and value pairs
    """
    fields = getattr(type(storage), "model_fields", None)
    if fields is not None and not isinstance(storage, dict):
        for name in fields:
            yield name, getattr(storage, name)
        return
    for name in storage:
        yield name, storage[name]


def apply_options(
    options: Options,
    values: dict[str, object],
    skip: frozenset[str] | set[str] | None = None,
) -> None:
    """
    Copies known fields from a mapping onto session options.

    Names that are not fields on the options object are skipped.
    Names in ``skip`` are left unchanged.

    :param options: session options
    :param values:  mapping of field names to values
    :param skip:    field names that must not be replaced
    """
    fields = type(options).model_fields
    skipped = skip or frozenset()
    for name, value in values.items():
        if name in fields and name not in skipped:
            setattr(options, name, copy.deepcopy(value))
