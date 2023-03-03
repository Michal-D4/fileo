from PyQt6.QtCore import Qt, QPoint, QSize, QDateTime, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QKeySequence, QShortcut, QTextCursor
from PyQt6.QtWidgets import (QWidget, QFrame, QFormLayout, QLabel,
    QLineEdit, QHBoxLayout, QVBoxLayout, QComboBox, QCompleter,
    QToolButton, QSizePolicy, QSpacerItem, QPlainTextEdit, QMenu,
    QApplication,
)

from core import app_globals as ag, db_ut, icons

def left_comma(pos: int, txt: str) -> int:
    comma_pos = txt[:pos].rfind(',')
    return 0 if comma_pos == -1 else comma_pos+2

def right_comma(pos: int, txt: str) -> int:
    comma_pos = txt[pos:].find(',')
    return len(txt) if comma_pos == -1 else pos + comma_pos


class fileInfo(QWidget):
    file_info_close = pyqtSignal()

    def __init__(self, parent = None) -> None:
        super().__init__(parent)

        self.id = 0        # file id

        self.form_layout = QFormLayout()
        self.form = QFrame(self)
        self.file_authors = QPlainTextEdit()
        self.combo = QComboBox()

        self.form_setup()
        self.populate_fields()
        self.populate_file_authors()
        self.populate_combo()

        self.setStyleSheet(ag.dyn_qss["dialog"][0])
        self.adjustSize()

        self.start_move_pos = QPoint(0,0)
        self.mouseMoveEvent = self.move_self

        escape = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape.activated.connect(self.to_close)

        del_ = QShortcut(QKeySequence(Qt.Key.Key_Delete), self.file_authors)
        del_.activated.connect(self.delete_link)

        self.combo.currentIndexChanged.connect(self.new_choice)
        self.file_authors.mousePressEvent = self.select_on_click

        self.file_authors.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_authors.customContextMenuRequested.connect(self.custom_menu)
        # self.file_authors.setOpenLinks(False)

    def to_close(self):
        self.file_info_close.emit()
        self.close()

    def custom_menu(self, pos):
        menu = QMenu(self)
        menu.addAction("Delete selected")
        menu.addAction("Copy selected")
        menu.addSeparator()
        menu.addAction("Copy all")
        action = menu.exec(self.file_authors.mapToGlobal(pos))
        if action:
            {'Delete selected': self.delete_link,
             'Copy selected': self.copy_selected,
             'Copy all': self.copy_all
            }[action.text()]()

    def copy_selected(self):
        curs = self.file_authors.textCursor()
        QApplication.clipboard().setText(curs.selectedText())

    def copy_all(self):
        QApplication.clipboard().setText(self.file_authors.toPlainText())

    def delete_link(self):
        curs = self.file_authors.textCursor()
        if curs.hasSelection():
            txt = curs.selectedText()
            i = self.combo.findText(txt, Qt.MatchFlag.MatchExactly)
            if i == -1:
                return
            id = self.combo.itemData(i, Qt.ItemDataRole.UserRole)
            db_ut.break_file_authors_link(self.id, id)
            self.populate_file_authors()

    def select_on_click(self, e: QMouseEvent):
        pos = e.pos()
        txt_curs_at_click = self.file_authors.cursorForPosition(pos)
        self.file_authors.setTextCursor(txt_curs_at_click)
        text_pos = self.file_authors.textCursor().position()
        self.select_author_under_pos(text_pos)

    def select_author_under_pos(self, pos: int):
        txt = self.file_authors.toPlainText()
        left = left_comma(pos, txt)
        right = right_comma(pos, txt)

        curs = self.file_authors.textCursor()
        curs.movePosition(
            QTextCursor.MoveOperation.PreviousCharacter,
            QTextCursor.MoveMode.MoveAnchor, pos-left
        )
        curs.movePosition(
            QTextCursor.MoveOperation.NextCharacter,
            QTextCursor.MoveMode.KeepAnchor, right-left
        )

        self.file_authors.setTextCursor(curs)

    def form_setup(self):
        h_layout = QHBoxLayout()
        lbl = QLabel()
        lbl.setText("File info")
        lbl.setObjectName("hdr_lbl")
        h_layout.addWidget(lbl)

        h_layout.setContentsMargins(9, 6, 9, 6)
        h_layout.addSpacerItem(
            QSpacerItem(80, 10,
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Minimum)
        )
        close_btn = QToolButton()
        close_btn.setAutoRaise(True)
        close_btn.setIcon(icons.get_other_icon("remove_btn")[0])
        close_btn.clicked.connect(self.to_close)
        close_btn.setToolTip("Close (Esc)")
        h_layout.addWidget(close_btn)

        hdr = QFrame(self)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        hdr.setSizePolicy(sizePolicy)
        hdr.setObjectName("hrdFrame")
        hdr.setLayout(h_layout)
        hdr.setStyleSheet(ag.dyn_qss["dialog_hdr"][0])

        self.form_layout.setContentsMargins(9, 0, 9, 9)
        self.form_layout.addRow(QLabel("File name:"), QLabel())
        self.form_layout.addRow(QLabel("Path:"), QLabel())
        self.form_layout.addRow(QLabel("Last opened date:"), QLabel())
        self.form_layout.addRow(QLabel("Modified date:"), QLabel())
        self.form_layout.addRow(QLabel("Created date:"), QLabel())
        self.form_layout.addRow(QLabel("Publication date(book):"), QLabel())
        self.form_layout.addRow(QLabel("Number of file openings:"), QLabel())
        self.form_layout.addRow(QLabel("Size of file:"), QLabel())
        self.form_layout.addRow(QLabel("Pages(book):"), QLineEdit())

        self.file_authors.setPlaceholderText(
            "The author(s) will appear here if entered or chosen in the combobox below"
        )
        self.file_authors.setReadOnly(True)
        self.file_authors.setMaximumSize(QSize(16777215, 50))
        self.form_layout.addRow(QLabel("Author(s)(book):"), self.file_authors)
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        self.form_layout.addRow(QLabel("Author selector:"), self.combo)

        v_layout0 =  QVBoxLayout()
        v_layout0.setContentsMargins(0, 0, 0, 0)
        v_layout0.addWidget(hdr)
        v_layout0.addLayout(self.form_layout)

        self.form.setObjectName("form")
        self.form.setLayout(v_layout0)

        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.form)

    def populate_file_authors(self):
        """
        from authors table
        """
        fa_curs = db_ut.get_file_authors(self.id)
        file_authors = []
        for author in fa_curs:
            file_authors.append(author[0])
        self.file_authors.setPlainText(', '.join(file_authors))

    def populate_combo(self):
        a_curs = db_ut.get_authors()
        for author, udat in a_curs:
            self.combo.addItem(author, udat)

    def populate_fields(self):
        """
        populate all fields
        except QComboBox from authors table
        """
        idx = ag.file_list.currentIndex()
        u_dat: ag.FileData = idx.data(Qt.ItemDataRole.UserRole)
        if u_dat:
            self.id = u_dat.id
            fields = db_ut.get_file_info(self.id)
            if not fields:
                return
            for i,field in enumerate(fields):
                if i >= 2 and i <= 5:
                    field = self.time_value(field)
                self.form_layout.itemAt(
                    i, QFormLayout.ItemRole.FieldRole
                    ).widget().setText(str(field))

    def time_value(self, val: int) -> str:
        a = QDateTime()
        a.setSecsSinceEpoch(val)
        return a.toString("dd/MM/yyyy hh:mm")

    def new_choice(self, idx: int):
        """
        add link author-file for the current file
        """
        author = self.combo.currentText()
        if not self.fill_file_authors(author):       # author already exists
            return

        # create new author
        id = db_ut.add_author(self.id, author)
        if id:
            self.combo.addItem(author, id)
            ag.signals_.user_action_signal.emit("author inserted")

    def fill_file_authors(self, author: str) -> bool:
        txt = self.file_authors.toPlainText()
        authors = txt.split(', ') if txt else []
        if author in authors:
            return False
        authors.append(author)
        authors.sort()
        self.file_authors.setPlainText(', '.join(authors))
        return True

    def move_self(self, e: QMouseEvent):
        if e.buttons() == Qt.MouseButton.LeftButton:
            pos_ = e.globalPosition().toPoint()
            dist = pos_ - self.start_move_pos
            if dist.manhattanLength() < 50:
                self.move(self.pos() + dist)
                e.accept()
            self.start_move_pos = pos_
