from PyQt6.QtCore import Qt, QUrl, QRect, pyqtSignal, pyqtSlot, QPoint
from PyQt6.QtGui import (QGuiApplication, QKeySequence, QShortcut,
    QTextCursor,
)
from PyQt6.QtWidgets import (QTextBrowser, QWidget, QVBoxLayout,
    QMenu, QLineEdit, QApplication,
)

from .. import tug
from ..core import app_globals as ag

class editTag(QWidget):
    def __init__(self, text: str, parent = None) -> None:
        super().__init__(parent)
        self.setObjectName("editTag")
        self.editor = QLineEdit(self)
        self.editor.setObjectName("editor")
        self.editor.setText(text)
        self.editor.setFocus(Qt.FocusReason.OtherFocusReason)
        self.editor.setCursor(Qt.CursorShape.ArrowCursor)
        self.editor.selectAll()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.editor)
        self.setLayout(layout)

        self.adjustSize()
        self.editor.editingFinished.connect(self.finish_edit)

        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape.activated.connect(self.cancel)

    @pyqtSlot()
    def finish_edit(self):
        txt = self.editor.text().strip()
        if txt:
            self.parent().edit_item.emit(txt)
        self.parent().browser.setFocus()
        self.close()

    @pyqtSlot()
    def cancel(self):
        self.parent().browser.setFocus()
        self.close()

class aBrowser(QWidget):
    edit_item = pyqtSignal(str)
    delete_items = pyqtSignal(str)
    change_selection = pyqtSignal(list)
    list_changed = pyqtSignal()

    def __init__(self, brackets: bool=False,
        read_only: bool=True, parent=None) -> None:
        super().__init__(parent)
        self.read_only = read_only
        self.brackets = brackets

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.browser: QTextBrowser = QTextBrowser()
        self.browser.setObjectName('a_browser')
        self.browser.selectionChanged.connect(self.selection_changed)
        layout.addWidget(self.browser)
        self.setLayout(layout)

        self.browser.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self.custom_menu)
        self.browser.setOpenLinks(False)

        self.tags = {}
        self.sel_tags = []
        self._to_edit: str = ''
        self.scroll_pos = 0

        self.browser.anchorClicked.connect(self.ref_clicked)
        ag.signals_.color_theme_changed.connect(self.show_in_bpowser)

        if not self.read_only:
            f2 = QShortcut(QKeySequence(Qt.Key.Key_F2), self.browser)
            f2.setContext(Qt.ShortcutContext.WidgetShortcut)
            f2.activated.connect(self.f2_rename_tag)

    @pyqtSlot()
    def f2_rename_tag(self):
        if self._to_edit and self._to_edit not in self.sel_tags:
            return
        self.rename_tag()

    def rename_tag(self):
        """
        edit last selected tag - current tag
        """
        if not self._to_edit:
            return
        c_rect = self.get_edit_rect()
        if c_rect:
            ed = editTag(self._to_edit, self)
            ed.setGeometry(c_rect)
            ed.show()

    def get_edit_rect(self):
        start, end = self.get_start_end()
        if start.y() < end.y():   # two line selection
            w = self.browser.width()
            return QRect(
                4, end.y()+end.height(),
                w-start.x()+end.x(), end.height()
            )

        return QRect(
            start.x()+4,
            end.y()+end.height(),
            end.x()-start.x()+12,
            end.height()
        )

    def get_start_end(self):
        self.browser.find(self._to_edit)
        curs = self.browser.textCursor()

        end = self.browser.cursorRect(curs)
        curs.setPosition(curs.position() - len(self._to_edit))
        start = self.browser.cursorRect(curs)
        return start, end

    @pyqtSlot(QPoint)
    def custom_menu(self, pos):
        if not self.tags:
            return
        self.scroll_pos = self.browser.verticalScrollBar().value()
        menu = QMenu(self)
        if not self.read_only:
            self.item_to_edit(pos)
            menu.addAction('Delete selected')
            menu.addAction(f'Rename "{self._to_edit}"\tF2')
        menu.addAction('Copy selected')
        menu.addSeparator()
        menu.addAction('Select all')
        action = menu.exec(self.browser.mapToGlobal(pos))
        if action:
            choice = action.text().split('"')[0]
            {"Delete selected": self.delete_selected,
             "Rename ": self.rename_tag,
             "Copy selected": self.copy_selected,
             "Select all": self.select_all,
             }[choice]()

    def delete_selected(self):
        if not self.sel_tags:
            return
        ids = ','.join((str(id) for id in self.get_selected_ids()))
        self.delete_items.emit(ids)

    def copy_selected(self):
        tags = self.get_selected()
        QApplication.clipboard().setText(';'.join(tags))

    def set_list(self, items: list):
        self.tags.clear()
        for key, val in items:
            self.tags[key] = val
        self.show_in_bpowser()

    @pyqtSlot()
    def selection_changed(self):
        """
        I need not to show selection as text, but selection as keywords,
        so the selection is cleared whenever the user tries to do so;
        selection is doing in self.ref_clicked() method
        """
        curs = self.browser.textCursor()
        if curs.hasSelection():
            curs.clearSelection()
            self.browser.setTextCursor(curs)

    def set_selection(self, sel_ids):
        _sels = list(sel_ids)
        self.sel_tags = [key for key, val in self.tags.items() if val in _sels]
        # logger.info(f'{self.objectName()}:{self.sel_tags=}')
        self.show_in_bpowser()

    def select_all(self):
        self.sel_tags = list(self.tags.keys())
        self.show_in_bpowser()

    def get_selected_ids(self) -> list[int]:
        return sorted([self.tags[tag] for tag in self.sel_tags])

    def get_tag_id(self, tag: str) -> int:
        return self.tags.get(tag, 0)

    @pyqtSlot(QUrl)
    def ref_clicked(self, href: QUrl):
        self.scroll_pos = self.browser.verticalScrollBar().value()
        mod = QGuiApplication.keyboardModifiers()
        self.update_selected(href, mod)
        self.change_selection.emit(self.sel_tags)
        self.show_in_bpowser()

    def item_to_edit(self, pos: QPoint):
        curs: QTextCursor = self.browser.cursorForPosition(pos)
        p = curs.position()
        key = '[]' if self.brackets else '  '
        txt = self.browser.toPlainText()
        q = txt[:p].rfind(key[0]) + 1
        r = txt[q:].find(key[1])
        self._to_edit = txt[q:q+r] if r > -1 else txt[q:]

    def get_selected(self) -> list[str]:
        # logger.info(f'{self.objectName()}: {self.sel_tags=}')
        return sorted(self.sel_tags, key=str.lower)

    def get_current(self) -> str:
        return self._to_edit

    def current_id(self) -> int:
        return self.tags.get(self._to_edit, 0)

    def update_selected(self, href: QUrl, mod: Qt.KeyboardModifier):
        tref = href.toString()[1:]
        if mod is Qt.KeyboardModifier.ControlModifier:
            if tref in self.sel_tags:
                self.sel_tags.remove(tref)
                self._to_edit = self.sel_tags[-1] if len(
                    self.sel_tags) > 0 else ''
            else:
                self.sel_tags.append(tref)
                self._to_edit = tref
        else:
            if self.sel_tags == [tref]:
                self.sel_tags.clear()
                self._to_edit = ''
                return
            self.sel_tags.clear()
            self.sel_tags.append(tref)
            self._to_edit = tref

    def show_in_bpowser(self):
        self.browser.clear()
        css = tug.get_dyn_qss('browser_style')
        inn = self.html_selected()
        self.browser.setText(''.join((css, inn)))
        self.browser.verticalScrollBar().setValue(self.scroll_pos)

    def html_selected(self):
        sel = self.sel_tags
        if self.brackets:
            if sel:
                return ' '.join(f"<a class={'s' if tag in sel else 't'}"
                    f' href="#{tag}">[{tag}]</a> ' for tag in self.tags)
            return ' '.join(f'<a class t href="#{tag}">[{tag}]</a> ' for tag in self.tags)
        if sel:
            return ' '.join(f"<a class={'s' if tag in sel else 't'}"
                f' href="#{tag}">{tag}</a> ' for tag in self.tags)
        return ' '.join(f'<a class t href="#{tag}">{tag}</a> ' for tag in self.tags)
