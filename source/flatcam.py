
import argparse
import sys
import os
import traceback
from datetime import datetime

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import QSettings, QTimer
from appMain import App
from appGUI import VisPyPatches

from appGUI.GUIElements import FCMessageBox

from multiprocessing import freeze_support

MIN_VERSION_MAJOR = 3
MIN_VERSION_MINOR = 6


def debug_trace():
    """
    Set a tracepoint in the Python debugger that works with Qt
    :return: None
    """
    from PyQt6.QtCore import pyqtRemoveInputHook
    # from pdb import set_trace
    pyqtRemoveInputHook()
    # set_trace()


def parse_command_line(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Reads the application command-line options.

    :param argv: arguments without the program name; ``sys.argv[1:]`` when omitted
    :return: parsed options; ``args`` holds the files to open
    """
    if argv is None:
        argv = sys.argv[1:]

    def eval_command_line_value(value: str):
        try:
            return eval(value)
        except NameError:
            return None

    parser = argparse.ArgumentParser(prog="FlatCam.py")
    parser.add_argument(
        "--shellfile",
        default="",
        metavar="file",
        help="Tcl script to run at startup",
    )
    parser.add_argument(
        "--shellvar",
        default="",
        metavar="values",
        help="comma-separated values exposed to the Tcl shell as shellvar_0, shellvar_1, ...",
    )
    parser.add_argument(
        "--headless",
        default=None,
        type=eval_command_line_value,
        metavar="value",
        help="1 runs without showing the main window",
    )
    # Multiprocessing pool will spawn additional processes with 'multiprocessing-fork' flag
    parser.add_argument("--multiprocessing-fork", default=None, help=argparse.SUPPRESS)
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        metavar="file",
        help="project, preferences, or script files to open",
    )

    parsed = parser.parse_args(argv)
    if parsed.args[:1] == ["--"]:
        parsed.args = parsed.args[1:]
    return parsed


def set_macos_app_name(name):
    """
    Sets the application name shown in the macOS menu bar when running from sources.

    macOS takes the name next to the Apple menu from the main bundle's ``CFBundleName``;
    for a bare interpreter there is none and the executable name (``python``) is shown.
    The bundled ``FlatCAM.app`` already has the key in its ``Info.plist``, so a frozen
    build is left untouched. Must be called before the ``QApplication`` is created.

    :param name:    the name to show in the menu bar
    """
    if sys.platform != 'darwin' or getattr(sys, 'frozen', False):
        return

    import ctypes
    import ctypes.util

    try:
        cf = ctypes.CDLL(ctypes.util.find_library('CoreFoundation'))
        cf.CFBundleGetMainBundle.restype = ctypes.c_void_p
        cf.CFBundleGetInfoDictionary.restype = ctypes.c_void_p
        cf.CFBundleGetInfoDictionary.argtypes = [ctypes.c_void_p]
        cf.CFStringCreateWithCString.restype = ctypes.c_void_p
        cf.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
        cf.CFDictionarySetValue.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        k_cf_string_encoding_utf8 = 0x08000100

        info = cf.CFBundleGetInfoDictionary(cf.CFBundleGetMainBundle())
        if not info:
            return
        key = cf.CFStringCreateWithCString(None, b'CFBundleName', k_cf_string_encoding_utf8)
        value = cf.CFStringCreateWithCString(None, name.encode('utf-8'), k_cf_string_encoding_utf8)
        cf.CFDictionarySetValue(info, key, value)
    except (OSError, AttributeError):
        # cosmetic only; never prevent the application from starting
        pass


if __name__ == '__main__':
    # All X11 calling should be thread safe otherwise we have strange issues
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    # NOTE: Never talk to the GUI from threads! This is why I commented the above.
    freeze_support()
    command_line = parse_command_line(sys.argv[1:])

    portable = False
    # Folder for user settings.
    if sys.platform == 'win32':
        # #######################################################################################################
        # ####### CONFIG FILE WITH PARAMETERS REGARDING PORTABILITY #############################################
        # #######################################################################################################
        config_file = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '\\config\\configuration.txt'
        try:
            with open(config_file, 'r'):
                pass
        except FileNotFoundError:
            config_file = os.path.dirname(os.path.realpath(__file__)) + '\\config\\configuration.txt'

        with open(config_file, 'r') as f:
            for line in f:
                param = str(line).replace('\n', '').rpartition('=')

                if param[0] == 'portable':
                    try:
                        portable = eval(param[2])
                    except NameError:
                        portable = False

        if portable is False:
            # data_path = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, None, 0) + '\\FlatCAM'
            data_path = os.path.join(os.getenv('appdata'), 'FlatCAM')
        else:
            data_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '\\config'
    else:
        data_path = os.path.expanduser('~') + '/.FlatCAM'

    if not os.path.exists(data_path):
        os.makedirs(data_path)

    log_file_path = os.path.join(data_path, "log.txt")

    major_v = sys.version_info.major
    minor_v = sys.version_info.minor

    v_msg = "FlatCAM Evo uses PYTHON 3 or later. The version minimum is %s.%s\n"\
            "Your Python version is: %s.%s" % (MIN_VERSION_MAJOR, MIN_VERSION_MINOR, str(major_v), str(minor_v))

    # Supported Python version is >= 3.6
    if major_v < MIN_VERSION_MAJOR or (major_v >= MIN_VERSION_MAJOR and minor_v < MIN_VERSION_MINOR):
        print(v_msg)
        msg = '%s\n' % str(datetime.today())
        msg += v_msg

        try:
            with open(log_file_path) as f:
                log_file = f.read()
            log_file += '\n' + msg

            with open(log_file_path, 'w') as f:
                f.write(log_file)
        except IOError:
            with open(log_file_path, 'w') as f:
                f.write(msg)

        # if minor_v >= 8:
        #     os._exit(0)
        # else:
        #     sys.exit(0)
        sys.exit(0)

    debug_trace()
    VisPyPatches.apply_patches()

    def excepthook(exc_type, exc_value, exc_tb):
        msg = '%s\n' % str(datetime.today())
        if exc_type != KeyboardInterrupt:
            msg += "".join(traceback.format_exception(exc_type, exc_value, exc_tb))

            try:
                with open(log_file_path) as f:
                    log_file = f.read()
                log_file += '\n' + msg

                with open(log_file_path, 'w') as f:
                    f.write(log_file)
            except IOError:
                with open(log_file_path, 'w') as f:
                    f.write(msg)

            # show the message
            try:
                msgbox = FCMessageBox()
                displayed_msg = "The application encountered a critical error and it will close.\n"\
                                "Please report this error to the developers."
                title = "Critical Error"
                msgbox.setWindowTitle(title)  # taskbar still shows it
                ic = QtGui.QIcon()
                ic.addPixmap(QtGui.QPixmap("assets/resources/warning.png"), QtGui.QIcon.Mode.Normal)
                msgbox.setWindowIcon(ic)
                msgbox.setText('<b>%s</b>' % displayed_msg)
                msgbox.setDetailedText(msg)
                msgbox.setIcon(QtWidgets.QMessageBox.Icon.Critical)

                bt_yes = msgbox.addButton("Quit", QtWidgets.QMessageBox.ButtonRole.YesRole)
                bt_ret = msgbox.addButton("Return", QtWidgets.QMessageBox.ButtonRole.NoRole)

                msgbox.setDefaultButton(bt_yes)
                # msgbox.setTextFormat(Qt.TextFormat.RichText)
                msgbox.exec()

                response = msgbox.clickedButton()
                if response == bt_ret:
                    pass
            except Exception:
                QtWidgets.QApplication.quit()
        else:
            QtWidgets.QApplication.quit()
        # or QtWidgets.QApplication.exit(0)

    sys.excepthook = excepthook

    set_macos_app_name('FlatCAM')
    app = QtWidgets.QApplication(sys.argv)

    # apply style
    settings = QSettings("Open Source", "FlatCAM_EVO")
    if settings.contains("style"):
        style_index = settings.value('style', type=str)
        try:
            idx = int(style_index)
        except Exception:
            idx = 0
        style = QtWidgets.QStyleFactory.keys()[idx]
        app.setStyle(style)
    else:
        app.setStyle('windowsvista')

    if settings.contains("font_size"):
        font_size = int(settings.value("font_size", type=str))      # noqa
        font = QtGui.QFont()
        font.setPointSize(font_size)
        app.setFont(font)

    fc = App(
        qapp=app,
        shellfile=command_line.shellfile,
        shellvar=command_line.shellvar,
        headless=command_line.headless,
        startup_args=command_line.args,
    )

    # interrupt the Qt loop such that Python events have a chance to be responsive
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    try:
        sys.exit(app.exec())
    except SystemError:
        pass
    # app.exec()
