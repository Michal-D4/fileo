# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\src\widgets\foldable.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_foldable(object):
    def setupUi(self, foldable):
        foldable.setObjectName("foldable")
        foldable.resize(189, 140)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(foldable.sizePolicy().hasHeightForWidth())
        foldable.setSizePolicy(sizePolicy)
        foldable.setMinimumSize(QtCore.QSize(0, 0))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(foldable)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.decorator = QtWidgets.QFrame(parent=foldable)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.decorator.sizePolicy().hasHeightForWidth())
        self.decorator.setSizePolicy(sizePolicy)
        self.decorator.setMinimumSize(QtCore.QSize(0, 3))
        self.decorator.setMaximumSize(QtCore.QSize(16777215, 3))
        self.decorator.setStyleSheet("")
        self.decorator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.decorator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.decorator.setLineWidth(0)
        self.decorator.setMidLineWidth(3)
        self.decorator.setObjectName("decorator")
        self.verticalLayout.addWidget(self.decorator)
        self.fold_head = QtWidgets.QFrame(parent=foldable)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fold_head.sizePolicy().hasHeightForWidth())
        self.fold_head.setSizePolicy(sizePolicy)
        self.fold_head.setMinimumSize(QtCore.QSize(0, 20))
        self.fold_head.setMaximumSize(QtCore.QSize(16777215, 20))
        self.fold_head.setStyleSheet("")
        self.fold_head.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.fold_head.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.fold_head.setLineWidth(0)
        self.fold_head.setObjectName("fold_head")
        self.headerLayout = QtWidgets.QHBoxLayout(self.fold_head)
        self.headerLayout.setContentsMargins(0, 0, 9, 0)
        self.headerLayout.setSpacing(4)
        self.headerLayout.setObjectName("headerLayout")
        self.toFold = QtWidgets.QToolButton(parent=self.fold_head)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toFold.sizePolicy().hasHeightForWidth())
        self.toFold.setSizePolicy(sizePolicy)
        self.toFold.setMinimumSize(QtCore.QSize(0, 20))
        self.toFold.setMaximumSize(QtCore.QSize(16777215, 20))
        self.toFold.setToolTip("")
        self.toFold.setToolTipDuration(-1)
        self.toFold.setStyleSheet("")
        self.toFold.setText("")
        self.toFold.setIconSize(QtCore.QSize(12, 12))
        self.toFold.setCheckable(True)
        self.toFold.setChecked(False)
        self.toFold.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.toFold.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toFold.setAutoRaise(True)
        self.toFold.setArrowType(QtCore.Qt.ArrowType.NoArrow)
        self.toFold.setObjectName("toFold")
        self.headerLayout.addWidget(self.toFold)
        self.verticalLayout.addWidget(self.fold_head)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.inner = QtWidgets.QFrame(parent=foldable)
        self.inner.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.inner.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.inner.setObjectName("inner")
        self.verticalLayout_2.addWidget(self.inner)
        self.verticalLayout_2.setStretch(1, 1)

        self.retranslateUi(foldable)
        QtCore.QMetaObject.connectSlotsByName(foldable)

    def retranslateUi(self, foldable):
        _translate = QtCore.QCoreApplication.translate
        foldable.setWindowTitle(_translate("foldable", "Form"))
