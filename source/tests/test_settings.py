"""Tests for the typed application settings model."""

import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exceptions import FlatCAMError, SettingsError
from settings import Settings


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

    assert settings.version == 8.992
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
    path.write_text('{"units": "IN"}', encoding="utf-8")

    settings = Settings.load(path)

    assert settings.units == "IN"
    assert settings.version == 8.992


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
