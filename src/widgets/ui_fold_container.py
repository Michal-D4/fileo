# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\src\fileo\widgets\fold_container.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Foldings(object):
    def setupUi(self, Foldings):
        Foldings.setObjectName("Foldings")
        Foldings.resize(170, 651)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Foldings.sizePolicy().hasHeightForWidth())
        Foldings.setSizePolicy(sizePolicy)
        Foldings.setMinimumSize(QtCore.QSize(0, 0))
        Foldings.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(Foldings)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.navi_header = QtWidgets.QFrame(Foldings)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.navi_header.sizePolicy().hasHeightForWidth())
        self.navi_header.setSizePolicy(sizePolicy)
        self.navi_header.setMinimumSize(QtCore.QSize(0, 32))
        self.navi_header.setMaximumSize(QtCore.QSize(16777215, 32))
        self.navi_header.setStyleSheet("")
        self.navi_header.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.navi_header.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.navi_header.setLineWidth(0)
        self.navi_header.setObjectName("navi_header")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.navi_header)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.app_mode = QtWidgets.QLabel(self.navi_header)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.app_mode.sizePolicy().hasHeightForWidth())
        self.app_mode.setSizePolicy(sizePolicy)
        self.app_mode.setMinimumSize(QtCore.QSize(0, 32))
        self.app_mode.setText("")
        self.app_mode.setObjectName("app_mode")
        self.horizontalLayout.addWidget(self.app_mode)
        self.more = QtWidgets.QToolButton(self.navi_header)
        self.more.setMinimumSize(QtCore.QSize(22, 22))
        self.more.setMaximumSize(QtCore.QSize(22, 22))
        self.more.setWhatsThis("")
        self.more.setAutoFillBackground(False)
        self.more.setText("")
        self.more.setIconSize(QtCore.QSize(22, 22))
        self.more.setCheckable(False)
        self.more.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.more.setAutoRaise(True)
        self.more.setObjectName("more")
        self.horizontalLayout.addWidget(self.more)
        self.verticalLayout_4.addWidget(self.navi_header)
        self.scrollArea = QtWidgets.QScrollArea(Foldings)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.scrollArea.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeading|QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
        self.scrollArea.setObjectName("scrollArea")
        self.contents = QtWidgets.QWidget()
        self.contents.setGeometry(QtCore.QRect(0, 0, 170, 619))
        self.contents.setObjectName("contents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.contents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.foldable_1 = Foldable(self.contents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.foldable_1.sizePolicy().hasHeightForWidth())
        self.foldable_1.setSizePolicy(sizePolicy)
        self.foldable_1.setMinimumSize(QtCore.QSize(0, 22))
        self.foldable_1.setObjectName("foldable_1")
        self.verticalLayout.addWidget(self.foldable_1)
        self.foldable_2 = Foldable(self.contents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.foldable_2.sizePolicy().hasHeightForWidth())
        self.foldable_2.setSizePolicy(sizePolicy)
        self.foldable_2.setMinimumSize(QtCore.QSize(0, 22))
        self.foldable_2.setObjectName("foldable_2")
        self.verticalLayout.addWidget(self.foldable_2)
        self.foldable_3 = Foldable(self.contents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.foldable_3.sizePolicy().hasHeightForWidth())
        self.foldable_3.setSizePolicy(sizePolicy)
        self.foldable_3.setMinimumSize(QtCore.QSize(0, 22))
        self.foldable_3.setObjectName("foldable_3")
        self.verticalLayout.addWidget(self.foldable_3)
        self.foldable_4 = Foldable(self.contents)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.foldable_4.sizePolicy().hasHeightForWidth())
        self.foldable_4.setSizePolicy(sizePolicy)
        self.foldable_4.setMinimumSize(QtCore.QSize(0, 22))
        self.foldable_4.setObjectName("foldable_4")
        self.verticalLayout.addWidget(self.foldable_4)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Maximum)
        self.verticalLayout.addItem(spacerItem)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout.setStretch(3, 1)
        self.scrollArea.setWidget(self.contents)
        self.verticalLayout_4.addWidget(self.scrollArea)

        self.retranslateUi(Foldings)
        QtCore.QMetaObject.connectSlotsByName(Foldings)

    def retranslateUi(self, Foldings):
        _translate = QtCore.QCoreApplication.translate
        Foldings.setWindowTitle(_translate("Foldings", "Form"))
        self.more.setToolTip(_translate("Foldings", "Hide/Show Views"))
from .foldable import Foldable