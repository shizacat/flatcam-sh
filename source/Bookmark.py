
from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6 import QtGui, QtCore, QtWidgets
from appGUI.GUIElements import FCTable, FCEntry, FCButton, FCFileSaveDialog, GLay, FCLabel

import sys
import webbrowser

from copy import deepcopy
from datetime import datetime as dt

import gettext
import appTranslation as fcTranslate
import builtins

if TYPE_CHECKING:
    from appMain import App

fcTranslate.apply_language('strings')
if '_' not in builtins.__dict__:
    _ = gettext.gettext


class BookmarkManager(QtWidgets.QWidget):
    """Edits the Help-menu bookmarks stored in the application options."""

    # mark_rows = QtCore.pyqtSignal()

    def __init__(
        self,
        app: App,
        storage: dict[str, list[str]],
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        """
        Builds the bookmark table and the controls that edit it.

        :param app:     application that owns the Help menu and the options
        :param storage: bookmarks keyed by order; each value is a title and a web link
        :param parent:  Qt parent widget
        """
        super(BookmarkManager, self).__init__(parent)

        self.app = app

        assert isinstance(storage, dict), "Storage argument is not a dictionary"

        self.bm_dict = deepcopy(storage)

        # layouts
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        table_hlay = QtWidgets.QHBoxLayout()
        layout.addLayout(table_hlay)

        self.table_widget = FCTable(drag_drop=True, protected_rows=[0, 1])
        self.table_widget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table_hlay.addWidget(self.table_widget)

        self.table_widget.setColumnCount(3)
        self.table_widget.setColumnWidth(0, 20)
        self.table_widget.setHorizontalHeaderLabels(
            [
                '#',
                _('Title'),
                _('Web Link')
            ]
        )
        self.table_widget.horizontalHeaderItem(0).setToolTip(
            _("Index.\n"
              "The rows in gray color will populate the Bookmarks menu.\n"
              "The number of gray colored rows is set in Preferences."))
        self.table_widget.horizontalHeaderItem(1).setToolTip(
            _("Description of the link that is set as an menu action.\n"
              "Try to keep it short because it is installed as a menu item."))
        self.table_widget.horizontalHeaderItem(2).setToolTip(
            _("Web Link. E.g: https://your_website.org "))

        # New Bookmark
        new_vlay = QtWidgets.QVBoxLayout()
        layout.addLayout(new_vlay)

        new_title_lbl = FCLabel('%s' % _("New Bookmark"), bold=True)
        new_vlay.addWidget(new_title_lbl)

        grid0 = GLay(v_spacing=5, h_spacing=3)
        new_vlay.addLayout(grid0)

        title_lbl = FCLabel('%s:' % _("Title"))
        self.title_entry = FCEntry()
        grid0.addWidget(title_lbl, 0, 0)
        grid0.addWidget(self.title_entry, 0, 1)

        link_lbl = FCLabel('%s:' % _("Web Link"))
        self.link_entry = FCEntry()
        self.link_entry.set_value('http://')
        grid0.addWidget(link_lbl, 2, 0)
        grid0.addWidget(self.link_entry, 2, 1)

        # Buttons Layout
        button_hlay = QtWidgets.QHBoxLayout()
        layout.addLayout(button_hlay)

        add_entry_btn = FCButton(_("Add Entry"))
        remove_entry_btn = FCButton(_("Remove Entry"))
        export_list_btn = FCButton(_("Export List"))
        import_list_btn = FCButton(_("Import List"))

        button_hlay.addWidget(add_entry_btn)
        button_hlay.addWidget(remove_entry_btn)

        button_hlay.addWidget(export_list_btn)
        button_hlay.addWidget(import_list_btn)

        # ##############################################################################
        # ######################## SIGNALS #############################################
        # ##############################################################################

        add_entry_btn.clicked.connect(self.on_add_entry)
        remove_entry_btn.clicked.connect(self.on_remove_entry)
        export_list_btn.clicked.connect(self.on_export_bookmarks)
        import_list_btn.clicked.connect(self.on_import_bookmarks)
        self.title_entry.returnPressed.connect(self.on_add_entry)
        self.link_entry.returnPressed.connect(self.on_add_entry)

        self.ui_connect()
        self.build_bm_ui()

    def ui_connect(self) -> None:
        """Connects the table drag-and-drop signal to the row marker."""
        self.table_widget.drag_drop_sig.connect(self.mark_table_rows_for_actions)

    def ui_disconnect(self) -> None:
        """Disconnects the table drag-and-drop signal."""
        try:
            self.table_widget.drag_drop_sig.disconnect(self.mark_table_rows_for_actions)
        except (TypeError, AttributeError):
            pass

    def build_bm_ui(self) -> None:
        """Fills the table from the stored bookmarks and copies them into the options."""

        self.table_widget.setRowCount(len(self.bm_dict))

        nr_crt = 0
        sorted_bookmarks = sorted(list(self.bm_dict.items()), key=lambda x: int(x[0]))
        for entry, bookmark in sorted_bookmarks:
            row = nr_crt
            nr_crt += 1

            title = bookmark[0]
            weblink = bookmark[1]

            id_item = QtWidgets.QTableWidgetItem('%d' % int(nr_crt))
            # id.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.table_widget.setItem(row, 0, id_item)  # Tool name/id

            title_item = QtWidgets.QTableWidgetItem(title)
            self.table_widget.setItem(row, 1, title_item)

            weblink_txt = QtWidgets.QTextBrowser()
            weblink_txt.setOpenExternalLinks(True)
            weblink_txt.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)
            weblink_txt.document().setDefaultStyleSheet("a{ text-decoration: none; }")

            weblink_txt.setHtml('<a href=%s>%s</a>' % (weblink, weblink))

            self.table_widget.setCellWidget(row, 2, weblink_txt)

            vertical_header = self.table_widget.verticalHeader()
            vertical_header.hide()

            horizontal_header = self.table_widget.horizontalHeader()
            horizontal_header.setMinimumSectionSize(10)
            horizontal_header.setDefaultSectionSize(70)
            horizontal_header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Fixed)
            horizontal_header.resizeSection(0, 20)
            horizontal_header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            horizontal_header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)

        self.mark_table_rows_for_actions()

        self.app.options.global_bookmarks.clear()
        for key, val in self.bm_dict.items():
            self.app.options.global_bookmarks[key] = deepcopy(val)

    def on_add_entry(self, **kwargs: str) -> str | None:
        """
        Adds a bookmark to the table and, when it fits the menu limit, to the Help menu.

        :param kwargs: optional ``title`` and ``link``; empty values are read from the form
        :return:       ``"fail"`` when the title or link is empty or already stored
        """
        if 'title' in kwargs:
            title = kwargs['title']
        else:
            title = self.title_entry.get_value()
        if title == '':
            self.app.inform.emit('[ERROR_NOTCL] %s' % _("Title entry is empty."))
            return 'fail'

        if 'link' in kwargs:
            link = kwargs['link']
        else:
            link = self.link_entry.get_value()

        if link == 'http://':
            self.app.inform.emit('[ERROR_NOTCL] %s' % _("Web link entry is empty."))
            return 'fail'

        # if 'http' not in link or 'https' not in link:
        #     link = 'http://' + link

        for bookmark in self.bm_dict.values():
            if title == bookmark[0] or link == bookmark[1]:
                self.app.inform.emit('[ERROR_NOTCL] %s' % _("Either the Title or the Weblink already in the table."))
                return 'fail'

        # for some reason if the last char in the weblink is a slash it does not make the link clickable
        # so I remove it
        if link[-1] == '/':
            link = link[:-1]
        # add the new entry to storage
        new_entry = len(self.bm_dict) + 1
        self.bm_dict[str(new_entry)] = [title, link]

        # add the link to the menu but only if it is within the set limit
        bm_limit = int(self.app.options.global_bookmarks_limit)
        if len(self.bm_dict) < bm_limit:
            act = QtGui.QAction(parent=self.app.ui.menuhelp_bookmarks)
            act.setText(title)
            act.setIcon(QtGui.QIcon(self.app.resource_location + '/link16.png'))
            act.triggered.connect(lambda: webbrowser.open(link))
            self.app.ui.menuhelp_bookmarks.insertAction(self.app.ui.menuhelp_bookmarks_manager, act)

        self.app.inform.emit('[success] %s' % _("Bookmark added."))

        # add the new entry to the bookmark manager table
        self.build_bm_ui()

    def on_remove_entry(self) -> None:
        """Removes the selected bookmark from the table and from the Help menu."""
        index_list = []
        for model_index in self.table_widget.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)
            title_to_remove = self.table_widget.item(model_index.row(), 1).text()

            if title_to_remove == 'FlatCAM' or title_to_remove == _('Backup Site'):
                self.app.inform.emit('[WARNING_NOTCL] %s.' % _("This bookmark can not be removed"))
                self.build_bm_ui()
                return
            else:
                for k, bookmark in list(self.bm_dict.items()):
                    if title_to_remove == bookmark[0]:
                        # remove from the storage
                        self.bm_dict.pop(k, None)

                        for act in self.app.ui.menuhelp_bookmarks.actions():
                            if act.text() == title_to_remove:
                                # disconnect the signal
                                try:
                                    act.triggered.disconnect()
                                except TypeError:
                                    pass
                                # remove the action from the menu
                                self.app.ui.menuhelp_bookmarks.removeAction(act)

        # house keeping: it pays to have keys increased by one
        new_key = 0
        new_dict = {}
        for k, v in self.bm_dict.items():
            # we start with key 1 so we can use the len(self.bm_dict)
            # when adding bookmarks (keys in bm_dict)
            new_key += 1
            new_dict[str(new_key)] = v

        self.bm_dict = deepcopy(new_dict)
        new_dict.clear()

        self.app.inform.emit('[success] %s' % _("Bookmark removed."))

        self.build_bm_ui()

    def on_export_bookmarks(self) -> None:
        """Writes the stored bookmarks to a text file chosen by the user."""
        self.app.settings.report_usage("on_export_bookmarks")
        self.app.log.debug("on_export_bookmarks()")

        date = str(dt.today()).rpartition('.')[0]
        date = ''.join(c for c in date if c not in ':-')
        date = date.replace(' ', '_')

        filter__ = "Text File (*.TXT);;All Files (*.*)"
        filename, _f = FCFileSaveDialog.get_saved_filename(
            caption=_("Export Bookmarks"),
            directory='{l_save}/{n}_{date}'.format(l_save=str(self.app.get_last_save_folder()),
                                                   n=_("Bookmarks"),
                                                   date=date),
            ext_filter=filter__)

        filename = str(filename)

        if filename == "":
            self.app.inform.emit('[WARNING_NOTCL] %s' % _("Cancelled."))
            return
        else:
            try:
                f = open(filename, 'w')
                f.close()
            except PermissionError:
                self.app.inform.emit('[WARNING] %s' %
                                     _("Permission denied, saving not possible.\n"
                                       "Most likely another app is holding the file open and not accessible."))
                return
            except IOError:
                self.app.log.debug('Creating a new bookmarks file ...')
                f = open(filename, 'w')
                f.close()
            except Exception:
                e = sys.exc_info()[0]
                self.app.log.error("Could not load the file.")
                self.app.log.error(str(e))
                self.app.inform.emit('[ERROR_NOTCL] %s' % _("Could not load the file."))
                return

            # Save Bookmarks to a file
            try:
                with open(filename, "w") as f:
                    for title, link in self.bm_dict.items():
                        line2write = str(title) + ':' + str(link) + '\n'
                        f.write(line2write)
            except Exception:
                self.app.inform.emit('[ERROR_NOTCL] %s' % _("Failed to write bookmarks to file."))
                return
        self.app.inform.emit('[success] %s: %s' % (_("Exported bookmarks to"), filename))

    def on_import_bookmarks(self) -> None:
        """Reads bookmarks from a text file and adds each line to the table."""
        self.app.log.debug("on_import_bookmarks()")

        filter_ = "Text File (*.txt);;All Files (*.*)"
        filename, _f = QtWidgets.QFileDialog.getOpenFileName(caption=_("Import Bookmarks"), filter=filter_)

        filename = str(filename)

        if filename == "":
            self.app.inform.emit('[WARNING_NOTCL] %s' % _("Cancelled."))
        else:
            try:
                with open(filename) as f:
                    bookmarks = f.readlines()
            except IOError:
                self.app.log.error("Could not load bookmarks file.")
                self.app.inform.emit('[ERROR_NOTCL] %s' % _("Could not load the file."))
                return

            for line in bookmarks:
                proc_line = line.replace(' ', '').partition(':')
                self.on_add_entry(title=proc_line[0], link=proc_line[2])

            self.app.inform.emit('[success] %s: %s' % (_("Imported Bookmarks from"), filename))

    def mark_table_rows_for_actions(self) -> None:
        """Paints the rows that are installed in the Help menu."""
        for row in range(self.table_widget.rowCount()):
            item_to_paint = self.table_widget.item(row, 0)
            if row < self.app.options.global_bookmarks_limit:
                item_to_paint.setBackground(QtGui.QColor('gray'))
                # item_to_paint.setForeground(QtGui.QColor('black'))
            else:
                item_to_paint.setBackground(QtGui.QColor('white'))
                # item_to_paint.setForeground(QtGui.QColor('black'))

    def rebuild_actions(self) -> None:
        """Rebuilds the stored bookmarks from the table order and reinstalls the menu actions."""
        # rebuild the storage to reflect the order of the lines
        self.bm_dict.clear()
        for row in range(self.table_widget.rowCount()):
            title = self.table_widget.item(row, 1).text()
            wlink = self.table_widget.cellWidget(row, 2).toPlainText()

            entry = int(row) + 1
            self.bm_dict.update(
                {
                    str(entry): [title, wlink]
                }
            )

        self.app.install_bookmarks(book_dict=self.bm_dict)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        """
        Rebuilds the menu actions and closes the widget.

        :param event: Qt close event
        """
        self.rebuild_actions()
        self.ui_disconnect()
        super().closeEvent(event)
