# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\src\fileo\ui\main.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Sho(object):
    def setupUi(self, Sho):
        Sho.setObjectName("Sho")
        Sho.resize(988, 600)
        Sho.setStyleSheet("")
        self.outer = QtWidgets.QWidget(Sho)
        self.outer.setStyleSheet("")
        self.outer.setObjectName("outer")
        self.appMargins = QtWidgets.QVBoxLayout(self.outer)
        self.appMargins.setContentsMargins(5, 5, 5, 5)
        self.appMargins.setSpacing(0)
        self.appMargins.setObjectName("appMargins")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.toolBar = QtWidgets.QFrame(self.outer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toolBar.sizePolicy().hasHeightForWidth())
        self.toolBar.setSizePolicy(sizePolicy)
        self.toolBar.setMinimumSize(QtCore.QSize(48, 0))
        self.toolBar.setMaximumSize(QtCore.QSize(48, 16777215))
        self.toolBar.setStyleSheet("")
        self.toolBar.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.toolBar.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.toolBar.setLineWidth(0)
        self.toolBar.setObjectName("toolBar")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.toolBar)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.dataBase = QtWidgets.QToolButton(self.toolBar)
        self.dataBase.setMinimumSize(QtCore.QSize(48, 48))
        self.dataBase.setMaximumSize(QtCore.QSize(48, 48))
        self.dataBase.setStyleSheet("")
        self.dataBase.setText("")
        self.dataBase.setIconSize(QtCore.QSize(32, 32))
        self.dataBase.setAutoRaise(True)
        self.dataBase.setObjectName("dataBase")
        self.verticalLayout_2.addWidget(self.dataBase)
        self.btnDir = QtWidgets.QToolButton(self.toolBar)
        self.btnDir.setMinimumSize(QtCore.QSize(48, 48))
        self.btnDir.setMaximumSize(QtCore.QSize(48, 48))
        self.btnDir.setStyleSheet("")
        self.btnDir.setText("")
        self.btnDir.setIconSize(QtCore.QSize(32, 32))
        self.btnDir.setCheckable(True)
        self.btnDir.setChecked(True)
        self.btnDir.setAutoExclusive(True)
        self.btnDir.setAutoRaise(True)
        self.btnDir.setObjectName("btnDir")
        self.buttons = QtWidgets.QButtonGroup(Sho)
        self.buttons.setObjectName("buttons")
        self.buttons.addButton(self.btnDir)
        self.verticalLayout_2.addWidget(self.btnDir)
        self.btnFilter = QtWidgets.QToolButton(self.toolBar)
        self.btnFilter.setMinimumSize(QtCore.QSize(48, 48))
        self.btnFilter.setMaximumSize(QtCore.QSize(48, 48))
        self.btnFilter.setStyleSheet("")
        self.btnFilter.setText("")
        self.btnFilter.setIconSize(QtCore.QSize(32, 32))
        self.btnFilter.setCheckable(True)
        self.btnFilter.setChecked(False)
        self.btnFilter.setAutoExclusive(True)
        self.btnFilter.setAutoRaise(True)
        self.btnFilter.setObjectName("btnFilter")
        self.buttons.addButton(self.btnFilter)
        self.verticalLayout_2.addWidget(self.btnFilter)
        self.btnFilterSetup = QtWidgets.QToolButton(self.toolBar)
        self.btnFilterSetup.setMinimumSize(QtCore.QSize(48, 48))
        self.btnFilterSetup.setMaximumSize(QtCore.QSize(48, 48))
        self.btnFilterSetup.setText("")
        self.btnFilterSetup.setIconSize(QtCore.QSize(32, 32))
        self.btnFilterSetup.setCheckable(True)
        self.btnFilterSetup.setAutoRaise(True)
        self.btnFilterSetup.setObjectName("btnFilterSetup")
        self.buttons.addButton(self.btnFilterSetup)
        self.verticalLayout_2.addWidget(self.btnFilterSetup)
        self.btnScan = QtWidgets.QToolButton(self.toolBar)
        self.btnScan.setMinimumSize(QtCore.QSize(48, 48))
        self.btnScan.setMaximumSize(QtCore.QSize(48, 48))
        self.btnScan.setStyleSheet("")
        self.btnScan.setText("")
        self.btnScan.setIconSize(QtCore.QSize(32, 32))
        self.btnScan.setAutoRaise(True)
        self.btnScan.setObjectName("btnScan")
        self.verticalLayout_2.addWidget(self.btnScan)
        spacerItem = QtWidgets.QSpacerItem(20, 286, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.btnToggleBar = QtWidgets.QToolButton(self.toolBar)
        self.btnToggleBar.setMinimumSize(QtCore.QSize(48, 48))
        self.btnToggleBar.setMaximumSize(QtCore.QSize(48, 48))
        self.btnToggleBar.setStyleSheet("")
        self.btnToggleBar.setText("")
        self.btnToggleBar.setIconSize(QtCore.QSize(32, 32))
        self.btnToggleBar.setAutoRaise(True)
        self.btnToggleBar.setObjectName("btnToggleBar")
        self.verticalLayout_2.addWidget(self.btnToggleBar)
        self.btnSetup = QtWidgets.QToolButton(self.toolBar)
        self.btnSetup.setMinimumSize(QtCore.QSize(48, 48))
        self.btnSetup.setMaximumSize(QtCore.QSize(48, 48))
        self.btnSetup.setStyleSheet("")
        self.btnSetup.setText("")
        self.btnSetup.setIconSize(QtCore.QSize(32, 32))
        self.btnSetup.setAutoRaise(True)
        self.btnSetup.setObjectName("btnSetup")
        self.verticalLayout_2.addWidget(self.btnSetup)
        self.horizontalLayout_6.addWidget(self.toolBar)
        self.container = QtWidgets.QFrame(self.outer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.container.sizePolicy().hasHeightForWidth())
        self.container.setSizePolicy(sizePolicy)
        self.container.setMinimumSize(QtCore.QSize(170, 0))
        self.container.setMaximumSize(QtCore.QSize(170, 16777215))
        self.container.setWhatsThis("")
        self.container.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.container.setStyleSheet("")
        self.container.setObjectName("container")
        self.horizontalLayout_6.addWidget(self.container)
        self.fileFrame = QtWidgets.QFrame(self.outer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileFrame.sizePolicy().hasHeightForWidth())
        self.fileFrame.setSizePolicy(sizePolicy)
        self.fileFrame.setMinimumSize(QtCore.QSize(170, 0))
        self.fileFrame.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.fileFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.fileFrame.setLineWidth(0)
        self.fileFrame.setObjectName("fileFrame")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.fileFrame)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.topBar = QtWidgets.QFrame(self.fileFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.topBar.sizePolicy().hasHeightForWidth())
        self.topBar.setSizePolicy(sizePolicy)
        self.topBar.setMinimumSize(QtCore.QSize(0, 32))
        self.topBar.setMaximumSize(QtCore.QSize(16777215, 32))
        self.topBar.setStyleSheet("")
        self.topBar.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.topBar.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.topBar.setLineWidth(0)
        self.topBar.setObjectName("topBar")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.topBar)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(9, -1, 24, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(self.topBar)
        self.label.setText("")
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(347, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.field_menu = QtWidgets.QToolButton(self.topBar)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(22)
        sizePolicy.setVerticalStretch(22)
        sizePolicy.setHeightForWidth(self.field_menu.sizePolicy().hasHeightForWidth())
        self.field_menu.setSizePolicy(sizePolicy)
        self.field_menu.setMinimumSize(QtCore.QSize(22, 22))
        self.field_menu.setText("")
        self.field_menu.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.field_menu.setAutoRaise(True)
        self.field_menu.setObjectName("field_menu")
        self.horizontalLayout_2.addWidget(self.field_menu)
        self.horizontalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.minimize = QtWidgets.QToolButton(self.topBar)
        self.minimize.setMinimumSize(QtCore.QSize(46, 32))
        self.minimize.setMaximumSize(QtCore.QSize(46, 32))
        self.minimize.setText("")
        self.minimize.setIconSize(QtCore.QSize(24, 24))
        self.minimize.setAutoRaise(True)
        self.minimize.setObjectName("minimize")
        self.horizontalLayout.addWidget(self.minimize)
        self.maximize = QtWidgets.QToolButton(self.topBar)
        self.maximize.setMinimumSize(QtCore.QSize(46, 32))
        self.maximize.setMaximumSize(QtCore.QSize(46, 32))
        self.maximize.setText("")
        self.maximize.setIconSize(QtCore.QSize(24, 24))
        self.maximize.setAutoRaise(True)
        self.maximize.setObjectName("maximize")
        self.horizontalLayout.addWidget(self.maximize)
        self.close = QtWidgets.QToolButton(self.topBar)
        self.close.setMinimumSize(QtCore.QSize(46, 32))
        self.close.setMaximumSize(QtCore.QSize(46, 32))
        self.close.setText("")
        self.close.setIconSize(QtCore.QSize(28, 28))
        self.close.setAutoRaise(True)
        self.close.setObjectName("close")
        self.horizontalLayout.addWidget(self.close)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.verticalLayout_3.addWidget(self.topBar)
        self.bottomFileFrame = QtWidgets.QFrame(self.fileFrame)
        self.bottomFileFrame.setObjectName("bottomFileFrame")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.bottomFileFrame)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.vSplit = QtWidgets.QFrame(self.bottomFileFrame)
        self.vSplit.setMinimumSize(QtCore.QSize(0, 0))
        self.vSplit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.vSplit.setStyleSheet("")
        self.vSplit.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.vSplit.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.vSplit.setLineWidth(0)
        self.vSplit.setMidLineWidth(3)
        self.vSplit.setObjectName("vSplit")
        self.horizontalLayout_5.addWidget(self.vSplit)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.file_list = QtWidgets.QTreeView(self.bottomFileFrame)
        self.file_list.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.setToolTip("")
        self.file_list.setStyleSheet("")
        self.file_list.setLineWidth(2)
        self.file_list.setDragEnabled(True)
        self.file_list.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragOnly)
        self.file_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setIndentation(3)
        self.file_list.setUniformRowHeights(True)
        self.file_list.setItemsExpandable(False)
        self.file_list.setSortingEnabled(True)
        self.file_list.setExpandsOnDoubleClick(False)
        self.file_list.setObjectName("file_list")
        self.file_list.header().setStretchLastSection(False)
        self.verticalLayout.addWidget(self.file_list)
        self.hSplit = QtWidgets.QFrame(self.bottomFileFrame)
        self.hSplit.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.hSplit.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.hSplit.setLineWidth(0)
        self.hSplit.setMidLineWidth(3)
        self.hSplit.setObjectName("hSplit")
        self.verticalLayout.addWidget(self.hSplit)
        self.noteHolder = QtWidgets.QFrame(self.bottomFileFrame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.noteHolder.sizePolicy().hasHeightForWidth())
        self.noteHolder.setSizePolicy(sizePolicy)
        self.noteHolder.setMinimumSize(QtCore.QSize(0, 75))
        self.noteHolder.setStyleSheet("")
        self.noteHolder.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.noteHolder.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.noteHolder.setLineWidth(0)
        self.noteHolder.setObjectName("noteHolder")
        self.verticalLayout.addWidget(self.noteHolder)
        self.verticalLayout.setStretch(0, 1)
        self.horizontalLayout_5.addLayout(self.verticalLayout)
        self.verticalLayout_3.addWidget(self.bottomFileFrame)
        self.horizontalLayout_6.addWidget(self.fileFrame)
        self.horizontalLayout_6.setStretch(2, 1)
        self.appMargins.addLayout(self.horizontalLayout_6)
        self.status = QtWidgets.QFrame(self.outer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status.sizePolicy().hasHeightForWidth())
        self.status.setSizePolicy(sizePolicy)
        self.status.setMinimumSize(QtCore.QSize(0, 20))
        self.status.setMaximumSize(QtCore.QSize(16777215, 20))
        self.status.setStyleSheet("")
        self.status.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.status.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.status.setLineWidth(0)
        self.status.setObjectName("status")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.status)
        self.horizontalLayout_3.setContentsMargins(9, 0, 9, 0)
        self.horizontalLayout_3.setSpacing(9)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.busy = QtWidgets.QLabel(self.status)
        self.busy.setText("")
        self.busy.setObjectName("busy")
        self.horizontalLayout_3.addWidget(self.busy)
        self.db_name = QtWidgets.QLabel(self.status)
        self.db_name.setText("")
        self.db_name.setObjectName("db_name")
        self.horizontalLayout_3.addWidget(self.db_name)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.others = QtWidgets.QLabel(self.status)
        self.others.setText("")
        self.others.setObjectName("others")
        self.horizontalLayout_3.addWidget(self.others)
        self.appMargins.addWidget(self.status)
        Sho.setCentralWidget(self.outer)

        self.retranslateUi(Sho)
        QtCore.QMetaObject.connectSlotsByName(Sho)

    def retranslateUi(self, Sho):
        _translate = QtCore.QCoreApplication.translate
        Sho.setWindowTitle(_translate("Sho", "MainWindow"))
        self.dataBase.setToolTip(_translate("Sho", "Connect to DB/Create DB"))
        self.btnDir.setToolTip(_translate("Sho", "Show file list for current directory"))
        self.btnFilter.setToolTip(_translate("Sho", "Show file list according the filter"))
        self.btnFilterSetup.setToolTip(_translate("Sho", "Setup file list filter"))
        self.btnScan.setToolTip(_translate("Sho", "Scan file system for files and add them into DB"))
        self.btnToggleBar.setToolTip(_translate("Sho", "Toggle Navigator bar"))
        self.btnSetup.setToolTip(_translate("Sho", "Settings"))
        self.field_menu.setToolTip(_translate("Sho", "Show/Hide fields"))
