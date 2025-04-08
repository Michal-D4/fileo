# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\src\widgets\scan_disk.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_scanDisk(object):
    def setupUi(self, scanDisk):
        scanDisk.setObjectName("scanDisk")
        scanDisk.resize(451, 228)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(scanDisk.sizePolicy().hasHeightForWidth())
        scanDisk.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(scanDisk)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.dlg_frame = QtWidgets.QFrame(parent=scanDisk)
        self.dlg_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.dlg_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.dlg_frame.setObjectName("dlg_frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dlg_frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.ttl_frame = QtWidgets.QFrame(parent=self.dlg_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ttl_frame.sizePolicy().hasHeightForWidth())
        self.ttl_frame.setSizePolicy(sizePolicy)
        self.ttl_frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.ttl_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.ttl_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.ttl_frame.setObjectName("ttl_frame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.ttl_frame)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.win_title = QtWidgets.QLabel(parent=self.ttl_frame)
        self.win_title.setObjectName("win_title")
        self.horizontalLayout_4.addWidget(self.win_title)
        self.verticalLayout_2.addWidget(self.ttl_frame)
        self.path_frame = QtWidgets.QFrame(parent=self.dlg_frame)
        self.path_frame.setObjectName("path_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.path_frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.root_dir = QtWidgets.QLineEdit(parent=self.path_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.root_dir.sizePolicy().hasHeightForWidth())
        self.root_dir.setSizePolicy(sizePolicy)
        self.root_dir.setText("")
        self.root_dir.setPlaceholderText("Enter the root path to search files")
        self.root_dir.setObjectName("root_dir")
        self.horizontalLayout.addWidget(self.root_dir)
        self.open_btn = QtWidgets.QToolButton(parent=self.path_frame)
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
        self.verticalLayout_2.addWidget(self.path_frame)
        self.ext_frame = QtWidgets.QFrame(parent=self.dlg_frame)
        self.ext_frame.setObjectName("ext_frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.ext_frame)
        self.verticalLayout.setSpacing(9)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_2 = QtWidgets.QLabel(parent=self.ext_frame)
        self.label_2.setMinimumSize(QtCore.QSize(0, 20))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_5.addWidget(self.label_2)
        self.extensions = QtWidgets.QLineEdit(parent=self.ext_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.extensions.sizePolicy().hasHeightForWidth())
        self.extensions.setSizePolicy(sizePolicy)
        self.extensions.setMinimumSize(QtCore.QSize(0, 20))
        self.extensions.setText("")
        self.extensions.setObjectName("extensions")
        self.horizontalLayout_5.addWidget(self.extensions)
        self.horizontalLayout_5.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.no_ext = QtWidgets.QCheckBox(parent=self.ext_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.no_ext.sizePolicy().hasHeightForWidth())
        self.no_ext.setSizePolicy(sizePolicy)
        self.no_ext.setMinimumSize(QtCore.QSize(0, 0))
        self.no_ext.setIconSize(QtCore.QSize(0, 0))
        self.no_ext.setObjectName("no_ext")
        self.verticalLayout.addWidget(self.no_ext)
        self.verticalLayout_2.addWidget(self.ext_frame)
        self.btn_frame = QtWidgets.QFrame(parent=self.dlg_frame)
        self.btn_frame.setObjectName("btn_frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.btn_frame)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btnCancel = QtWidgets.QPushButton(parent=self.btn_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnCancel.sizePolicy().hasHeightForWidth())
        self.btnCancel.setSizePolicy(sizePolicy)
        self.btnCancel.setMinimumSize(QtCore.QSize(0, 28))
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout_2.addWidget(self.btnCancel)
        self.btnGo = QtWidgets.QPushButton(parent=self.btn_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnGo.sizePolicy().hasHeightForWidth())
        self.btnGo.setSizePolicy(sizePolicy)
        self.btnGo.setMinimumSize(QtCore.QSize(0, 28))
        self.btnGo.setObjectName("btnGo")
        self.horizontalLayout_2.addWidget(self.btnGo)
        self.verticalLayout_2.addWidget(self.btn_frame)
        self.verticalLayout_3.addWidget(self.dlg_frame)

        self.retranslateUi(scanDisk)
        QtCore.QMetaObject.connectSlotsByName(scanDisk)

    def retranslateUi(self, scanDisk):
        _translate = QtCore.QCoreApplication.translate
        scanDisk.setWindowTitle(_translate("scanDisk", "Search files to save in database"))
        self.win_title.setText(_translate("scanDisk", "Adding files to the database"))
        self.label_2.setText(_translate("scanDisk", "List of file extensions"))
        self.extensions.setPlaceholderText(_translate("scanDisk", "comma separated list of extensions"))
        self.no_ext.setText(_translate("scanDisk", "include files without extension"))
        self.btnCancel.setText(_translate("scanDisk", "Cancel"))
        self.btnGo.setText(_translate("scanDisk", "Go"))
