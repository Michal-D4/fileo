# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\src\fileo\widgets\notes.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_FileNotes(object):
    def setupUi(self, FileNotes):
        FileNotes.setObjectName("FileNotes")
        FileNotes.resize(544, 44)
        self.verticalLayout = QtWidgets.QVBoxLayout(FileNotes)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.header = QtWidgets.QFrame(FileNotes)
        self.header.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.header.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.header.setObjectName("header")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.header)
        self.horizontalLayout.setContentsMargins(9, 0, 9, 0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.title = QtWidgets.QLabel(self.header)
        self.title.setObjectName("title")
        self.horizontalLayout.addWidget(self.title)
        self.tagEdit = QtWidgets.QLineEdit(self.header)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tagEdit.sizePolicy().hasHeightForWidth())
        self.tagEdit.setSizePolicy(sizePolicy)
        self.tagEdit.setFrame(False)
        self.tagEdit.setReadOnly(True)
        self.tagEdit.setObjectName("tagEdit")
        self.horizontalLayout.addWidget(self.tagEdit)
        self.add = QtWidgets.QToolButton(self.header)
        self.add.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.add.setAutoRaise(True)
        self.add.setObjectName("add")
        self.horizontalLayout.addWidget(self.add)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addWidget(self.header)
        self.labels = QtWidgets.QFrame(FileNotes)
        self.labels.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.labels.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.labels.setObjectName("labels")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.labels)
        self.horizontalLayout_3.setContentsMargins(9, 0, 9, 0)
        self.horizontalLayout_3.setSpacing(32)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.l_tags = QtWidgets.QLabel(self.labels)
        self.l_tags.setObjectName("l_tags")
        self.horizontalLayout_3.addWidget(self.l_tags)
        self.l_authors = QtWidgets.QLabel(self.labels)
        self.l_authors.setObjectName("l_authors")
        self.horizontalLayout_3.addWidget(self.l_authors)
        self.l_locations = QtWidgets.QLabel(self.labels)
        self.l_locations.setObjectName("l_locations")
        self.horizontalLayout_3.addWidget(self.l_locations)
        self.l_file_info = QtWidgets.QLabel(self.labels)
        self.l_file_info.setObjectName("l_file_info")
        self.horizontalLayout_3.addWidget(self.l_file_info)
        self.l_comments = QtWidgets.QLabel(self.labels)
        self.l_comments.setObjectName("l_comments")
        self.horizontalLayout_3.addWidget(self.l_comments)
        spacerItem = QtWidgets.QSpacerItem(562, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.btns_lbl = QtWidgets.QFrame(self.labels)
        self.btns_lbl.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.btns_lbl.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.btns_lbl.setObjectName("btns_lbl")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.btns_lbl)
        self.horizontalLayout_2.setContentsMargins(-1, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.plus = QtWidgets.QToolButton(self.btns_lbl)
        self.plus.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.plus.setAutoRaise(True)
        self.plus.setObjectName("plus")
        self.horizontalLayout_2.addWidget(self.plus)
        self.horizontalLayout_3.addWidget(self.btns_lbl)
        self.verticalLayout.addWidget(self.labels)

        self.retranslateUi(FileNotes)
        QtCore.QMetaObject.connectSlotsByName(FileNotes)

    def retranslateUi(self, FileNotes):
        _translate = QtCore.QCoreApplication.translate
        FileNotes.setWindowTitle(_translate("FileNotes", "Form"))
        self.title.setText(_translate("FileNotes", "TextLabel"))
        self.tagEdit.setPlaceholderText(_translate("FileNotes", "enter file tags here (comma separated) or double click to select from list"))
        self.add.setToolTip(_translate("FileNotes", "add note"))
        self.add.setText(_translate("FileNotes", "..."))
        self.l_tags.setText(_translate("FileNotes", "Tag selector"))
        self.l_authors.setText(_translate("FileNotes", "Author selector"))
        self.l_locations.setText(_translate("FileNotes", "Locations"))
        self.l_file_info.setText(_translate("FileNotes", "File info"))
        self.l_comments.setText(_translate("FileNotes", "Comments"))
        self.plus.setToolTip(_translate("FileNotes", "add note"))
        self.plus.setText(_translate("FileNotes", "..."))
