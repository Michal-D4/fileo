# Form implementation generated from reading ui file 'c:\Users\mihal\OneDrive\Documents\pyprj\fileo\src\fileo\widgets\set_filter.ui'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_filterSetup(object):
    def setupUi(self, filterSetup):
        filterSetup.setObjectName("filterSetup")
        filterSetup.resize(356, 419)
        self.verticalLayout = QtWidgets.QVBoxLayout(filterSetup)
        self.verticalLayout.setObjectName("verticalLayout")
        self.form = QtWidgets.QFrame(filterSetup)
        self.form.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.form.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.form.setObjectName("form")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.form)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.hrdFrame = QtWidgets.QFrame(self.form)
        self.hrdFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.hrdFrame.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.hrdFrame.setObjectName("hrdFrame")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.hrdFrame)
        self.horizontalLayout_6.setContentsMargins(-1, 6, -1, 6)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.hdr_lbl = QtWidgets.QLabel(self.hrdFrame)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.hdr_lbl.setFont(font)
        self.hdr_lbl.setObjectName("hdr_lbl")
        self.horizontalLayout_6.addWidget(self.hdr_lbl)
        self.verticalLayout_3.addWidget(self.hrdFrame)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(9, -1, 9, -1)
        self.formLayout.setObjectName("formLayout")
        self.selected_dir = QtWidgets.QCheckBox(self.form)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.selected_dir.setFont(font)
        self.selected_dir.setChecked(True)
        self.selected_dir.setObjectName("selected_dir")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.LabelRole, self.selected_dir)
        self.dir_list = QtWidgets.QPlainTextEdit(self.form)
        self.dir_list.setMaximumSize(QtCore.QSize(16777215, 40))
        self.dir_list.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.dir_list.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.dir_list.setReadOnly(False)
        self.dir_list.setObjectName("dir_list")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.ItemRole.FieldRole, self.dir_list)
        self.tag_list = QtWidgets.QPlainTextEdit(self.form)
        self.tag_list.setMaximumSize(QtCore.QSize(16777215, 40))
        self.tag_list.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.tag_list.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.tag_list.setReadOnly(True)
        self.tag_list.setObjectName("tag_list")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.FieldRole, self.tag_list)
        self.selected_ext = QtWidgets.QCheckBox(self.form)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.selected_ext.setFont(font)
        self.selected_ext.setObjectName("selected_ext")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.LabelRole, self.selected_ext)
        self.ext_list = QtWidgets.QPlainTextEdit(self.form)
        self.ext_list.setMaximumSize(QtCore.QSize(16777215, 40))
        self.ext_list.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.ext_list.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.ext_list.setReadOnly(True)
        self.ext_list.setObjectName("ext_list")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.ItemRole.FieldRole, self.ext_list)
        self.selected_author = QtWidgets.QCheckBox(self.form)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.selected_author.setFont(font)
        self.selected_author.setObjectName("selected_author")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.LabelRole, self.selected_author)
        self.author_list = QtWidgets.QPlainTextEdit(self.form)
        self.author_list.setMaximumSize(QtCore.QSize(16777215, 40))
        self.author_list.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.author_list.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.author_list.setReadOnly(True)
        self.author_list.setObjectName("author_list")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.ItemRole.FieldRole, self.author_list)
        self.open_sel = QtWidgets.QCheckBox(self.form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.open_sel.setFont(font)
        self.open_sel.setObjectName("open_sel")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.ItemRole.LabelRole, self.open_sel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.open_cond = QtWidgets.QComboBox(self.form)
        self.open_cond.setMinimumSize(QtCore.QSize(99, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.open_cond.setFont(font)
        self.open_cond.setObjectName("open_cond")
        self.open_cond.addItem("")
        self.open_cond.addItem("")
        self.horizontalLayout.addWidget(self.open_cond)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.open_edit = QtWidgets.QSpinBox(self.form)
        self.open_edit.setObjectName("open_edit")
        self.horizontalLayout.addWidget(self.open_edit)
        self.formLayout.setLayout(4, QtWidgets.QFormLayout.ItemRole.FieldRole, self.horizontalLayout)
        self.rating_sel = QtWidgets.QCheckBox(self.form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rating_sel.setFont(font)
        self.rating_sel.setObjectName("rating_sel")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.ItemRole.LabelRole, self.rating_sel)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.rating_cond = QtWidgets.QComboBox(self.form)
        self.rating_cond.setMinimumSize(QtCore.QSize(99, 0))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.rating_cond.setFont(font)
        self.rating_cond.setObjectName("rating_cond")
        self.rating_cond.addItem("")
        self.rating_cond.addItem("")
        self.rating_cond.addItem("")
        self.horizontalLayout_2.addWidget(self.rating_cond)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.rating_edit = QtWidgets.QSpinBox(self.form)
        self.rating_edit.setObjectName("rating_edit")
        self.horizontalLayout_2.addWidget(self.rating_edit)
        self.formLayout.setLayout(5, QtWidgets.QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_2 = QtWidgets.QLabel(self.form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_3.addWidget(self.label_2)
        self.date_type = QtWidgets.QComboBox(self.form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.date_type.setFont(font)
        self.date_type.setObjectName("date_type")
        self.date_type.addItem("")
        self.date_type.addItem("")
        self.date_type.addItem("")
        self.date_type.addItem("")
        self.horizontalLayout_3.addWidget(self.date_type)
        self.formLayout.setLayout(6, QtWidgets.QFormLayout.ItemRole.LabelRole, self.horizontalLayout_3)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.after = QtWidgets.QCheckBox(self.form)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.after.setFont(font)
        self.after.setChecked(True)
        self.after.setObjectName("after")
        self.horizontalLayout_4.addWidget(self.after)
        self.after_date = QtWidgets.QDateEdit(self.form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.after_date.setFont(font)
        self.after_date.setObjectName("after_date")
        self.horizontalLayout_4.addWidget(self.after_date)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.before = QtWidgets.QCheckBox(self.form)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.before.setFont(font)
        self.before.setObjectName("before")
        self.horizontalLayout_5.addWidget(self.before)
        self.before_date = QtWidgets.QDateEdit(self.form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.before_date.setFont(font)
        self.before_date.setObjectName("before_date")
        self.horizontalLayout_5.addWidget(self.before_date)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.formLayout.setLayout(6, QtWidgets.QFormLayout.ItemRole.FieldRole, self.verticalLayout_2)
        self.frame_tag = QtWidgets.QFrame(self.form)
        self.frame_tag.setMaximumSize(QtCore.QSize(16777215, 21))
        self.frame_tag.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.frame_tag.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.frame_tag.setLineWidth(1)
        self.frame_tag.setObjectName("frame_tag")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_tag)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.selected_tag = QtWidgets.QCheckBox(self.frame_tag)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.selected_tag.setFont(font)
        self.selected_tag.setChecked(True)
        self.selected_tag.setObjectName("selected_tag")
        self.horizontalLayout_7.addWidget(self.selected_tag)
        self.all_btn = QtWidgets.QRadioButton(self.frame_tag)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.all_btn.setFont(font)
        self.all_btn.setChecked(True)
        self.all_btn.setObjectName("all_btn")
        self.horizontalLayout_7.addWidget(self.all_btn)
        self.any_btn = QtWidgets.QRadioButton(self.frame_tag)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.any_btn.setFont(font)
        self.any_btn.setObjectName("any_btn")
        self.horizontalLayout_7.addWidget(self.any_btn)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.ItemRole.LabelRole, self.frame_tag)
        self.verticalLayout_3.addLayout(self.formLayout)
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.setContentsMargins(9, 9, 9, 9)
        self.buttonsLayout.setSpacing(20)
        self.buttonsLayout.setObjectName("buttonsLayout")
        self.btnApply = QtWidgets.QPushButton(self.form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.btnApply.setFont(font)
        self.btnApply.setObjectName("btnApply")
        self.buttonsLayout.addWidget(self.btnApply)
        self.btnDone = QtWidgets.QPushButton(self.form)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.btnDone.setFont(font)
        self.btnDone.setDefault(True)
        self.btnDone.setObjectName("btnDone")
        self.buttonsLayout.addWidget(self.btnDone)
        self.verticalLayout_3.addLayout(self.buttonsLayout)
        self.verticalLayout.addWidget(self.form)

        self.retranslateUi(filterSetup)
        QtCore.QMetaObject.connectSlotsByName(filterSetup)

    def retranslateUi(self, filterSetup):
        _translate = QtCore.QCoreApplication.translate
        filterSetup.setWindowTitle(_translate("filterSetup", "Form"))
        self.hdr_lbl.setText(_translate("filterSetup", "Filter setup"))
        self.open_sel.setText(_translate("filterSetup", "file open number"))
        self.open_cond.setItemText(0, _translate("filterSetup", "less or equal"))
        self.open_cond.setItemText(1, _translate("filterSetup", "greate then"))
        self.rating_sel.setText(_translate("filterSetup", "rating"))
        self.rating_cond.setItemText(0, _translate("filterSetup", "less than"))
        self.rating_cond.setItemText(1, _translate("filterSetup", "equal to"))
        self.rating_cond.setItemText(2, _translate("filterSetup", "great than"))
        self.label_2.setText(_translate("filterSetup", "Date of"))
        self.date_type.setItemText(0, _translate("filterSetup", "opened"))
        self.date_type.setItemText(1, _translate("filterSetup", "modified"))
        self.date_type.setItemText(2, _translate("filterSetup", "published"))
        self.date_type.setItemText(3, _translate("filterSetup", "commented"))
        self.after.setText(_translate("filterSetup", "after"))
        self.before.setText(_translate("filterSetup", "before"))
        self.all_btn.setText(_translate("filterSetup", "all"))
        self.any_btn.setText(_translate("filterSetup", "any"))
        self.btnApply.setText(_translate("filterSetup", "Apply"))
        self.btnDone.setText(_translate("filterSetup", "Done"))
