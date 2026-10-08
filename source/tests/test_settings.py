"""Tests for the typed application settings model."""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exceptions import FlatCAMError, SettingsError
from settings import Options, Settings
from settings.st_types import Appearance, Theme
from settings.utils import (
    PROJECT_EXCLUDED_FIELDS,
    STARTUP_THEME_FIELDS,
    apply_options,
    copy_shared,
    option_items,
    propagate_settings,
)


def test_settings_error_uses_the_project_base_exception() -> None:
    """Verify settings errors inherit from the project base exception."""
    assert issubclass(SettingsError, FlatCAMError)


def test_every_setting_has_a_default() -> None:
    """Verify every setting has a default used when no settings file exists."""
    required = [
        name for name, field in Settings.model_fields.items() if field.is_required()
    ]
    settings = Settings()

    assert required == []
    assert set(settings.model_dump()) == set(Settings.model_fields)


def test_representative_defaults() -> None:
    """Verify representative scalar, translated, and collection defaults."""
    settings = Settings()

    assert settings.version == "8.992"
    assert settings.units == "MM"
    assert settings.tools_transform_reference == "Selection"
    assert settings.global_grid_context_menu == {
        "in": [0.01, 0.02, 0.025, 0.05, 0.1],
        "mm": [0.1, 0.2, 0.5, 1, 2.54],
    }
    assert settings.document_font_sizes[-1] == "96"


def test_mutable_defaults_are_independent() -> None:
    """Verify model instances do not share mutable defaults."""
    first = Settings()
    second = Settings()

    first.global_languages.append("Spanish")
    first.global_grid_context_menu["mm"].append(5.0)
    first.global_stats["launch"] = 1

    assert second.global_languages == ["English"]
    assert second.global_grid_context_menu["mm"] == [0.1, 0.2, 0.5, 1, 2.54]
    assert second.global_stats == {}


def test_unknown_fields_are_rejected() -> None:
    """Verify unknown setting names cannot be supplied."""
    with pytest.raises(ValidationError):
        Settings(unknown_setting=True)


def test_load_reads_json_file(tmp_path: Path) -> None:
    """Verify a JSON file overrides the settings it contains."""
    path = tmp_path / "settings.json"
    path.write_text(
        '{"units": "IN", "global_theme": "dark", "global_appearance": "dark"}',
        encoding="utf-8",
    )

    settings = Settings.load(path)

    assert settings.units == "IN"
    assert settings.version == "8.992"
    assert settings.global_appearance is Appearance.DARK
    assert "global_theme" not in Settings.model_fields


def test_load_raises_settings_error(tmp_path: Path) -> None:
    """Verify file and validation failures raise the shared settings error."""
    missing = tmp_path / "missing.json"
    invalid_json = tmp_path / "invalid.json"
    invalid_value = tmp_path / "invalid-value.json"
    invalid_json.write_text("{", encoding="utf-8")
    invalid_value.write_text('{"units": []}', encoding="utf-8")

    with pytest.raises(SettingsError):
        Settings.load(missing)
    with pytest.raises(SettingsError):
        Settings.load(invalid_json)
    with pytest.raises(SettingsError):
        Settings.load(invalid_value)


def test_write_saves_json_file(tmp_path: Path) -> None:
    """Verify settings written to disk can be loaded back."""
    path = tmp_path / "settings.json"
    settings = Settings(units="IN")

    settings.write(path)

    assert Settings.load(path).units == "IN"


def test_write_raises_settings_error(tmp_path: Path) -> None:
    """Verify a failed settings write raises the shared settings error."""
    with pytest.raises(SettingsError):
        Settings().write(tmp_path / "missing" / "settings.json")


def test_report_usage_counts_resources() -> None:
    """Verify each resource usage counter increments on its own."""
    settings = Settings()

    settings.report_usage("ToolMove()")
    settings.report_usage("ToolMove()")
    settings.report_usage("ToolFilm()")

    assert settings.global_stats["ToolMove()"] == 2
    assert settings.global_stats["ToolFilm()"] == 1


def test_bind_reports_changed_settings() -> None:
    """Verify a bound callback receives the name of a changed setting."""
    settings = Settings()
    changed = []
    settings.bind(changed.append)

    settings.units = "IN"
    settings.units = "IN"

    assert changed == ["units"]
    assert settings.units == "IN"


def test_unbind_stops_change_notifications() -> None:
    """Verify an unbound callback no longer receives setting changes."""
    settings = Settings()
    changed = []
    settings.bind(changed.append)

    settings.unbind(changed.append)
    settings.units = "IN"

    assert changed == []
    with pytest.raises(SettingsError):
        settings.unbind(changed.append)


def test_bind_is_not_called_when_assignment_is_rejected() -> None:
    """Verify a rejected assignment does not notify bound callbacks."""
    settings = Settings()
    changed = []
    settings.bind(changed.append)

    with pytest.raises(ValidationError):
        settings.units = []

    assert changed == []


def test_assignment_is_validated() -> None:
    """Verify field validation also applies after initialization."""
    settings = Settings()

    with pytest.raises(ValidationError):
        settings.units = []


def test_options_start_from_settings_and_then_diverge() -> None:
    """Verify session options copy saved settings and do not write them back."""
    settings = Settings()
    options = Options.from_settings(settings)

    options.units = "IN"
    options.global_theme = Theme.DARK
    options.global_grid_context_menu["mm"].append(5.0)

    assert options.units == "IN"
    assert options.global_theme is Theme.DARK
    assert settings.units == "MM"
    assert "global_theme" not in Settings.model_fields
    assert 5.0 not in settings.global_grid_context_menu["mm"]
    assert "version" not in Options.model_fields
    assert "global_stats" not in Options.model_fields
    assert set(Options.model_fields) - {"global_theme"} < set(Settings.model_fields)


def test_copy_shared_copies_common_fields_without_sharing_nested_values() -> None:
    """Verify shared fields are copied and fields that exist on only one object stay put."""
    settings = Settings(units="IN")
    settings.report_usage("launch")
    settings.global_grid_context_menu["mm"].append(5.0)
    options = Options.from_settings(Settings())
    options.global_theme = Theme.DARK

    copy_shared(options, settings)

    assert options.global_theme is Theme.DARK

    assert options.units == "IN"
    assert options.global_grid_context_menu["mm"][-1] == 5.0
    options.global_grid_context_menu["mm"].append(9.0)
    assert settings.global_grid_context_menu["mm"][-1] == 5.0

    options.units = "MM"
    copy_shared(settings, options)

    assert settings.units == "MM"
    assert settings.version == "8.992"
    assert settings.global_stats == {"launch": 1}


def test_option_items_yields_name_and_value_pairs() -> None:
    """Verify session options and a dictionary both yield name and value pairs."""
    options = Options.from_settings(Settings(units="IN"))
    items = dict(option_items(options))

    assert items["units"] == "IN"
    assert "version" not in items
    assert "global_stats" not in items

    stored = {"units": "MM", "tools_iso_tooldia": 0.2}
    assert list(option_items(stored)) == [
        ("units", "MM"),
        ("tools_iso_tooldia", 0.2),
    ]


def test_apply_options_copies_known_fields_and_skips_the_rest() -> None:
    """Verify known option names are copied and unknown names are left out."""
    options = Options.from_settings(Settings())
    grid = {"in": [0.01], "mm": [0.1]}

    apply_options(
        options,
        {
            "units": "IN",
            "global_grid_context_menu": grid,
            "not_a_setting": True,
        },
    )

    assert options.units == "IN"
    assert options.global_theme is Theme.LIGHT
    grid["mm"].append(2.0)
    assert options.global_grid_context_menu["mm"] == [0.1]


def test_apply_options_leaves_the_startup_theme_when_asked() -> None:
    """Verify a project mapping cannot replace the theme applied at startup."""
    options = Options.from_settings(Settings())
    options.global_appearance = Appearance.DARK
    options.global_theme = Theme.DARK
    options.global_dark_canvas = True

    apply_options(
        options,
        {
            "units": "IN",
            "global_appearance": Appearance.LIGHT,
            "global_theme": Theme.LIGHT,
            "global_dark_canvas": False,
        },
        skip=STARTUP_THEME_FIELDS,
    )

    assert options.units == "IN"
    assert options.global_appearance is Appearance.DARK
    assert options.global_theme is Theme.DARK
    assert options.global_dark_canvas is True


def test_apply_options_leaves_application_level_when_a_project_is_imported() -> None:
    """Verify a project mapping cannot replace the Application Level chosen in Preferences."""
    options = Options.from_settings(Settings())
    options.global_app_level = "a"

    apply_options(
        options,
        {
            "units": "IN",
            "global_app_level": "b",
        },
        skip=PROJECT_EXCLUDED_FIELDS,
    )

    assert options.units == "IN"
    assert options.global_app_level == "a"
    assert "global_app_level" in PROJECT_EXCLUDED_FIELDS
    assert STARTUP_THEME_FIELDS < PROJECT_EXCLUDED_FIELDS


def test_theme_is_light_only_for_the_light_color() -> None:
    """Verify the light session color keeps dark text on a light background."""
    assert Theme.LIGHT.is_light()
    assert not Theme.DARK.is_light()


def test_load_maps_retired_appearance_names_to_system(tmp_path: Path) -> None:
    """Verify default and auto from older settings files become the system color."""
    path = tmp_path / "settings.json"
    path.write_text('{"global_appearance": "default"}', encoding="utf-8")
    assert Settings.load(path).global_appearance is Appearance.SYSTEM

    path.write_text('{"global_appearance": "auto"}', encoding="utf-8")
    assert Settings.load(path).global_appearance is Appearance.SYSTEM


def test_theme_from_appearance_resolves_each_choice(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify the color choice maps to the session color, and System follows the OS."""
    options = Options.from_settings(Settings())

    options.global_appearance = Appearance.LIGHT
    assert options.theme_from_appearance() is Theme.LIGHT
    options.global_appearance = Appearance.DARK
    assert options.theme_from_appearance() is Theme.DARK

    monkeypatch.setattr("settings.models.options.darkdetect.isDark", lambda: True)
    options.global_appearance = Appearance.SYSTEM
    assert options.theme_from_appearance() is Theme.DARK
    monkeypatch.setattr("settings.models.options.darkdetect.isDark", lambda: False)
    assert options.theme_from_appearance() is Theme.LIGHT


def test_propagate_settings_copies_parser_defaults() -> None:
    """Verify parser defaults receive a stored name, or the name with the class prefix removed."""
    from appParsers.ParseExcellon import Excellon
    from appParsers.ParseGerber import Gerber
    from camlib import Geometry

    saved = {
        Excellon: dict(Excellon.defaults),
        Gerber: dict(Gerber.defaults),
        Geometry: dict(Geometry.defaults),
    }
    try:
        settings = Settings(
            excellon_zeros="L",
            excellon_units="MM",
            excellon_format_upper_in=5,
            gerber_use_buffer_for_union=False,
        )
        propagate_settings(settings)

        assert Excellon.defaults["zeros"] == "L"
        assert Excellon.defaults["excellon_units"] == "MM"
        assert Excellon.defaults["excellon_format_upper_in"] == 5
        assert Excellon.defaults["excellon_circle_steps"] == saved[Excellon]["excellon_circle_steps"]
        assert "use_buffer_for_union" not in Gerber.defaults
        assert Geometry.defaults == saved[Geometry]
    finally:
        for parser, defaults in saved.items():
            parser.defaults.clear()
            parser.defaults.update(defaults)
