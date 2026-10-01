"""Tests for the folder that stores user settings."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import appMain
from appMain import App


def _host() -> SimpleNamespace:
    """
    Builds the small stand-in the folder method needs.

    :return: object with a log and a headless flag
    """
    return SimpleNamespace(cmd_line_headless=0, log=Mock())


def _windows_app(monkeypatch: pytest.MonkeyPatch, app_file: Path) -> None:
    """
    Points the Windows lookup at a fake application file.

    :param monkeypatch: pytest patch helper
    :param app_file:    stand-in for appMain.py
    """
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(appMain, "__file__", str(app_file))


def test_user_settings_folder_on_unix_is_under_home(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify macOS and Linux keep user settings in ~/.FlatCAM."""
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(appMain.Path, "home", lambda: tmp_path)

    assert App.user_settings_folder(_host()) == tmp_path / ".FlatCAM"


def test_user_settings_folder_without_a_config_file_uses_appdata(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify a missing Windows configuration file selects the APPDATA folder."""
    appdata = tmp_path / "AppData"
    _windows_app(monkeypatch, tmp_path / "pkg" / "appMain.py")
    monkeypatch.setenv("appdata", str(appdata))
    host = _host()

    assert App.user_settings_folder(host) == appdata / "FlatCAM"
    host.log.error.assert_called_once()


def test_user_settings_folder_reads_portable_and_headless(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify portable mode uses the config folder and headless is recorded."""
    config = tmp_path / "config"
    config.mkdir()
    (config / "configuration.txt").write_text("portable=True\nheadless=true\n", encoding="utf-8")
    _windows_app(monkeypatch, tmp_path / "pkg" / "appMain.py")
    host = _host()

    assert App.user_settings_folder(host) == config
    assert host.cmd_line_headless == 1


def test_user_settings_folder_reads_the_fallback_config_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify the configuration file beside the application is used when the outer one is absent."""
    appdata = tmp_path / "AppData"
    fallback = tmp_path / "pkg" / "config"
    fallback.mkdir(parents=True)
    (fallback / "configuration.txt").write_text("portable=False\n", encoding="utf-8")
    _windows_app(monkeypatch, tmp_path / "pkg" / "appMain.py")
    monkeypatch.setenv("appdata", str(appdata))

    assert App.user_settings_folder(_host()) == appdata / "FlatCAM"


def test_user_settings_folder_returns_none_when_the_config_cannot_be_parsed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify an unreadable portable flag returns no settings folder."""
    config = tmp_path / "config"
    config.mkdir()
    (config / "configuration.txt").write_text("portable=1/0\n", encoding="utf-8")
    _windows_app(monkeypatch, tmp_path / "pkg" / "appMain.py")
    host = _host()

    assert App.user_settings_folder(host) is None
    host.log.error.assert_called_once()


def test_user_settings_folder_ignores_an_unknown_portable_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify an unknown portable value keeps the normal Windows folder."""
    appdata = tmp_path / "AppData"
    config = tmp_path / "config"
    config.mkdir()
    (config / "configuration.txt").write_text("portable=not_a_name\n", encoding="utf-8")
    _windows_app(monkeypatch, tmp_path / "pkg" / "appMain.py")
    monkeypatch.setenv("appdata", str(appdata))

    assert App.user_settings_folder(_host()) == appdata / "FlatCAM"


def test_user_settings_folder_raises_when_appdata_is_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify Windows without APPDATA raises TypeError."""
    _windows_app(monkeypatch, tmp_path / "pkg" / "appMain.py")
    monkeypatch.delenv("appdata", raising=False)

    with pytest.raises(TypeError):
        App.user_settings_folder(_host())


def test_user_settings_folder_raises_when_the_config_path_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify a configuration path that is not a readable file raises OSError."""
    blocked = tmp_path / "pkg" / "config" / "configuration.txt"
    blocked.mkdir(parents=True)
    _windows_app(monkeypatch, tmp_path / "pkg" / "appMain.py")

    with pytest.raises(OSError):
        App.user_settings_folder(_host())
