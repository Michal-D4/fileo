# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\src\widgets\pref.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_prefForm(object):
    def setupUi(self, prefForm):
        prefForm.setObjectName("prefForm")
        prefForm.resize(400, 310)
        self.verticalLayout = QtWidgets.QVBoxLayout(prefForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.dlg_frame = QtWidgets.QFrame(parent=prefForm)
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
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ico = QtWidgets.QLabel(parent=self.ttl_frame)
        self.ico.setText("")
        self.ico.setObjectName("ico")
        self.horizontalLayout.addWidget(self.ico)
        self.label = QtWidgets.QLabel(parent=self.ttl_frame)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout_2.addWidget(self.ttl_frame)
        self.pref_form = QtWidgets.QFrame(parent=self.dlg_frame)
        self.pref_form.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pref_form.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.pref_form.setObjectName("pref_form")
        self.verticalLayout_2.addWidget(self.pref_form)
        self.pref_btns = QtWidgets.QFrame(parent=self.dlg_frame)
        self.pref_btns.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.pref_btns.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.pref_btns.setObjectName("pref_btns")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.pref_btns)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(167, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.accept_pref = QtWidgets.QPushButton(parent=self.pref_btns)
        self.accept_pref.setMinimumSize(QtCore.QSize(95, 28))
        self.accept_pref.setObjectName("accept_pref")
        self.horizontalLayout_2.addWidget(self.accept_pref)
        self.cancel = QtWidgets.QPushButton(parent=self.pref_btns)
        self.cancel.setMinimumSize(QtCore.QSize(95, 28))
        self.cancel.setObjectName("cancel")
        self.horizontalLayout_2.addWidget(self.cancel)
        self.verticalLayout_2.addWidget(self.pref_btns)
        self.verticalLayout_2.setStretch(1, 1)
        self.verticalLayout.addWidget(self.dlg_frame)

        self.retranslateUi(prefForm)
        QtCore.QMetaObject.connectSlotsByName(prefForm)

    def retranslateUi(self, prefForm):
        _translate = QtCore.QCoreApplication.translate
        prefForm.setWindowTitle(_translate("prefForm", "Form"))
        self.label.setText(_translate("prefForm", "Application preferences"))
        self.accept_pref.setText(_translate("prefForm", "Ok"))
        self.cancel.setText(_translate("prefForm", "Cancel"))