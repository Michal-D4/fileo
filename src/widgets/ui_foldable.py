# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\tmp\src\widgets\foldable.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
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
        self.gridLayout = QtWidgets.QGridLayout(foldable)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.outerFrame = QtWidgets.QFrame(foldable)
        self.outerFrame.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.outerFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.outerFrame.setObjectName("outerFrame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.outerFrame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.decorator = QtWidgets.QFrame(self.outerFrame)
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
        self.header = QtWidgets.QFrame(self.outerFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setMinimumSize(QtCore.QSize(0, 19))
        self.header.setMaximumSize(QtCore.QSize(16777215, 19))
        self.header.setStyleSheet("")
        self.header.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.header.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.header.setLineWidth(0)
        self.header.setObjectName("header")
        self.headerLayout = QtWidgets.QHBoxLayout(self.header)
        self.headerLayout.setContentsMargins(0, 0, 5, 0)
        self.headerLayout.setSpacing(0)
        self.headerLayout.setObjectName("headerLayout")
        self.toFold = QtWidgets.QToolButton(self.header)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toFold.sizePolicy().hasHeightForWidth())
        self.toFold.setSizePolicy(sizePolicy)
        self.toFold.setMinimumSize(QtCore.QSize(0, 19))
        self.toFold.setMaximumSize(QtCore.QSize(16777215, 19))
        self.toFold.setStyleSheet("")
        self.toFold.setText("AUTHORS")
        self.toFold.setIconSize(QtCore.QSize(15, 15))
        self.toFold.setCheckable(True)
        self.toFold.setChecked(False)
        self.toFold.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.toFold.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toFold.setArrowType(QtCore.Qt.ArrowType.NoArrow)
        self.toFold.setObjectName("toFold")
        self.headerLayout.addWidget(self.toFold)
        self.verticalLayout.addWidget(self.header)
        self.inner = QtWidgets.QFrame(self.outerFrame)
        self.inner.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.inner.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.inner.setObjectName("inner")
        self.verticalLayout.addWidget(self.inner)
        self.gridLayout.addWidget(self.outerFrame, 0, 0, 1, 1)

        self.retranslateUi(foldable)
        QtCore.QMetaObject.connectSlotsByName(foldable)

    def retranslateUi(self, foldable):
        _translate = QtCore.QCoreApplication.translate
        foldable.setWindowTitle(_translate("foldable", "Form"))
        self.toFold.setToolTip(_translate("foldable", "Collape/Expand"))