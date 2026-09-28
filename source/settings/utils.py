"""Helpers for applying application settings outside the settings model."""

from settings import Settings


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
        if name not in settings.model_fields:
            continue
        value = getattr(settings, name)
        if name in parser.defaults:
            parser.defaults[name] = value
            continue
        prefix = parser.__name__.lower() + "_"
        if name.startswith(prefix):
            short_name = name[len(prefix):]
            if short_name in parser.defaults:
                parser.defaults[short_name] = value
