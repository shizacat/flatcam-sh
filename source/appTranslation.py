# ##########################################################
# FlatCAM: 2D Post-processing for Manufacturing            #
# File Author: Marius Adrian Stanciu (c)                   #
# Date: 3/10/2019                                          #
# MIT Licence                                              #
# ##########################################################

import os
import ctypes
import sys
import logging
from pathlib import Path

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt

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

translations = {}

languages_path_search = ''


def isAdmin():
    try:
        is_admin = (os.getuid() == 0) or (os.geteuid() == 0)
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    return is_admin


def load_languages():
    available_translations = []
    languages_path_search = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale')

    try:
        available_translations = next(os.walk(languages_path_search))[1]
    except StopIteration:
        if not available_translations:
            languages_path_search = os.path.join(str(Path(__file__).parents[1]), 'locale')
            try:
                available_translations = next(os.walk(languages_path_search))[1]
            except StopIteration:
                pass

    for lang in available_translations:
        try:
            if lang in languages_dict.keys():
                translations[lang] = languages_dict[lang]
        except KeyError as e:
            log.debug("FlatCAMTranslations.load_languages() --> %s" % str(e))
    return translations


def languages_dir():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale')


def languages_dir_cx_freeze():
    return os.path.join(Path(__file__).parents[1], 'locale')


def on_language_apply_click(app, restart=False):
    """
    Using instructions from here:
    https://inventwithpython.com/blog/2014/12/20/translate-your-python-3-program-with-the-gettext-module/

    :return:
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
    :return:       the applied language name, ``no language`` when no catalog matches,
                   or None when the catalog cannot be installed
    """
    lang_code = ''

    if lang is None:
        settings = GuiSettings()
        name = settings.language()
        if name is None:
            name = 'English'
            settings.save_language(name)

    else:
        name = str(lang)    # we make it a string: "None"

    for lang_code, lang_usable in load_languages().items():
        if lang_usable == name:
            # break and then use the current key as language
            break

    if lang_code == '':
        return "no language"
    else:
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


def restart_program(app, ask=None):
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function.
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
    """
    Frameless QMessageBox
    """

    def __init__(self, *args, **kwargs):
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

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.moving = True
            self.offset = event.position()

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPosition().toPoint() - self.offset.toPoint())
