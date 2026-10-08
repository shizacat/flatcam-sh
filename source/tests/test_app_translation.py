"""Tests for locale discovery and gettext installation."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QEvent, QPointF, QSettings, Qt
from PyQt6.QtGui import QMouseEvent

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import appTranslation
from settings.gui_settings import GuiSettings


@pytest.fixture(scope="module", autouse=True)
def qapplication():
    """Create the Qt application before any QSettings object.

    A QSettings created first is deleted when QApplication is constructed.
    """
    from PyQt6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def gui_settings(tmp_path: Path):
    """Point the singleton at a temporary file and drop it afterwards."""
    store = QSettings(str(tmp_path / "gui.ini"), QSettings.Format.IniFormat)
    settings = GuiSettings.reset(store)
    assert settings is not None
    yield settings
    GuiSettings.reset()


def _mouse_event(kind: QEvent.Type, button: Qt.MouseButton, local_pos: QPointF, global_pos: QPointF) -> QMouseEvent:
    """Builds a mouse event with separate local and global positions."""
    return QMouseEvent(
        kind,
        local_pos,
        global_pos,
        button,
        button,
        Qt.KeyboardModifier.NoModifier,
    )


def test_languages_dir_points_at_the_module_locale() -> None:
    """Verify the locale directory sits next to the translation module."""
    module_dir = Path(appTranslation.__file__).resolve().parent

    assert appTranslation.languages_dir() == module_dir / "locale"
    assert appTranslation.languages_dir_cx_freeze() == module_dir.parent / "locale"


def test_load_languages_maps_known_codes_and_skips_other_entries(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify only language folders listed in the dictionary are returned."""
    locale = tmp_path / "locale"
    (locale / "ru").mkdir(parents=True)
    (locale / "en").mkdir()
    (locale / "xx").mkdir()
    (locale / "notes.txt").write_text("not a language", encoding="utf-8")
    monkeypatch.setattr(appTranslation, "languages_dir", lambda: locale)
    monkeypatch.setattr(appTranslation, "languages_dir_cx_freeze", lambda: tmp_path / "missing")

    assert appTranslation.load_languages() == {"ru": "Pусский", "en": "English"}


def test_load_languages_uses_the_frozen_directory_when_the_module_locale_is_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify a missing module locale falls back to the frozen-build directory."""
    frozen = tmp_path / "frozen" / "locale"
    (frozen / "de").mkdir(parents=True)
    monkeypatch.setattr(appTranslation, "languages_dir", lambda: tmp_path / "absent")
    monkeypatch.setattr(appTranslation, "languages_dir_cx_freeze", lambda: frozen)

    assert appTranslation.load_languages() == {"de": "Deutsche"}


def test_load_languages_returns_an_empty_mapping_when_no_locale_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Verify a missing locale directory does not invent languages."""
    monkeypatch.setattr(appTranslation, "languages_dir", lambda: tmp_path / "absent")
    monkeypatch.setattr(appTranslation, "languages_dir_cx_freeze", lambda: tmp_path / "also-absent")

    assert appTranslation.load_languages() == {}


def test_load_languages_reads_the_shipped_catalogs() -> None:
    """Verify the catalogs shipped with the source tree are recognized."""
    found = appTranslation.load_languages()

    assert found["en"] == "English"
    assert found["ru"] == "Pусский"
    assert set(found) <= set(appTranslation.languages_dict)


def test_apply_language_returns_no_language_when_the_name_is_unknown(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify an unknown language name does not install another catalog."""
    monkeypatch.setattr(appTranslation, "load_languages", lambda: {"en": "English", "ru": "Pусский"})
    called = False

    def translation(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("translation catalog should not be opened")

    monkeypatch.setattr(appTranslation.gettext, "translation", translation)

    assert appTranslation.apply_language("strings", "Klingon") == "no language"
    assert called is False


def test_apply_language_installs_the_matching_catalog(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify the display name selects the language code and installs that catalog."""
    locale = tmp_path / "locale"
    catalog = MagicMock()
    calls = []

    def translation(domain, localedir, languages):
        calls.append((domain, Path(localedir), list(languages)))
        return catalog

    monkeypatch.setattr(appTranslation, "load_languages", lambda: {"ru": "Pусский"})
    monkeypatch.setattr(appTranslation, "languages_dir", lambda: locale)
    monkeypatch.setattr(appTranslation.gettext, "translation", translation)

    assert appTranslation.apply_language("strings", "Pусский") == "Pусский"
    assert calls == [("strings", locale, ["ru"])]
    catalog.install.assert_called_once_with()


def test_apply_language_falls_back_to_the_frozen_locale(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify a missing module catalog is loaded from the frozen-build directory."""
    module_locale = tmp_path / "module"
    frozen_locale = tmp_path / "frozen"
    catalog = MagicMock()
    calls = []

    def translation(domain, localedir, languages):
        calls.append(Path(localedir))
        if Path(localedir) == module_locale:
            raise FileNotFoundError(localedir)
        return catalog

    monkeypatch.setattr(appTranslation, "load_languages", lambda: {"fr": "Français"})
    monkeypatch.setattr(appTranslation, "languages_dir", lambda: module_locale)
    monkeypatch.setattr(appTranslation, "languages_dir_cx_freeze", lambda: frozen_locale)
    monkeypatch.setattr(appTranslation.gettext, "translation", translation)

    assert appTranslation.apply_language("strings", "Français") == "Français"
    assert calls == [module_locale, frozen_locale]
    catalog.install.assert_called_once_with()


def test_apply_language_keeps_the_name_when_no_catalog_file_loads(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify a known language is reported even when both catalog files are missing."""
    def translation(*args, **kwargs):
        raise FileNotFoundError("strings.mo")

    monkeypatch.setattr(appTranslation, "load_languages", lambda: {"en": "English"})
    monkeypatch.setattr(appTranslation.gettext, "translation", translation)

    assert appTranslation.apply_language("strings", "English") == "English"


def test_apply_language_stores_english_when_nothing_is_saved(
    monkeypatch: pytest.MonkeyPatch, gui_settings: GuiSettings
) -> None:
    """Verify a missing stored language is saved as English and then applied."""
    monkeypatch.setattr(appTranslation, "load_languages", lambda: {"en": "English"})
    monkeypatch.setattr(appTranslation.gettext, "translation", lambda *args, **kwargs: MagicMock())

    assert gui_settings.language() is None
    assert appTranslation.apply_language("strings") == "English"
    assert gui_settings.language() == "English"


def test_is_admin_is_false_for_a_normal_posix_user(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify a non-root POSIX user is not reported as an administrator."""
    monkeypatch.setattr(appTranslation.os, "getuid", lambda: 1000)
    monkeypatch.setattr(appTranslation.os, "geteuid", lambda: 1000)

    assert appTranslation.isAdmin() is False


def test_is_admin_is_true_for_root(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify a root effective id is reported as an administrator."""
    monkeypatch.setattr(appTranslation.os, "getuid", lambda: 1000)
    monkeypatch.setattr(appTranslation.os, "geteuid", lambda: 0)

    assert appTranslation.isAdmin() is True


def test_is_admin_uses_the_windows_api_when_posix_ids_are_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify Windows admin detection is used when POSIX user ids do not exist."""
    monkeypatch.delattr(appTranslation.os, "getuid", raising=False)
    windll = SimpleNamespace(shell32=SimpleNamespace(IsUserAnAdmin=lambda: 1))
    monkeypatch.setattr(appTranslation.ctypes, "windll", windll, raising=False)

    assert appTranslation.isAdmin() is True


def test_apply_click_does_nothing_when_the_language_is_already_active(gui_settings: GuiSettings) -> None:
    """Verify choosing the stored language does not save or restart."""
    gui_settings.save_language("English")
    app = MagicMock()
    app.ui.general_pref_form.general_app_group.language_combo.currentText.return_value = "English"
    app.options.global_theme.is_light.return_value = True

    appTranslation.on_language_apply_click(app, restart=True)

    assert gui_settings.language() == "English"
    app.new_launch.stop.emit.assert_not_called()


def test_apply_click_saves_and_restarts_only_after_confirmation(
    monkeypatch: pytest.MonkeyPatch, gui_settings: GuiSettings
) -> None:
    """Verify Apply Language stores the name and restarts only when the user confirms."""
    gui_settings.save_language("English")
    app = MagicMock()
    app.ui.general_pref_form.general_app_group.language_combo.currentText.return_value = "Română"
    app.options.global_theme.is_light.return_value = True
    restarted = []
    monkeypatch.setattr(appTranslation, "restart_program", lambda **kwargs: restarted.append(kwargs["app"]))

    class _Box:
        def __init__(self, parent=None):
            self.yes = object()
            self.no = object()
            self.choice = self.no

        def addButton(self, text, role):
            return self.yes if text == "Yes" else self.no

        def clickedButton(self):
            return self.choice

        def __getattr__(self, name):
            return lambda *args, **kwargs: None

    box = _Box()
    monkeypatch.setattr(appTranslation, "FCMessageBox", lambda parent=None: box)

    appTranslation.on_language_apply_click(app, restart=True)

    assert gui_settings.language() == "English"
    assert restarted == []

    box.choice = box.yes
    appTranslation.on_language_apply_click(app, restart=True)

    assert gui_settings.language() == "Română"
    assert restarted == [app]


def test_restart_program_reexecutes_without_asking(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify a clean project restarts the interpreter without a save dialog."""
    recorded = {}

    def execl(python, *args):
        recorded["python"] = python
        recorded["args"] = args

    monkeypatch.setattr(appTranslation.os, "execl", execl)
    monkeypatch.setattr(appTranslation, "copy_shared", lambda *args, **kwargs: None)
    app = MagicMock()
    app.options.global_theme.is_light.return_value = False
    app.should_we_save = False
    app.collection.get_list.return_value = []

    appTranslation.restart_program(app)

    assert recorded["python"] == sys.executable
    assert recorded["args"][0] == sys.executable
    app.preferencesUiManager.save_defaults.assert_called_once_with()
    app.f_handlers.on_file_save_project_as.assert_not_called()


def test_restart_program_saves_the_project_when_the_user_confirms(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify a confirmed restart asks the file handler to save the project."""
    monkeypatch.setattr(appTranslation.os, "execl", lambda *args: None)
    monkeypatch.setattr(appTranslation, "copy_shared", lambda *args, **kwargs: None)
    app = MagicMock()
    app.options.global_theme.is_light.return_value = True
    app.should_we_save = False

    class _Box:
        def __init__(self, parent=None):
            self.yes = object()

        def addButton(self, text, role):
            return self.yes

        def clickedButton(self):
            return self.yes

        def __getattr__(self, name):
            return lambda *args, **kwargs: None

    monkeypatch.setattr(appTranslation, "FCMessageBox", lambda parent=None: _Box())

    appTranslation.restart_program(app, ask=True)

    app.f_handlers.on_file_save_project_as.assert_called_once_with(use_thread=True, quit_action=True)


def test_message_box_starts_a_drag_on_left_press_and_moves(qapplication) -> None:
    """Verify a left-button drag records the offset and moves the window."""
    box = appTranslation.FCMessageBox()
    press = _mouse_event(QEvent.Type.MouseButtonPress, Qt.MouseButton.LeftButton, QPointF(4, 6), QPointF(40, 60))
    other = _mouse_event(QEvent.Type.MouseButtonPress, Qt.MouseButton.RightButton, QPointF(1, 1), QPointF(2, 2))

    box.mousePressEvent(other)
    assert box.moving is None

    box.mousePressEvent(press)
    assert box.moving is True
    assert box.offset == QPointF(4, 6)

    move = _mouse_event(QEvent.Type.MouseMove, Qt.MouseButton.LeftButton, QPointF(0, 0), QPointF(24, 36))
    box.mouseMoveEvent(move)

    assert box.pos() == (QPointF(24, 36) - QPointF(4, 6)).toPoint()
