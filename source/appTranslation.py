# ##########################################################
# FlatCAM: 2D Post-processing for Manufacturing            #
# File Author: Marius Adrian Stanciu (c)                   #
# Date: 3/10/2019                                          #
# MIT Licence                                              #
# ##########################################################

from __future__ import annotations

import os
import ctypes
import sys
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt

if TYPE_CHECKING:
    from appMain import App

from settings.utils import copy_shared

import gettext
import builtins
from settings.gui_settings import GuiSettings

log = logging.getLogger('base')

if '_' not in builtins.__dict__:
    _ = gettext.gettext

# ISO639-1 codes from here: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
languages_dict = {
    'zh': '简体中文',
    'de': 'Deutsche',
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'it': 'Italiano',
    'pt_BR': 'Portugues do Brasil',
    'ro': 'Română',
    'ru': 'Pусский',
    'tr': 'Türk',
}


def isAdmin() -> bool:
    """Reports whether the process is running with administrator rights."""
    try:
        is_admin = (os.getuid() == 0) or (os.geteuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def load_languages() -> dict[str, str]:
    """
    Loads the translation catalogs found under the locale directory.

    :return: language code mapped to the name shown in Preferences
    """
    locale_dir = languages_dir()
    if not locale_dir.is_dir():
        locale_dir = languages_dir_cx_freeze()

    available_translations = []
    if locale_dir.is_dir():
        available_translations = [path.name for path in locale_dir.iterdir() if path.is_dir()]

    translations: dict[str, str] = {}
    for lang in available_translations:
        try:
            if lang in languages_dict.keys():
                translations[lang] = languages_dict[lang]
        except KeyError as e:
            log.debug("FlatCAMTranslations.load_languages() --> %s" % str(e))
    return translations


def languages_dir() -> Path:
    """Returns the locale directory next to this module."""
    return Path(__file__).resolve().parent / 'locale'


def languages_dir_cx_freeze() -> Path:
    """Returns the locale directory used by a frozen build."""
    return Path(__file__).resolve().parents[1] / 'locale'


def on_language_apply_click(app: App, restart: bool = False) -> None:
    """
    Saves a newly chosen language and restarts the application when requested.

    :param app:     application that owns the language combo and the options
    :param restart: when True, ask for confirmation and restart after saving
    """
    name = app.ui.general_pref_form.general_app_group.language_combo.currentText()

    if app.options.global_theme.is_light():
        resource_loc = 'assets/resources'
    else:
        resource_loc = 'assets/resources/dark_resources'

    # do nothing if trying to apply the language that is the current language (already applied).
    if GuiSettings().language() == name:
        return

    if restart:
        msgbox = FCMessageBox(parent=app.ui)
        title = _("The application will restart.")
        txt = '%s %s?' % (_("Are you sure do you want to change the current language to"), name.capitalize())
        msgbox.setWindowTitle('%s ...' % _("Apply Language"))  # taskbar still shows it
        msgbox.setWindowIcon(QtGui.QIcon(resource_loc + '/app128.png'))
        msgbox.setText('<b>%s</b>' % title)
        msgbox.setInformativeText(txt)
        msgbox.setIconPixmap(QtGui.QPixmap(resource_loc + '/language32.png'))

        bt_yes = msgbox.addButton(_("Yes"), QtWidgets.QMessageBox.ButtonRole.YesRole)
        bt_no = msgbox.addButton(_("No"), QtWidgets.QMessageBox.ButtonRole.NoRole)

        msgbox.setDefaultButton(bt_yes)
        msgbox.exec()
        response = msgbox.clickedButton()

        if response == bt_no:
            return
        else:
            GuiSettings().save_language(name)

            restart_program(app=app)


def apply_language(domain: str, lang: str | None = None) -> str | None:
    """
    Installs a gettext translation for the application strings.

    A missing ``lang`` reads the stored language and stores English when that key is absent.

    :param domain: gettext domain, ``strings``
    :param lang:   language name from Preferences, or None to use the stored language
    :return:       the applied language name, or ``no language`` when no catalog matches
    """
    if lang is None:
        settings = GuiSettings()
        name = settings.language()
        if name is None:
            name = 'English'
            settings.save_language(name)

    else:
        name = str(lang)    # we make it a string: "None"

    lang_code = ''
    for code, lang_usable in load_languages().items():
        if lang_usable == name:
            lang_code = code
            break

    if lang_code == '':
        return "no language"

    try:
        current_lang = gettext.translation(str(domain), localedir=languages_dir(), languages=[lang_code])
        current_lang.install()
    except Exception as e:
        log.error("FlatCAMTranslation.apply_language() --> %s. Perhaps is Cx_freeze-ed?" % str(e))
        try:
            current_lang = gettext.translation(str(domain),
                                                localedir=languages_dir_cx_freeze(),
                                                languages=[lang_code])
            current_lang.install()
        except Exception as e:
            log.error("FlatCAMTranslation.apply_language() --> %s" % str(e))

    return name


def restart_program(app: App, ask: bool | None = None) -> None:
    """
    Restarts the process after saving settings.

    The call replaces the current process. Save data before calling it.

    :param app: application to shut down and restart
    :param ask: when True, ask to save the project even if nothing is marked modified
    """
    log.debug("FlatCAMTranslation.restart_program()")

    if app.options.global_theme.is_light():
        resource_loc = 'assets/resources'
    else:
        resource_loc = 'assets/resources/dark_resources'

    # try to quit the Socket opened by ArgsThread class
    try:
        app.new_launch.stop.emit()
        # app.new_launch.thread_exit = True
        # app.new_launch.listener.close()
    except Exception as err:
        log.error("FlatCAMTranslation.restart_program() --> %s" % str(err))

    # try to quit the QThread that run ArgsThread class
    try:
        app.listen_th.quit()
        app.listen_th.wait(1000)
    except Exception as err:
        log.error("FlatCAMTranslation.restart_program() --> %s" % str(err))

    if app.should_we_save and app.collection.get_list() or ask is True:
        msgbox = FCMessageBox(parent=app.ui)
        title = _("Save changes")
        txt = _("There are files/objects modified.\n"
                "Do you want to Save the project?")
        msgbox.setWindowTitle(title)  # taskbar still shows it
        msgbox.setWindowIcon(QtGui.QIcon(resource_loc + '/app128.png'))
        msgbox.setText('<b>%s</b>' % title)
        msgbox.setInformativeText(txt)
        msgbox.setIconPixmap(QtGui.QPixmap(resource_loc + '/save_as.png'))

        bt_yes = msgbox.addButton(_('Yes'), QtWidgets.QMessageBox.ButtonRole.YesRole)
        msgbox.addButton(_('No'), QtWidgets.QMessageBox.ButtonRole.NoRole)

        msgbox.setDefaultButton(bt_yes)
        msgbox.exec()
        response = msgbox.clickedButton()

        if response == bt_yes:
            app.f_handlers.on_file_save_project_as(use_thread=True, quit_action=True)

    copy_shared(app.settings, app.options)
    app.preferencesUiManager.save_defaults()

    try:
        python = sys.executable
        os.execl(python, python, *sys.argv)
    except Exception:
        # app_run_as_admin = isAdmin()
        msgbox = FCMessageBox(parent=app.ui)
        title = _("The setting will be applied at the next application start.")
        txt = _("The user does not have admin rights or UAC issues.")
        msgbox.setWindowTitle('%s ...' % _("Quit"))  # taskbar still shows it
        msgbox.setWindowIcon(QtGui.QIcon(resource_loc + '/app128.png'))
        msgbox.setText('<b>%s</b>' % title)
        msgbox.setInformativeText(txt)
        msgbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)

        bt_yes = msgbox.addButton(_("Quit"), QtWidgets.QMessageBox.ButtonRole.YesRole)

        msgbox.setDefaultButton(bt_yes)
        msgbox.exec()


# TODO Due of some circular imports issues which I currently can't fix I re-add this class here
#  (mainly is located in appGUI.GUIElements) - required for a consistent look
class FCMessageBox(QtWidgets.QMessageBox):
    """Frameless message box that can be dragged by the mouse."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Creates a frameless message box.

        :param args:   positional arguments forwarded to ``QMessageBox``
        :param kwargs: keyword arguments forwarded to ``QMessageBox``
        """
        super(FCMessageBox, self).__init__(*args, **kwargs)
        self.offset = None
        self.moving = None
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint)

        #   "background-color: palette(base); "
        self.setStyleSheet(
            "QDialog { "
            "border: 1px solid palette(shadow); "
            "}"
        )

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        Starts a window drag when the left button is pressed.

        :param event: mouse press event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.moving = True
            self.offset = event.position()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        Moves the window while the left button stays down.

        :param event: mouse move event
        """
        if self.moving:
            self.move(event.globalPosition().toPoint() - self.offset.toPoint())
