# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\src\widgets\about.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_aboutForm(object):
    def setupUi(self, aboutForm):
        aboutForm.setObjectName("aboutForm")
        aboutForm.resize(483, 174)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(aboutForm)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.dlg_frame = QtWidgets.QFrame(parent=aboutForm)
        self.dlg_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.dlg_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.dlg_frame.setObjectName("dlg_frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dlg_frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.ttl_frame = QtWidgets.QFrame(parent=self.dlg_frame)
        self.ttl_frame.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.ttl_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.ttl_frame.setObjectName("ttl_frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.ttl_frame)
        self.horizontalLayout.setContentsMargins(-1, 9, -1, 9)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ico = QtWidgets.QLabel(parent=self.ttl_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ico.sizePolicy().hasHeightForWidth())
        self.ico.setSizePolicy(sizePolicy)
        self.ico.setMinimumSize(QtCore.QSize(0, 0))
        self.ico.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.ico.setText("")
        self.ico.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.ico.setObjectName("ico")
        self.horizontalLayout.addWidget(self.ico)
        self.ttl_label = QtWidgets.QLabel(parent=self.ttl_frame)
        self.ttl_label.setObjectName("ttl_label")
        self.horizontalLayout.addWidget(self.ttl_label)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout_2.addWidget(self.ttl_frame)
        self.fr_about = QtWidgets.QFrame(parent=self.dlg_frame)
        self.fr_about.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.fr_about.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.fr_about.setObjectName("fr_about")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.fr_about)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.app_info = QtWidgets.QLabel(parent=self.fr_about)
        self.app_info.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.app_info.setObjectName("app_info")
        self.verticalLayout.addWidget(self.app_info)
        self.git_repo = QtWidgets.QLabel(parent=self.fr_about)
        self.git_repo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.git_repo.setObjectName("git_repo")
        self.verticalLayout.addWidget(self.git_repo)
        self.verticalLayout_2.addWidget(self.fr_about)
        self.fr_btn = QtWidgets.QFrame(parent=self.dlg_frame)
        self.fr_btn.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.fr_btn.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.fr_btn.setObjectName("fr_btn")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.fr_btn)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(167, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.ok_btn = QtWidgets.QPushButton(parent=self.fr_btn)
        self.ok_btn.setMinimumSize(QtCore.QSize(95, 28))
        self.ok_btn.setObjectName("ok_btn")
        self.horizontalLayout_2.addWidget(self.ok_btn)
        self.verticalLayout_2.addWidget(self.fr_btn)
        self.verticalLayout_2.setStretch(1, 1)
        self.horizontalLayout_3.addWidget(self.dlg_frame)

        self.retranslateUi(aboutForm)
        QtCore.QMetaObject.connectSlotsByName(aboutForm)

    def retranslateUi(self, aboutForm):
        _translate = QtCore.QCoreApplication.translate
        aboutForm.setWindowTitle(_translate("aboutForm", "Form"))
        self.ttl_label.setText(_translate("aboutForm", "About Fileo"))
        self.app_info.setText(_translate("aboutForm", "app_info"))
        self.git_repo.setText(_translate("aboutForm", "git_repo"))
        self.ok_btn.setText(_translate("aboutForm", "Ok"))
