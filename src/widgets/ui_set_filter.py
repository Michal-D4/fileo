# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo2\src\widgets\set_filter.ui'
#
# Created by: PyQt6 UI code generator 6.5.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_filterSetup(object):
    def setupUi(self, filterSetup):
        filterSetup.setObjectName("filterSetup")
        filterSetup.resize(504, 487)
        self.VLayoutMain = QtWidgets.QVBoxLayout(filterSetup)
        self.VLayoutMain.setContentsMargins(9, 9, 9, 9)
        self.VLayoutMain.setObjectName("VLayoutMain")
        self.dlg_frame = QtWidgets.QFrame(parent=filterSetup)
        self.dlg_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.dlg_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.dlg_frame.setObjectName("dlg_frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.dlg_frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 9)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ttl_frame = QtWidgets.QFrame(parent=self.dlg_frame)
        self.ttl_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.ttl_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.ttl_frame.setObjectName("ttl_frame")
        self.HLayoutTitle = QtWidgets.QHBoxLayout(self.ttl_frame)
        self.HLayoutTitle.setContentsMargins(-1, 6, -1, 6)
        self.HLayoutTitle.setObjectName("HLayoutTitle")
        self.ico = QtWidgets.QLabel(parent=self.ttl_frame)
        self.ico.setText("")
        self.ico.setObjectName("ico")
        self.HLayoutTitle.addWidget(self.ico)
        self.hdr_lbl = QtWidgets.QLabel(parent=self.ttl_frame)
        self.hdr_lbl.setObjectName("hdr_lbl")
        self.HLayoutTitle.addWidget(self.hdr_lbl)
        self.HLayoutTitle.setStretch(1, 1)
        self.verticalLayout.addWidget(self.ttl_frame)
        self.form = QtWidgets.QFrame(parent=self.dlg_frame)
        self.form.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.form.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.form.setObjectName("form")
        self.formLayout = QtWidgets.QFormLayout(self.form)
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setObjectName("formLayout")
        self.frameDir = QtWidgets.QFrame(parent=self.form)
        self.frameDir.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frameDir.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frameDir.setObjectName("frameDir")
        self.VLayoutDir = QtWidgets.QVBoxLayout(self.frameDir)
        self.VLayoutDir.setContentsMargins(0, 0, 0, 0)
        self.VLayoutDir.setObjectName("VLayoutDir")
        self.selected_dir = QtWidgets.QCheckBox(parent=self.frameDir)
        self.selected_dir.setChecked(False)
        self.selected_dir.setObjectName("selected_dir")
        self.VLayoutDir.addWidget(self.selected_dir)
        self.HLayoutSubDir = QtWidgets.QHBoxLayout()
        self.HLayoutSubDir.setObjectName("HLayoutSubDir")
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.HLayoutSubDir.addItem(spacerItem)
        self.subDirs = QtWidgets.QCheckBox(parent=self.frameDir)
        self.subDirs.setObjectName("subDirs")
        self.HLayoutSubDir.addWidget(self.subDirs)
        self.VLayoutDir.addLayout(self.HLayoutSubDir)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.frameDir)
        self.dir_list = QtWidgets.QPlainTextEdit(parent=self.form)
        self.dir_list.setMaximumSize(QtCore.QSize(16777215, 60))
        self.dir_list.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.dir_list.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.dir_list.setReadOnly(True)
        self.dir_list.setObjectName("dir_list")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dir_list)
        self.no_folder = QtWidgets.QCheckBox(parent=self.form)
        self.no_folder.setObjectName("no_folder")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.no_folder)
        self.frame_tag = QtWidgets.QFrame(parent=self.form)
        self.frame_tag.setMaximumSize(QtCore.QSize(16777215, 21))
        self.frame_tag.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_tag.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_tag.setLineWidth(1)
        self.frame_tag.setObjectName("frame_tag")
        self.HLayoutTags = QtWidgets.QHBoxLayout(self.frame_tag)
        self.HLayoutTags.setContentsMargins(0, 0, 0, 0)
        self.HLayoutTags.setObjectName("HLayoutTags")
        self.selected_tag = QtWidgets.QCheckBox(parent=self.frame_tag)
        self.selected_tag.setChecked(False)
        self.selected_tag.setObjectName("selected_tag")
        self.HLayoutTags.addWidget(self.selected_tag)
        self.all_btn = QtWidgets.QRadioButton(parent=self.frame_tag)
        self.all_btn.setChecked(True)
        self.all_btn.setObjectName("all_btn")
        self.HLayoutTags.addWidget(self.all_btn)
        self.any_btn = QtWidgets.QRadioButton(parent=self.frame_tag)
        self.any_btn.setObjectName("any_btn")
        self.HLayoutTags.addWidget(self.any_btn)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.frame_tag)
        self.tag_list = QtWidgets.QPlainTextEdit(parent=self.form)
        self.tag_list.setMaximumSize(QtCore.QSize(16777215, 40))
        self.tag_list.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.tag_list.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.tag_list.setReadOnly(True)
        self.tag_list.setObjectName("tag_list")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.tag_list)
        self.selected_ext = QtWidgets.QCheckBox(parent=self.form)
        self.selected_ext.setObjectName("selected_ext")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.selected_ext)
        self.ext_list = QtWidgets.QPlainTextEdit(parent=self.form)
        self.ext_list.setMaximumSize(QtCore.QSize(16777215, 40))
        self.ext_list.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.ext_list.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.ext_list.setReadOnly(True)
        self.ext_list.setObjectName("ext_list")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.ext_list)
        self.selected_author = QtWidgets.QCheckBox(parent=self.form)
        self.selected_author.setObjectName("selected_author")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.LabelRole, self.selected_author)
        self.author_list = QtWidgets.QPlainTextEdit(parent=self.form)
        self.author_list.setMaximumSize(QtCore.QSize(16777215, 40))
        self.author_list.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.author_list.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.author_list.setReadOnly(True)
        self.author_list.setObjectName("author_list")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.ItemRole.FieldRole, self.author_list)
        self.open_sel = QtWidgets.QCheckBox(parent=self.form)
        self.open_sel.setObjectName("open_sel")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.ItemRole.LabelRole, self.open_sel)
        self.HLayoutOpen = QtWidgets.QHBoxLayout()
        self.HLayoutOpen.setContentsMargins(9, -1, -1, -1)
        self.HLayoutOpen.setObjectName("HLayoutOpen")
        self.open_cond = QtWidgets.QComboBox(parent=self.form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.open_cond.sizePolicy().hasHeightForWidth())
        self.open_cond.setSizePolicy(sizePolicy)
        self.open_cond.setMinimumSize(QtCore.QSize(50, 0))
        self.open_cond.setMaximumSize(QtCore.QSize(50, 16777215))
        self.open_cond.setObjectName("open_cond")
        self.open_cond.addItem("")
        self.open_cond.addItem("")
        self.HLayoutOpen.addWidget(self.open_cond)
        spacerItem1 = QtWidgets.QSpacerItem(12, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.HLayoutOpen.addItem(spacerItem1)
        self.open_edit = QtWidgets.QLineEdit(parent=self.form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.open_edit.sizePolicy().hasHeightForWidth())
        self.open_edit.setSizePolicy(sizePolicy)
        self.open_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.open_edit.setMaximumSize(QtCore.QSize(50, 16777215))
        self.open_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.open_edit.setObjectName("open_edit")
        self.HLayoutOpen.addWidget(self.open_edit)
        spacerItem2 = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.HLayoutOpen.addItem(spacerItem2)
        self.HLayoutOpen.setStretch(0, 1)
        self.HLayoutOpen.setStretch(2, 2)
        self.HLayoutOpen.setStretch(3, 1)
        self.formLayout.setLayout(9, QtWidgets.QFormLayout.ItemRole.FieldRole, self.HLayoutOpen)
        self.rating_sel = QtWidgets.QCheckBox(parent=self.form)
        self.rating_sel.setObjectName("rating_sel")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.ItemRole.LabelRole, self.rating_sel)
        self.HLayoutRating = QtWidgets.QHBoxLayout()
        self.HLayoutRating.setContentsMargins(9, -1, -1, -1)
        self.HLayoutRating.setObjectName("HLayoutRating")
        self.rating_cond = QtWidgets.QComboBox(parent=self.form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rating_cond.sizePolicy().hasHeightForWidth())
        self.rating_cond.setSizePolicy(sizePolicy)
        self.rating_cond.setMinimumSize(QtCore.QSize(50, 0))
        self.rating_cond.setMaximumSize(QtCore.QSize(50, 16777215))
        self.rating_cond.setObjectName("rating_cond")
        self.rating_cond.addItem("")
        self.rating_cond.addItem("")
        self.rating_cond.addItem("")
        self.HLayoutRating.addWidget(self.rating_cond)
        spacerItem3 = QtWidgets.QSpacerItem(12, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.HLayoutRating.addItem(spacerItem3)
        self.rating_edit = QtWidgets.QLineEdit(parent=self.form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.rating_edit.sizePolicy().hasHeightForWidth())
        self.rating_edit.setSizePolicy(sizePolicy)
        self.rating_edit.setMinimumSize(QtCore.QSize(0, 0))
        self.rating_edit.setMaximumSize(QtCore.QSize(50, 16777215))
        self.rating_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.rating_edit.setObjectName("rating_edit")
        self.HLayoutRating.addWidget(self.rating_edit)
        spacerItem4 = QtWidgets.QSpacerItem(80, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.HLayoutRating.addItem(spacerItem4)
        self.HLayoutRating.setStretch(0, 1)
        self.HLayoutRating.setStretch(2, 2)
        self.HLayoutRating.setStretch(3, 1)
        self.formLayout.setLayout(11, QtWidgets.QFormLayout.ItemRole.FieldRole, self.HLayoutRating)
        self.date_type_frame = QtWidgets.QFrame(parent=self.form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date_type_frame.sizePolicy().hasHeightForWidth())
        self.date_type_frame.setSizePolicy(sizePolicy)
        self.date_type_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.date_type_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.date_type_frame.setObjectName("date_type_frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.date_type_frame)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(12)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtWidgets.QLabel(parent=self.date_type_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setMinimumSize(QtCore.QSize(41, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.date_type = QtWidgets.QComboBox(parent=self.date_type_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.date_type.sizePolicy().hasHeightForWidth())
        self.date_type.setSizePolicy(sizePolicy)
        self.date_type.setMinimumSize(QtCore.QSize(91, 24))
        self.date_type.setMaximumSize(QtCore.QSize(16777215, 24))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.date_type.setFont(font)
        self.date_type.setObjectName("date_type")
        self.date_type.addItem("")
        self.date_type.addItem("")
        self.date_type.addItem("")
        self.date_type.addItem("")
        self.date_type.addItem("")
        self.horizontalLayout.addWidget(self.date_type)
        spacerItem5 = QtWidgets.QSpacerItem(32, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(9, -1, -1, -1)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem6 = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem6)
        self.note_date_type = QtWidgets.QComboBox(parent=self.date_type_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.note_date_type.sizePolicy().hasHeightForWidth())
        self.note_date_type.setSizePolicy(sizePolicy)
        self.note_date_type.setMinimumSize(QtCore.QSize(110, 24))
        self.note_date_type.setMaximumSize(QtCore.QSize(16777215, 24))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.note_date_type.setFont(font)
        self.note_date_type.setObjectName("note_date_type")
        self.note_date_type.addItem("")
        self.note_date_type.addItem("")
        self.note_date_type.addItem("")
        self.note_date_type.addItem("")
        self.horizontalLayout_3.addWidget(self.note_date_type)
        spacerItem7 = QtWidgets.QSpacerItem(10, 20, QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem7)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.ItemRole.LabelRole, self.date_type_frame)
        self.date_frame = QtWidgets.QFrame(parent=self.form)
        self.date_frame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.date_frame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.date_frame.setObjectName("date_frame")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.date_frame)
        self.horizontalLayout_2.setContentsMargins(9, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.HLayoutAfter_2 = QtWidgets.QHBoxLayout()
        self.HLayoutAfter_2.setObjectName("HLayoutAfter_2")
        self.after = QtWidgets.QCheckBox(parent=self.date_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.after.sizePolicy().hasHeightForWidth())
        self.after.setSizePolicy(sizePolicy)
        self.after.setMinimumSize(QtCore.QSize(80, 0))
        self.after.setChecked(True)
        self.after.setObjectName("after")
        self.HLayoutAfter_2.addWidget(self.after)
        self.after_date = QtWidgets.QDateEdit(parent=self.date_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.after_date.sizePolicy().hasHeightForWidth())
        self.after_date.setSizePolicy(sizePolicy)
        self.after_date.setMinimumSize(QtCore.QSize(0, 24))
        self.after_date.setMaximumSize(QtCore.QSize(16777215, 24))
        self.after_date.setObjectName("after_date")
        self.HLayoutAfter_2.addWidget(self.after_date)
        self.verticalLayout_3.addLayout(self.HLayoutAfter_2)
        self.HLayoutBefore_2 = QtWidgets.QHBoxLayout()
        self.HLayoutBefore_2.setObjectName("HLayoutBefore_2")
        self.before = QtWidgets.QCheckBox(parent=self.date_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.before.sizePolicy().hasHeightForWidth())
        self.before.setSizePolicy(sizePolicy)
        self.before.setMinimumSize(QtCore.QSize(80, 0))
        self.before.setObjectName("before")
        self.HLayoutBefore_2.addWidget(self.before)
        self.before_date = QtWidgets.QDateEdit(parent=self.date_frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.before_date.sizePolicy().hasHeightForWidth())
        self.before_date.setSizePolicy(sizePolicy)
        self.before_date.setMinimumSize(QtCore.QSize(0, 24))
        self.before_date.setMaximumSize(QtCore.QSize(16777215, 24))
        self.before_date.setObjectName("before_date")
        self.HLayoutBefore_2.addWidget(self.before_date)
        self.verticalLayout_3.addLayout(self.HLayoutBefore_2)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem8)
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.ItemRole.FieldRole, self.date_frame)
        self.verticalLayout.addWidget(self.form)
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setContentsMargins(9, 0, 9, 0)
        self.buttonsLayout.setSpacing(20)
        self.buttonsLayout.setObjectName("buttonsLayout")
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.buttonsLayout.addItem(spacerItem9)
        self.btnApply = QtWidgets.QPushButton(parent=self.dlg_frame)
        self.btnApply.setMinimumSize(QtCore.QSize(0, 28))
        self.btnApply.setFlat(True)
        self.btnApply.setObjectName("btnApply")
        self.buttonsLayout.addWidget(self.btnApply)
        self.btnDone = QtWidgets.QPushButton(parent=self.dlg_frame)
        self.btnDone.setMinimumSize(QtCore.QSize(0, 28))
        self.btnDone.setDefault(False)
        self.btnDone.setFlat(True)
        self.btnDone.setObjectName("btnDone")
        self.buttonsLayout.addWidget(self.btnDone)
        self.verticalLayout.addLayout(self.buttonsLayout)
        self.verticalLayout.setStretch(1, 1)
        self.VLayoutMain.addWidget(self.dlg_frame)

        self.retranslateUi(filterSetup)
        QtCore.QMetaObject.connectSlotsByName(filterSetup)

    def retranslateUi(self, filterSetup):
        _translate = QtCore.QCoreApplication.translate
        filterSetup.setWindowTitle(_translate("filterSetup", "Form"))
        self.hdr_lbl.setText(_translate("filterSetup", "Filter setup"))
        self.subDirs.setText(_translate("filterSetup", "all subfolders"))
        self.no_folder.setText(_translate("filterSetup", "files not included in any folder"))
        self.all_btn.setText(_translate("filterSetup", "all"))
        self.any_btn.setText(_translate("filterSetup", "any"))
        self.open_sel.setText(_translate("filterSetup", "open #"))
        self.open_cond.setItemText(0, _translate("filterSetup", "<="))
        self.open_cond.setItemText(1, _translate("filterSetup", ">"))
        self.rating_sel.setText(_translate("filterSetup", "rating"))
        self.rating_cond.setItemText(0, _translate("filterSetup", "<"))
        self.rating_cond.setItemText(1, _translate("filterSetup", "="))
        self.rating_cond.setItemText(2, _translate("filterSetup", ">"))
        self.label_3.setText(_translate("filterSetup", "Date of"))
        self.date_type.setItemText(0, _translate("filterSetup", "opened"))
        self.date_type.setItemText(1, _translate("filterSetup", "modified"))
        self.date_type.setItemText(2, _translate("filterSetup", "added"))
        self.date_type.setItemText(3, _translate("filterSetup", "published"))
        self.date_type.setItemText(4, _translate("filterSetup", "note_date"))
        self.note_date_type.setItemText(0, _translate("filterSetup", "last modified"))
        self.note_date_type.setItemText(1, _translate("filterSetup", "any modified"))
        self.note_date_type.setItemText(2, _translate("filterSetup", "last created"))
        self.note_date_type.setItemText(3, _translate("filterSetup", "any created"))
        self.after.setText(_translate("filterSetup", "after"))
        self.before.setText(_translate("filterSetup", "before"))
        self.btnApply.setText(_translate("filterSetup", "Apply"))
        self.btnDone.setText(_translate("filterSetup", "Done"))
