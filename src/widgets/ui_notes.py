# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\src\widgets\notes.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_FileNotes(object):
    def setupUi(self, FileNotes):
        FileNotes.setObjectName("FileNotes")
        FileNotes.resize(728, 46)
        self.main_layout = QtWidgets.QVBoxLayout(FileNotes)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setObjectName("main_layout")
        self.head = QtWidgets.QFrame(parent=FileNotes)
        self.head.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.head.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.head.setObjectName("head")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.head)
        self.horizontalLayout.setContentsMargins(0, 0, 9, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.authorEdit = QtWidgets.QLineEdit(parent=self.head)
        self.authorEdit.setFrame(False)
        self.authorEdit.setObjectName("authorEdit")
        self.horizontalLayout.addWidget(self.authorEdit)
        self.tagEdit = QtWidgets.QLineEdit(parent=self.head)
        self.tagEdit.setFrame(False)
        self.tagEdit.setObjectName("tagEdit")
        self.horizontalLayout.addWidget(self.tagEdit)
        self.srch_in_notes = QtWidgets.QToolButton(parent=self.head)
        self.srch_in_notes.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.srch_in_notes.setAutoRaise(True)
        self.srch_in_notes.setObjectName("srch_in_notes")
        self.horizontalLayout.addWidget(self.srch_in_notes)
        self.expand = QtWidgets.QToolButton(parent=self.head)
        self.expand.setCheckable(True)
        self.expand.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.expand.setAutoRaise(True)
        self.expand.setObjectName("expand")
        self.horizontalLayout.addWidget(self.expand)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.main_layout.addWidget(self.head)
        self.labels = QtWidgets.QFrame(parent=FileNotes)
        self.labels.setMinimumSize(QtCore.QSize(0, 24))
        self.labels.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.labels.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.labels.setObjectName("labels")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.labels)
        self.horizontalLayout_3.setContentsMargins(9, 0, 9, 0)
        self.horizontalLayout_3.setSpacing(20)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.l_tags = QtWidgets.QLabel(parent=self.labels)
        self.l_tags.setIndent(0)
        self.l_tags.setObjectName("l_tags")
        self.horizontalLayout_3.addWidget(self.l_tags)
        self.l_authors = QtWidgets.QLabel(parent=self.labels)
        self.l_authors.setIndent(0)
        self.l_authors.setObjectName("l_authors")
        self.horizontalLayout_3.addWidget(self.l_authors)
        self.l_locations = QtWidgets.QLabel(parent=self.labels)
        self.l_locations.setIndent(0)
        self.l_locations.setObjectName("l_locations")
        self.horizontalLayout_3.addWidget(self.l_locations)
        self.l_file_info = QtWidgets.QLabel(parent=self.labels)
        self.l_file_info.setIndent(0)
        self.l_file_info.setObjectName("l_file_info")
        self.horizontalLayout_3.addWidget(self.l_file_info)
        self.l_file_notes = QtWidgets.QLabel(parent=self.labels)
        self.l_file_notes.setIndent(0)
        self.l_file_notes.setObjectName("l_file_notes")
        self.horizontalLayout_3.addWidget(self.l_file_notes)
        self.l_editor = QtWidgets.QLabel(parent=self.labels)
        self.l_editor.setIndent(0)
        self.l_editor.setObjectName("l_editor")
        self.horizontalLayout_3.addWidget(self.l_editor)
        spacerItem = QtWidgets.QSpacerItem(562, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.note_btns = QtWidgets.QFrame(parent=self.labels)
        self.note_btns.setMinimumSize(QtCore.QSize(0, 0))
        self.note_btns.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.note_btns.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.note_btns.setObjectName("note_btns")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.note_btns)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.plus = QtWidgets.QToolButton(parent=self.note_btns)
        self.plus.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.plus.setAutoRaise(True)
        self.plus.setObjectName("plus")
        self.horizontalLayout_4.addWidget(self.plus)
        self.collapse_notes = QtWidgets.QToolButton(parent=self.note_btns)
        self.collapse_notes.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.collapse_notes.setAutoRaise(True)
        self.collapse_notes.setObjectName("collapse_notes")
        self.horizontalLayout_4.addWidget(self.collapse_notes)
        self.horizontalLayout_3.addWidget(self.note_btns)
        self.edit_btns = QtWidgets.QFrame(parent=self.labels)
        self.edit_btns.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.edit_btns.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.edit_btns.setObjectName("edit_btns")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.edit_btns)
        self.horizontalLayout_2.setContentsMargins(-1, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.save = QtWidgets.QToolButton(parent=self.edit_btns)
        self.save.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.save.setAutoRaise(True)
        self.save.setObjectName("save")
        self.horizontalLayout_2.addWidget(self.save)
        self.cancel = QtWidgets.QToolButton(parent=self.edit_btns)
        self.cancel.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.cancel.setAutoRaise(True)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout_2.addWidget(self.cancel)
        self.horizontalLayout_3.addWidget(self.edit_btns)
        self.main_layout.addWidget(self.labels)

        self.retranslateUi(FileNotes)
        QtCore.QMetaObject.connectSlotsByName(FileNotes)

    def retranslateUi(self, FileNotes):
        _translate = QtCore.QCoreApplication.translate
        FileNotes.setWindowTitle(_translate("FileNotes", "Form"))
        self.authorEdit.setToolTip(_translate("FileNotes", "File\'s authors"))
        self.authorEdit.setPlaceholderText(_translate("FileNotes", "Enter a list of authors separated by commas or select from the \"Author selector\""))
        self.tagEdit.setToolTip(_translate("FileNotes", "File\'s tags"))
        self.tagEdit.setPlaceholderText(_translate("FileNotes", "Enter a list of tags separated by commas or select from the \"Tag selector\""))
        self.srch_in_notes.setToolTip(_translate("FileNotes", "search files by notes context, Ctrl+Shift+F"))
        self.srch_in_notes.setText(_translate("FileNotes", "..."))
        self.expand.setToolTip(_translate("FileNotes", "Maximize panel"))
        self.expand.setText(_translate("FileNotes", "..."))
        self.l_tags.setText(_translate("FileNotes", "Tag selector"))
        self.l_authors.setText(_translate("FileNotes", "Author selector"))
        self.l_locations.setText(_translate("FileNotes", "Locations"))
        self.l_file_info.setText(_translate("FileNotes", "File info"))
        self.l_file_notes.setText(_translate("FileNotes", "Notes"))
        self.l_editor.setText(_translate("FileNotes", "Note editor"))
        self.plus.setToolTip(_translate("FileNotes", "Create new note, Ctrl-N"))
        self.plus.setText(_translate("FileNotes", "..."))
        self.collapse_notes.setToolTip(_translate("FileNotes", "Collapse all notes"))
        self.collapse_notes.setText(_translate("FileNotes", "..."))
        self.save.setToolTip(_translate("FileNotes", "Save note, Ctrl-S"))
        self.save.setText(_translate("FileNotes", "..."))
        self.cancel.setToolTip(_translate("FileNotes", "Cancel editing, Ctrl-Q"))
        self.cancel.setText(_translate("FileNotes", "..."))
