# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\tmp\src\widgets\open_db.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_openDB(object):
    def setupUi(self, openDB):
        openDB.setObjectName("openDB")
        openDB.resize(268, 210)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(openDB)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frameDB = QtWidgets.QFrame(openDB)
        self.frameDB.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frameDB.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.frameDB.setLineWidth(3)
        self.frameDB.setObjectName("frameDB")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frameDB)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.select_db = QtWidgets.QFrame(self.frameDB)
        self.select_db.setObjectName("select_db")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.select_db)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.input_path = QtWidgets.QLineEdit(self.select_db)
        self.input_path.setText("")
        self.input_path.setPlaceholderText("Enter path to open or to create database. Esc - to close without choice")
        self.input_path.setObjectName("input_path")
        self.horizontalLayout.addWidget(self.input_path)
        self.open_btn = QtWidgets.QToolButton(self.select_db)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(22)
        sizePolicy.setVerticalStretch(22)
        sizePolicy.setHeightForWidth(self.open_btn.sizePolicy().hasHeightForWidth())
        self.open_btn.setSizePolicy(sizePolicy)
        self.open_btn.setMinimumSize(QtCore.QSize(22, 22))
        self.open_btn.setText("")
        self.open_btn.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.open_btn.setAutoRaise(True)
        self.open_btn.setObjectName("open_btn")
        self.horizontalLayout.addWidget(self.open_btn)
        self.verticalLayout.addWidget(self.select_db)
        self.listDB = QtWidgets.QListWidget(self.frameDB)
        self.listDB.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listDB.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listDB.setDefaultDropAction(QtCore.Qt.DropAction.IgnoreAction)
        self.listDB.setViewMode(QtWidgets.QListView.ViewMode.ListMode)
        self.listDB.setItemAlignment(QtCore.Qt.AlignmentFlag.AlignLeading)
        self.listDB.setObjectName("listDB")
        self.verticalLayout.addWidget(self.listDB)
        self.verticalLayout_2.addWidget(self.frameDB)

        self.retranslateUi(openDB)
        QtCore.QMetaObject.connectSlotsByName(openDB)

    def retranslateUi(self, openDB):
        _translate = QtCore.QCoreApplication.translate
        openDB.setWindowTitle(_translate("openDB", "Form"))
        self.listDB.setSortingEnabled(True)