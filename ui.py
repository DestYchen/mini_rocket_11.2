from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from dateutil.relativedelta import relativedelta

import re
import sys
import os
import time
import logging
from datetime import datetime
from read_data import *
#from collect_data import *
from ui_dict import *
from calculations import calculate
from valid import validate_data
#Creating a logger
logger = logging.getLogger(__name__)
logging.basicConfig(filename='error.log', filemode='w', level=logging.DEBUG,encoding='utf8')


#Функция для праивльной отрисовки графиков при выборе показателя "ROE". 
def graph_roe(list):
    resul = np.empty(np.array(list).shape)
    for i in range(len(list)):
        if isinstance(list[i], str):
            if "недостаточно данных" in list[i]:
                resul[i] = 0
            elif " (Чистая прибыль отрицательная.)" in list[i]:
                list[i] = list[i].replace(" (Чистая прибыль отрицательная.)", "")
                list[i] = list[i].replace(" ", "")
                resul[i] = list[i]

            elif " (Капитал отрицательный.)" in list[i]:
                resul[i] = 0

            elif " (Чистая прибыль и капитал отрицательны.)" in list[i]:
                resul[i] = 0

            else:
                resul[i] = list[i]
        
        else:
            resul[i] = list[i]

    return resul


try:
    class Ui_MainWindow(QtWidgets.QMainWindow):

        def setupUi(self, MainWindow):

            self.desire_dates = []
            """список выбранных дат(меняется одновременно с выбором даты на вкладке)"""

            self.selection_names_list = []
            """список выбранных ЛК(если сделан Ручной выбор)"""

            self.final_answer = []
            """численный ответ последнего расчета"""

            self.final_dates = []
            """выбранные даты последнего выполненного расчета"""

            self.comp_period=7
            """(соп. выборка)количество ненулевых дат"""

            self.comp_point=['5.1',]
            """(соп. выборка)список пунктов, по которым определяяется сопоставимость"""

            MainWindow.setObjectName("MainWindow")
            MainWindow.resize(1021, 650)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
            MainWindow.setSizePolicy(sizePolicy)
            palette = QtGui.QPalette()
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
            brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
            brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
            brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
            brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
            brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
            brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
            brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
            MainWindow.setPalette(palette)
            icon = QtGui.QIcon.fromTheme("logo.jpg")
            MainWindow.setWindowIcon(icon)
            MainWindow.setStyleSheet("QWidget {\n"
                                     "    color: black;\n"
                                     "    background-color: white;\n"
                                     "    font-family: Rubik;\n"
                                     "    font-weight: 400;\n"
                                     "}\n"
                                     "\n"
                                     "QComboBox:disabled {"
                                     "color:gray;\n"
                                     "border: 1px solid lightgray; \n}"
                                     "QComboBox {\n"
                                     "    border: 1px solid gray;\n"
                                     "    border-radius: 3px;\n"
                                     "        padding: 1px 18px 1px 3px;\n"
                                     "    min-width: 6em;\n"
                                     "}\n"
                                     "\n"
                                     "QRadioButton:disabled {"
                                     "color:gray;\n"
                                     "}"
                                     "QCheckBox:disabled {"
                                     "color:gray;\n"
                                     "}"
                                     "QPushButton:disabled {"
                                     "color:gray;\n"
                                     "border: 1px solid lightgray; \n}"
                                     "QPushButton{\n"
                                     "    border: 2px solid #8f8f91;\n"
                                     "    border-radius: 6px;\n"
                                     "    border-style: outset;\n"
                                     "    border-color: rgb(194, 194, 194);\n"
                                     "}\n"
                                     "\n"
                                     "QPushButton:hover {\n"
                                     "    background-color: rgb(194, 194, 194);\n"
                                     "}\n"
                                     "\n"
                                     "QPushButton:pressed {\n"
                                     "    background-color: rgb(232, 232, 232);\n"
                                     "}\n"
                                     "")
            self.gridLayout_3 = QtWidgets.QGridLayout(MainWindow)
            self.gridLayout_3.setObjectName("gridLayout_3")
            self.tabWidget = QtWidgets.QTabWidget(MainWindow)
            self.tabWidget.setEnabled(True)
            self.tabWidget.setStyleSheet("")
            self.tabWidget.setTabShape(QtWidgets.QTabWidget.Triangular)
            self.tabWidget.setObjectName("tabWidget")

            self.tab_main = QtWidgets.QWidget()
            """Главная вкладка"""
            self.tab_main.setObjectName("tab_main")
            self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_main)
            self.gridLayout_4.setObjectName("gridLayout_4")
            self.rep_type = QtWidgets.QGroupBox(self.tab_main)
            """GroupBox: тип отчета(экономические индикаторы, управленчиские данные)"""
            self.rep_type.setObjectName("rep_type")
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.rep_type.sizePolicy().hasHeightForWidth())
            self.rep_type.setSizePolicy(sizePolicy)
            self.gridLayout_11 = QtWidgets.QGridLayout(self.rep_type)
            self.gridLayout_11.setObjectName("gridLayout_11")
            self.rep_ecind_rb = QtWidgets.QRadioButton(self.rep_type)
            """кнопка отчета типа экономический индикатор"""
            self.rep_ecind_rb.setObjectName("rep_ecind_rb")
            self.gridLayout_11.addWidget(self.rep_ecind_rb, 0, 0, 1, 1)
            self.rep_datmanage_rb = QtWidgets.QRadioButton(self.rep_type)
            """кнопка отчета типа управленческие данные"""
            self.rep_datmanage_rb.setObjectName("rep_datmanage_rb")
            self.gridLayout_11.addWidget(self.rep_datmanage_rb, 0, 1, 1, 1)
            self.rep_msfo_rb = QtWidgets.QRadioButton(self.rep_type)
            """кнопка отчета типа МСФО"""
            self.rep_msfo_rb.setObjectName("rep_msfo_rb")
            self.gridLayout_11.addWidget(self.rep_msfo_rb, 0, 2, 1, 1)
            self.rep_fsbu_rb = QtWidgets.QRadioButton(self.rep_type)
            """кнопка отчета типа ФСБУ"""
            self.rep_fsbu_rb.setObjectName("rep_fsbu_rb")
            self.gridLayout_11.addWidget(self.rep_fsbu_rb, 0, 3, 1, 1)
            self.gridLayout_4.addWidget(self.rep_type, 0, 0, 1, 1)
            self.answ_box = QtWidgets.QGroupBox(self.tab_main)
            """(GroupBox)для ответа на главной вкладке"""
            self.answ_box.setObjectName("answ_box")
            self.gridLayout_5 = QtWidgets.QGridLayout(self.answ_box)
            self.gridLayout_5.setObjectName("gridLayout_5")
            # ---------------------------------------------------------------
            self.result_label = QtWidgets.QTextEdit(self.answ_box)
            """(TextEdit)результат на главной вкладке"""
            self.result_label.setReadOnly(True)
            # self.result_label=ScrollLabel(self.answ_box)
            # self.result_label = QtWidgets.QLabel(self.answ_box)---------------
            self.result_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.result_label.setText("")
            self.result_label.setObjectName("result_label")
            self.gridLayout_5.addWidget(self.result_label, 0, 0, 1, 1)
            self.gridLayout_4.addWidget(self.answ_box, 0, 1, 5, 1)
            self.result_label.setStyleSheet("QTextEdit{\n"
                                            "    background-color:rgb(220, 220, 220);\n"
                                            "    font-family: Rubik;\n"
                                            "    font-weight: 400;\n"
                                            "    font-size: 11pt;\n"
                                            "}")
            self.lk_attribute_group = QtWidgets.QGroupBox(self.tab_main)
            """(GroupBox)типы выборки ЛК"""
            self.lk_attribute_group.setObjectName("lk_attribute_group")
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                               QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.lk_attribute_group.sizePolicy().hasHeightForWidth())
            self.lk_attribute_group.setSizePolicy(sizePolicy)
            # self.lk_attribute_group.setMinimumSize(QtCore.QSize(35, 35))
            # self.lk_attribute_group.setMaximumSize(QtCore.QSize(50, 50))
            self.gridLayout_7 = QtWidgets.QGridLayout(self.lk_attribute_group)
            self.gridLayout_7.setObjectName("gridLayout_7")

            self.comp_btns_group=QtWidgets.QGroupBox(self.lk_attribute_group)
            """(GroupBox)группа кнопок сопоставимых выборок"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                               QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.comp_btns_group.sizePolicy().hasHeightForWidth())
            self.comp_btns_group.setSizePolicy(sizePolicy)
            self.vlayout=QtWidgets.QVBoxLayout(self.comp_btns_group)
            self.gridLayout_7.addWidget(self.comp_btns_group, 0, 0, 1, 1)
            self.comparable_lk_rb = QtWidgets.QRadioButton(self.comp_btns_group)
            """кнопка сопоставимая выборка"""
            self.comparable_lk_rb.setObjectName("comparable_lk_rb")
            self.cust_comparable_lk_rb = QtWidgets.QRadioButton(self.comp_btns_group)
            """кнопка настраиваемая сопоставимая выборка"""
            self.cust_comparable_lk_rb.setObjectName("cust_comparable_lk_rb")
            self.vlayout.addWidget(self.comparable_lk_rb)
            self.vlayout.addWidget(self.cust_comparable_lk_rb)
            self.comparable_hint_lbl=QtWidgets.QLabel(self.comp_btns_group)
            """Label с текстом условий сопоставимой выборки на данный момент"""
            self.vlayout.addWidget(self.comparable_hint_lbl)
            #self.gridLayout_7.addWidget(self.comparable_lk_rb, 0, 0, 1, 1)
            self.all_lk_rb = QtWidgets.QRadioButton(self.lk_attribute_group)
            """кнопка выборка всех лк"""
            self.all_lk_rb.setObjectName("all_lk_rb")
            self.gridLayout_7.addWidget(self.all_lk_rb, 0, 1, 1, 1)
            self.not_gtlk_check = QtWidgets.QCheckBox(self.lk_attribute_group)
            """исключить АО ГТЛК"""
            self.not_gtlk_check.setObjectName("not_gtlk_check")
            self.gridLayout_7.addWidget(self.not_gtlk_check, 0, 2, 1, 1)
            self.users_lk_rb = QtWidgets.QRadioButton(self.lk_attribute_group)
            """кнопка ручная выборка ЛК"""
            self.users_lk_rb.setStyleSheet("")
            self.users_lk_rb.setObjectName("users_lk_rb")
            self.gridLayout_7.addWidget(self.users_lk_rb, 0, 3, 1, 1)

            self.form_report_pb = QtWidgets.QPushButton(self.lk_attribute_group)
            """кнопка отчет по компании"""
            self.form_report_pb.setStyleSheet("")
            self.form_report_pb.setObjectName("form_report_pb")
            self.form_report_pb.setMinimumSize(QtCore.QSize(130, 35))
            self.gridLayout_7.addWidget(self.form_report_pb, 1, 3, 1, 1)

            self.gridLayout_4.addWidget(self.lk_attribute_group, 1, 0, 1, 1)
            self.lk_type_group = QtWidgets.QGroupBox(self.tab_main)
            """(GroupBox)кнопки выбора классификации ЛК"""
            self.lk_type_group.setObjectName("lk_type_group")
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                               QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setRetainSizeWhenHidden(True)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.lk_type_group.sizePolicy().hasHeightForWidth())
            self.lk_type_group.setSizePolicy(sizePolicy)
            self.gridLayout_8 = QtWidgets.QGridLayout(self.lk_type_group)
            self.gridLayout_8.setObjectName("gridLayout_8")
            self.type_cb_rb = QtWidgets.QRadioButton(self.lk_type_group)
            """кнопка классификация цб"""
            self.type_cb_rb.setObjectName("type_cb_rb")
            self.gridLayout_8.addWidget(self.type_cb_rb, 0, 0, 1, 1)
            self.type_ola_rb = QtWidgets.QRadioButton(self.lk_type_group)
            """кнопка классификация ОЛА"""
            self.type_ola_rb.setObjectName("type_ola_rb")
            self.gridLayout_8.addWidget(self.type_ola_rb, 0, 1, 1, 1)
            self.cb_comb = QtWidgets.QComboBox(self.lk_type_group)
            """(ComboBox)выбор типа из классификации цб """
            self.cb_comb.setObjectName("cb_comb")
            self.gridLayout_8.addWidget(self.cb_comb, 1, 0, 1, 1)
            self.ola_comb = QtWidgets.QComboBox(self.lk_type_group)
            """(ComboBox)выбор типа из классификации ола """
            self.ola_comb.setObjectName("ola_comb")
            self.gridLayout_8.addWidget(self.ola_comb, 1, 1, 1, 1)
            self.gridLayout_4.addWidget(self.lk_type_group, 2, 0, 1, 1)
            self.dates_group = QtWidgets.QGroupBox(self.tab_main)
            """(GroupBox)выбор дат"""
            self.dates_group.setObjectName("dates_group")
            self.gridLayout_6 = QtWidgets.QGridLayout(self.dates_group)
            self.gridLayout_6.setObjectName("gridLayout_6")
            self.date1 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date1.setObjectName("date1")
            self.gridLayout_6.addWidget(self.date1, 0, 0, 1, 1)
            self.date2 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date2.setObjectName("date2")
            self.gridLayout_6.addWidget(self.date2, 0, 1, 1, 1)
            self.date3 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date3.setObjectName("date3")
            self.gridLayout_6.addWidget(self.date3, 0, 2, 1, 1)
            self.date4 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date4.setObjectName("date4")
            self.gridLayout_6.addWidget(self.date4, 0, 3, 1, 1)
            self.date5 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date5.setObjectName("date5")
            self.gridLayout_6.addWidget(self.date5, 1, 0, 1, 1)
            self.date6 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date6.setObjectName("date6")
            self.gridLayout_6.addWidget(self.date6, 1, 1, 1, 1)
            self.date7 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date7.setObjectName("date7")
            self.gridLayout_6.addWidget(self.date7, 1, 2, 1, 1)
            self.date8 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date8.setObjectName("date8")
            self.gridLayout_6.addWidget(self.date8, 1, 3, 1, 1)
            self.date9 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date9.setObjectName("date9")
            self.gridLayout_6.addWidget(self.date9, 2, 0, 1, 1)
            self.date10 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date10.setObjectName("date10")
            self.gridLayout_6.addWidget(self.date10, 2, 1, 1, 1)
            self.date11 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date11.setObjectName("date11")
            self.gridLayout_6.addWidget(self.date11, 2, 2, 1, 1)
            self.date12 = QtWidgets.QCheckBox(self.dates_group)
            """(CheckBox)дата"""
            self.date12.setObjectName("date12")
            self.gridLayout_6.addWidget(self.date12, 2, 3, 1, 1)
            self.gridLayout_4.addWidget(self.dates_group, 3, 0, 1, 1)
            self.param_group = QtWidgets.QGroupBox(self.tab_main)
            """(GroupBox)группа кнопок выбора параметра вычислений(главная вкладка)"""
            self.param_group.setObjectName("param_group")
            self.gridLayout_9 = QtWidgets.QGridLayout(self.param_group)
            self.gridLayout_9.setObjectName("gridLayout_9")
            self.param_msfo_rb = QtWidgets.QRadioButton(self.param_group)
            """кнопка параметр мсфо"""
            self.param_msfo_rb.setObjectName("param_msfo_rb")
            self.gridLayout_9.addWidget(self.param_msfo_rb, 0, 0, 1, 1)
            self.param_fsbu_rb = QtWidgets.QRadioButton(self.param_group)
            """кнопка параметр фсбу"""
            self.param_fsbu_rb.setObjectName("param_fsbu_rb")
            self.gridLayout_9.addWidget(self.param_fsbu_rb, 0, 1, 1, 1)
            self.sliding_check = QtWidgets.QCheckBox(self.param_group)
            """(CheckBox)выбор скользящего года"""
            self.sliding_check.setObjectName("sliding_check")
            self.gridLayout_9.addWidget(self.sliding_check, 0, 2, 1, 1)
            self.prod_label = QtWidgets.QLabel(self.param_group)
            self.prod_label.setObjectName("prod_label")
            self.gridLayout_9.addWidget(self.prod_label, 1, 0, 1, 1)
            self.product_comb = QtWidgets.QComboBox(self.param_group)
            """(ComboBox)выбор типа продукта(все, опер.аренда..)"""
            self.product_comb.setObjectName("product_comb")
            self.gridLayout_9.addWidget(self.product_comb, 2, 0, 1, 2)
            self.param_type_group = QtWidgets.QGroupBox(self.param_group)
            """(GroupBox)группа кнопок выбора вычислений параметра(главная вкладка)"""
            self.param_type_group.setTitle("")
            self.param_type_group.setObjectName("param_type_group")
            self.gridLayout_10 = QtWidgets.QGridLayout(self.param_type_group)
            self.gridLayout_10.setObjectName("gridLayout_10")
            self.premade_param_rb = QtWidgets.QRadioButton(self.param_type_group)
            """кнопка Готовый показатель"""
            self.premade_param_rb.setObjectName("premade_param_rb")
            self.gridLayout_10.addWidget(self.premade_param_rb, 0, 0, 1, 1)
            self.custom_param_rb = QtWidgets.QRadioButton(self.param_type_group)
            """кнопка Свой показатель"""
            self.custom_param_rb.setObjectName("custom_param_rb")
            self.gridLayout_10.addWidget(self.custom_param_rb, 0, 1, 1, 1)
            self.gridLayout_9.addWidget(self.param_type_group, 3, 0, 1, 4)
            self.point_comb = QtWidgets.QComboBox(self.param_group)
            """(ComboBox)список доступных для вычисления готовых параметров"""
            self.point_comb.setObjectName("point_comb")
            self.gridLayout_9.addWidget(self.point_comb, 4, 0, 1, 4)
            self.validate_rb = QtWidgets.QPushButton(self.param_group)
            """кнопка валидации данных"""
            self.validate_rb.setStyleSheet("QPushButton {\n"
                                               "    border: 2px solid #8f8f91;\n"
                                               "    border-radius: 6px;\n"
                                               "    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
                                               "                                      stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
                                               "    min-width: 80px;\n"
                                               "}\n"
                                               "\n"
                                               "QPushButton:hover {\n"
                                               "    background-color: rgb(194, 194, 194);\n"
                                               "}\n"
                                               "\n"
                                               "QPushButton:pressed {\n"
                                               "    background-color: rgb(232, 232, 232);\n"
                                               "}\n"
                                               "")
            self.validate_rb.setObjectName("validate_rb")
            self.gridLayout_9.addWidget(self.validate_rb, 5, 1, 1, 1)

            self.build_graphs_rb = QtWidgets.QPushButton(self.param_group)
            """кнопка построить графики(строит набор стандартных графиков)"""
            self.build_graphs_rb.setStyleSheet("QPushButton {\n"
                                               "    border: 2px solid #8f8f91;\n"
                                               "    border-radius: 6px;\n"
                                               "    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
                                               "                                      stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
                                               "    min-width: 80px;\n"
                                               "}\n"
                                               "\n"
                                               "QPushButton:hover {\n"
                                               "    background-color: rgb(194, 194, 194);\n"
                                               "}\n"
                                               "\n"
                                               "QPushButton:pressed {\n"
                                               "    background-color: rgb(232, 232, 232);\n"
                                               "}\n"
                                               "")
            self.build_graphs_rb.setObjectName("build_graphs_rb")
            self.gridLayout_9.addWidget(self.build_graphs_rb, 5, 2, 1, 1)

            self.export_excel = QtWidgets.QPushButton(self.param_group)
            """кнопка экспорта расчета в excel"""
            self.export_excel.setStyleSheet("QPushButton {\n"
                                            "    border: 2px solid #8f8f91;\n"
                                            "    border-radius: 6px;\n"
                                            "    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
                                            "                                      stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
                                            "    min-width: 80px;\n"
                                            "}\n"
                                            "\n"
                                            "QPushButton:hover {\n"
                                            "    background-color: rgb(194, 194, 194);\n"
                                            "}\n"
                                            "\n"
                                            "QPushButton:pressed {\n"
                                            "    background-color: rgb(232, 232, 232);\n"
                                            "}\n"
                                            "")
            self.export_excel.setObjectName("export_excel")
            self.gridLayout_9.addWidget(self.export_excel, 5, 3, 1, 1)
            self.calc_pb = QtWidgets.QPushButton(self.param_group)
            """кнопка Расчет"""
            palette = QtGui.QPalette()
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
            gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, 1.0)
            gradient.setSpread(QtGui.QGradient.PadSpread)
            gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QtGui.QColor(246, 247, 250))
            gradient.setColorAt(1.0, QtGui.QColor(218, 219, 222))
            brush = QtGui.QBrush(gradient)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
            gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, 1.0)
            gradient.setSpread(QtGui.QGradient.PadSpread)
            gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QtGui.QColor(246, 247, 250))
            gradient.setColorAt(1.0, QtGui.QColor(218, 219, 222))
            brush = QtGui.QBrush(gradient)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
            gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, 1.0)
            gradient.setSpread(QtGui.QGradient.PadSpread)
            gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QtGui.QColor(246, 247, 250))
            gradient.setColorAt(1.0, QtGui.QColor(218, 219, 222))
            brush = QtGui.QBrush(gradient)
            palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
            gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, 1.0)
            gradient.setSpread(QtGui.QGradient.PadSpread)
            gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QtGui.QColor(246, 247, 250))
            gradient.setColorAt(1.0, QtGui.QColor(218, 219, 222))
            brush = QtGui.QBrush(gradient)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
            gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, 1.0)
            gradient.setSpread(QtGui.QGradient.PadSpread)
            gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QtGui.QColor(246, 247, 250))
            gradient.setColorAt(1.0, QtGui.QColor(218, 219, 222))
            brush = QtGui.QBrush(gradient)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
            gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, 1.0)
            gradient.setSpread(QtGui.QGradient.PadSpread)
            gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QtGui.QColor(246, 247, 250))
            gradient.setColorAt(1.0, QtGui.QColor(218, 219, 222))
            brush = QtGui.QBrush(gradient)
            palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
            gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, 1.0)
            gradient.setSpread(QtGui.QGradient.PadSpread)
            gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QtGui.QColor(246, 247, 250))
            gradient.setColorAt(1.0, QtGui.QColor(218, 219, 222))
            brush = QtGui.QBrush(gradient)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
            brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
            brush.setStyle(QtCore.Qt.SolidPattern)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
            gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, 1.0)
            gradient.setSpread(QtGui.QGradient.PadSpread)
            gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QtGui.QColor(246, 247, 250))
            gradient.setColorAt(1.0, QtGui.QColor(218, 219, 222))
            brush = QtGui.QBrush(gradient)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
            gradient = QtGui.QLinearGradient(0.0, 0.0, 0.0, 1.0)
            gradient.setSpread(QtGui.QGradient.PadSpread)
            gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
            gradient.setColorAt(0.0, QtGui.QColor(246, 247, 250))
            gradient.setColorAt(1.0, QtGui.QColor(218, 219, 222))
            brush = QtGui.QBrush(gradient)
            palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
            self.calc_pb.setPalette(palette)
            self.calc_pb.setStyleSheet("QPushButton {\n"
                                       "    border: 2px solid #8f8f91;\n"
                                       "    border-radius: 6px;\n"
                                       "    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,\n"
                                       "                                      stop: 0 #f6f7fa, stop: 1 #dadbde);\n"
                                       "    min-width: 80px;\n"
                                       "}\n"
                                       "\n"
                                       "QPushButton:hover {\n"
                                       "    background-color: rgb(194, 194, 194);\n"
                                       "}\n"
                                       "\n"
                                       "QPushButton:pressed {\n"
                                       "    background-color: rgb(232, 232, 232);\n"
                                       "}\n"
                                       "")
            self.calc_pb.setObjectName("calc_pb")
            self.gridLayout_9.addWidget(self.calc_pb, 5, 4, 1, 1)
            self.gridLayout_4.addWidget(self.param_group, 4, 0, 1, 1)
            self.tabWidget.addTab(self.tab_main, "")
            self.tab_user_choice = QtWidgets.QWidget()
            """вкладка ручной выбор лк"""
            self.tab_user_choice.setObjectName("tab_user_choice")
            self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.tab_user_choice)
            self.horizontalLayout_3.setObjectName("horizontalLayout_3")
            self.avcomp_group = QtWidgets.QGroupBox(self.tab_user_choice)
            """(GroupBox)содержит список доступных для выбора ЛК"""
            self.avcomp_group.setObjectName("avcomp_group")
            self.verticalLayout = QtWidgets.QVBoxLayout(self.avcomp_group)
            self.verticalLayout.setObjectName("verticalLayout")
            self.avcomp_list = QtWidgets.QListWidget(self.avcomp_group)
            """список доступных для выбора ЛК"""
            self.avcomp_list.setObjectName("avcomp_list")
            self.avcomp_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.verticalLayout.addWidget(self.avcomp_list)
            self.horizontalLayout_3.addWidget(self.avcomp_group)
            self.move_group = QtWidgets.QGroupBox(self.tab_user_choice)
            """(GroupBox)содержит кнопки перемещения лк в ручном выборе"""
            self.move_group.setMaximumSize(QtCore.QSize(120, 16777215))
            self.move_group.setStyleSheet("QGroupBox{\n"
                                          "    border: none;\n"
                                          "}")
            self.move_group.setTitle("")
            self.move_group.setObjectName("move_group")
            self.formLayout = QtWidgets.QFormLayout(self.move_group)
            self.formLayout.setObjectName("formLayout")
            self.to_chosen_pb = QtWidgets.QPushButton(self.move_group)
            """кнопка переноса ЛК из доступных в выбранные Ручным выбором"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.to_chosen_pb.sizePolicy().hasHeightForWidth())
            self.to_chosen_pb.setSizePolicy(sizePolicy)
            self.to_chosen_pb.setMinimumSize(QtCore.QSize(100, 20))
            self.to_chosen_pb.setMaximumSize(QtCore.QSize(110, 16777215))
            self.to_chosen_pb.setObjectName("to_chosen_pb")
            self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.to_chosen_pb)
            self.to_available_pb = QtWidgets.QPushButton(self.move_group)
            """кнопка переноса ЛК из выбранных в доступные Ручным выбором"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.to_available_pb.sizePolicy().hasHeightForWidth())
            self.to_available_pb.setSizePolicy(sizePolicy)
            self.to_available_pb.setMinimumSize(QtCore.QSize(100, 20))
            self.to_available_pb.setMaximumSize(QtCore.QSize(110, 16777215))
            self.to_available_pb.setStyleSheet("")
            self.to_available_pb.setObjectName("to_available_pb")
            self.formLayout.setWidget(1, QtWidgets.QFormLayout.SpanningRole, self.to_available_pb)
            self.horizontalLayout_3.addWidget(self.move_group)
            self.chosen_group = QtWidgets.QGroupBox(self.tab_user_choice)
            """(GroupBox)группа с списком выбранных лк(ручной выбор)"""
            self.chosen_group.setObjectName("chosen_group")
            self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.chosen_group)
            self.verticalLayout_2.setObjectName("verticalLayout_2")
            self.chosen_list = QtWidgets.QListWidget(self.chosen_group)
            """список выбранных лк(ручной выбор)"""
            self.chosen_list.setObjectName("chosen_list")
            self.verticalLayout_2.addWidget(self.chosen_list)
            self.horizontalLayout_3.addWidget(self.chosen_group)
            self.chosen_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
            self.tabWidget.addTab(self.tab_user_choice, "")
            self.tab_custom_param = QtWidgets.QWidget()
            self.gridLayout_12 = QtWidgets.QGridLayout(self.tab_custom_param)
            self.gridLayout_12.setObjectName("gridLayout_12")
            self.custom_group = QtWidgets.QGroupBox(self.tab_custom_param)
            """(GroupBox)все кнопки для вкладки свой показатель"""
            self.custom_group.setStyleSheet("QGroupBox {\n"
                                            "    border: none;\n"
                                            "}")
            self.custom_group.setTitle("")
            self.custom_group.setObjectName("custom_group")
            self.gridLayout = QtWidgets.QGridLayout(self.custom_group)
            self.gridLayout.setObjectName("gridLayout")
            self.calc_layout = QtWidgets.QGridLayout()
            self.calc_layout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
            self.calc_layout.setObjectName("calc_layout")
            self.pb_add = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка +"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_add.sizePolicy().hasHeightForWidth())
            self.pb_add.setSizePolicy(sizePolicy)
            self.pb_add.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_add.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_add.setStyleSheet("QPushButton {\n"
                                      "    font-weight: 600;\n"
                                      "}")
            self.pb_add.setObjectName("pb_add")
            self.calc_layout.addWidget(self.pb_add, 0, 3, 1, 1)
            self.pb_3 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 3"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_3.sizePolicy().hasHeightForWidth())
            self.pb_3.setSizePolicy(sizePolicy)
            self.pb_3.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_3.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_3.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_3.setObjectName("pb_3")
            self.calc_layout.addWidget(self.pb_3, 3, 2, 1, 1)
            self.pb_subtract = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка -"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_subtract.sizePolicy().hasHeightForWidth())
            self.pb_subtract.setSizePolicy(sizePolicy)
            self.pb_subtract.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_subtract.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_subtract.setStyleSheet("QPushButton {\n"
                                           "    font-weight: 600;\n"
                                           "}")
            self.pb_subtract.setObjectName("pb_subtract")
            self.calc_layout.addWidget(self.pb_subtract, 3, 3, 1, 1)
            self.pb_9 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 9"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_9.sizePolicy().hasHeightForWidth())
            self.pb_9.setSizePolicy(sizePolicy)
            self.pb_9.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_9.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_9.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_9.setObjectName("pb_9")
            self.calc_layout.addWidget(self.pb_9, 1, 2, 1, 1)
            self.pb_clear_entry = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка CE (удаляет последний введенный набор символов)"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_clear_entry.sizePolicy().hasHeightForWidth())
            self.pb_clear_entry.setSizePolicy(sizePolicy)
            self.pb_clear_entry.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_clear_entry.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_clear_entry.setStyleSheet("QPushButton {\n"
                                              "    font-weight: 600;\n"
                                              "}")
            self.pb_clear_entry.setObjectName("pb_clear_entry")
            self.calc_layout.addWidget(self.pb_clear_entry, 0, 1, 1, 1)
            self.pb_8 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 8"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_8.sizePolicy().hasHeightForWidth())
            self.pb_8.setSizePolicy(sizePolicy)
            self.pb_8.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_8.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_8.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_8.setObjectName("pb_8")
            self.calc_layout.addWidget(self.pb_8, 1, 1, 1, 1)
            self.pb_7 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 7"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_7.sizePolicy().hasHeightForWidth())
            self.pb_7.setSizePolicy(sizePolicy)
            self.pb_7.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_7.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_7.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_7.setObjectName("pb_7")
            self.calc_layout.addWidget(self.pb_7, 1, 0, 1, 1)
            self.pb_clear = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка C (очистить ввод)"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_clear.sizePolicy().hasHeightForWidth())
            self.pb_clear.setSizePolicy(sizePolicy)
            self.pb_clear.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_clear.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_clear.setStyleSheet("QPushButton {\n"
                                        "    font-weight: 600;\n"
                                        "}")
            self.pb_clear.setObjectName("pb_clear")
            self.calc_layout.addWidget(self.pb_clear, 0, 0, 1, 1)
            self.pb_0 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 0"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_0.sizePolicy().hasHeightForWidth())
            self.pb_0.setSizePolicy(sizePolicy)
            self.pb_0.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_0.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_0.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_0.setObjectName("pb_0")
            self.calc_layout.addWidget(self.pb_0, 4, 0, 1, 1)

            self.pb_point = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка . """
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_point.sizePolicy().hasHeightForWidth())
            self.pb_point.setSizePolicy(sizePolicy)
            self.pb_point.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_point.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_point.setStyleSheet("QPushButton {\n"
                                        "    font-weight: 600;\n"
                                        "}")
            self.pb_point.setObjectName("pb_point")
            self.calc_layout.addWidget(self.pb_point, 0, 2, 1, 1)
            self.pb_bracket_open = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка ( """
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_bracket_open.sizePolicy().hasHeightForWidth())
            self.pb_bracket_open.setSizePolicy(sizePolicy)
            self.pb_bracket_open.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_bracket_open.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_bracket_open.setStyleSheet("QPushButton {\n"
                                               "    font-weight: 600;\n"
                                               "}")
            self.pb_bracket_open.setObjectName("pb_bracket_open")
            self.calc_layout.addWidget(self.pb_bracket_open, 4, 1, 1, 1)
            self.pb_bracket_close = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка ) """
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_bracket_close.sizePolicy().hasHeightForWidth())
            self.pb_bracket_close.setSizePolicy(sizePolicy)
            self.pb_bracket_close.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_bracket_close.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_bracket_close.setStyleSheet("QPushButton {\n"
                                                "    font-weight: 600;\n"
                                                "}")
            self.pb_bracket_close.setObjectName("pb_bracket_close")
            self.calc_layout.addWidget(self.pb_bracket_close, 4, 2, 1, 1)
            self.pb_multiply = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка * """
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_multiply.sizePolicy().hasHeightForWidth())
            self.pb_multiply.setSizePolicy(sizePolicy)
            self.pb_multiply.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_multiply.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_multiply.setStyleSheet("QPushButton {\n"
                                           "    font-weight: 600;\n"
                                           "}")
            self.pb_multiply.setObjectName("pb_multiply")
            self.calc_layout.addWidget(self.pb_multiply, 2, 3, 1, 1)
            self.pb_2 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 2"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_2.sizePolicy().hasHeightForWidth())
            self.pb_2.setSizePolicy(sizePolicy)
            self.pb_2.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_2.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_2.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_2.setObjectName("pb_2")
            self.calc_layout.addWidget(self.pb_2, 3, 1, 1, 1)
            self.pb_4 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 4 """
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_4.sizePolicy().hasHeightForWidth())
            self.pb_4.setSizePolicy(sizePolicy)
            self.pb_4.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_4.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_4.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_4.setObjectName("pb_4")
            self.calc_layout.addWidget(self.pb_4, 2, 0, 1, 1)
            self.pb_div = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка / """
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_div.sizePolicy().hasHeightForWidth())
            self.pb_div.setSizePolicy(sizePolicy)
            self.pb_div.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_div.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_div.setStyleSheet("QPushButton {\n"
                                      "    font-weight: 600;\n"
                                      "}")
            self.pb_div.setObjectName("pb_div")
            self.calc_layout.addWidget(self.pb_div, 1, 3, 1, 1)
            self.pb_1 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 1 """
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_1.sizePolicy().hasHeightForWidth())
            self.pb_1.setSizePolicy(sizePolicy)
            self.pb_1.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_1.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_1.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_1.setObjectName("pb_1")
            self.calc_layout.addWidget(self.pb_1, 3, 0, 1, 1)
            self.pb_6 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 6 """
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_6.sizePolicy().hasHeightForWidth())
            self.pb_6.setSizePolicy(sizePolicy)
            self.pb_6.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_6.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_6.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_6.setObjectName("pb_6")
            self.calc_layout.addWidget(self.pb_6, 2, 2, 1, 1)
            self.pb_5 = QtWidgets.QPushButton(self.custom_group)
            """(свой показатель)калькулятор кнопка 5 """
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pb_5.sizePolicy().hasHeightForWidth())
            self.pb_5.setSizePolicy(sizePolicy)
            self.pb_5.setMinimumSize(QtCore.QSize(35, 35))
            self.pb_5.setMaximumSize(QtCore.QSize(50, 50))
            self.pb_5.setStyleSheet("QPushButton {\n"
                                    "    font-weight: 600;\n"
                                    "}")
            self.pb_5.setObjectName("pb_5")
            self.calc_layout.addWidget(self.pb_5, 2, 1, 1, 1)
            self.gridLayout.addLayout(self.calc_layout, 6, 0, 1, 1)
            self.groupBox = QtWidgets.QGroupBox(self.custom_group)
            self.groupBox.setMinimumSize(QtCore.QSize(0, 150))
            self.groupBox.setStyleSheet("QGroupBox{\n"
                                        "    border: none;\n"
                                        "}")
            self.groupBox.setTitle("")
            self.groupBox.setObjectName("groupBox")

            self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox)
            self.verticalLayout_3.setObjectName(u"verticalLayout_3")
            self.custom_param_type_group = QtWidgets.QGroupBox(self.groupBox)
            """(GroupBox)группа кнопок выбора типа прироста в показателе(свой показатель)"""
            self.custom_param_type_group.setObjectName(u"custom_param_type_group")
            sizePolicy5 = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            sizePolicy5.setHorizontalStretch(0)
            sizePolicy5.setVerticalStretch(0)
            sizePolicy5.setHeightForWidth(self.custom_param_type_group.sizePolicy().hasHeightForWidth())
            self.custom_param_type_group.setSizePolicy(sizePolicy5)
            self.custom_param_type_group.setMinimumSize(QtCore.QSize(0, 50))
            self.custom_param_type_group.setMaximumSize(QtCore.QSize(16777215, 50))
            self.custom_param_type_group.setStyleSheet(u"QGroupBox {\n"
                                                       "    border: 1px solid rgb(207, 207, 207);\n"
                                                       "    border-radius: 3px;\n"
                                                       "}")
            self.horizontalLayout = QtWidgets.QHBoxLayout(self.custom_param_type_group)
            self.horizontalLayout.setObjectName(u"horizontalLayout")
            self.not_growth_rb = QtWidgets.QRadioButton(self.custom_param_type_group)
            """кнопка нет прироста(свой показатель)"""
            self.not_growth_rb.setObjectName(u"not_growth_rb")

            self.horizontalLayout.addWidget(self.not_growth_rb)

            self.year_growth_rb = QtWidgets.QRadioButton(self.custom_param_type_group)
            """кнопка прирост год к году(свой показатель)"""
            self.year_growth_rb.setObjectName(u"year_growth_rb")

            self.horizontalLayout.addWidget(self.year_growth_rb)

            self.quater_growth_rb = QtWidgets.QRadioButton(self.custom_param_type_group)
            """кнопка прирост квартал к кварталу(свой показатель)"""
            self.quater_growth_rb.setObjectName(u"quater_growth_rb")

            self.horizontalLayout.addWidget(self.quater_growth_rb)

            self.verticalLayout_3.addWidget(self.custom_param_type_group)
            self.label_full_input = QtWidgets.QTextEdit(self.groupBox)
            """Label введенное пользователем выражение показателя(свой показатель)"""
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.label_full_input.sizePolicy().hasHeightForWidth())
            self.label_full_input.setSizePolicy(sizePolicy)
            self.label_full_input.setMinimumSize(QtCore.QSize(0, 80))
            self.label_full_input.setStyleSheet("QTextEdit{\n"
                                                "    background-color:rgb(220, 220, 220)\n"
                                                "}")
            self.label_full_input.setText("")
            self.label_full_input.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
            self.label_full_input.setObjectName("label_full_input")
            self.verticalLayout_3.addWidget(self.label_full_input)

            #
            self.hints_label = QtWidgets.QTextEdit(self.groupBox)
            """(TextEdit)расшифровки номеров пунктов в формуле(свой показатель)"""
            self.hints_label.setReadOnly(True)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.hints_label.sizePolicy().hasHeightForWidth())
            self.hints_label.setSizePolicy(sizePolicy)
            self.hints_label.setMinimumSize(QtCore.QSize(70, 80))
            self.hints_label.setStyleSheet("QTextEdit {\n"
                                           "    border: 1px solid rgb(207, 207, 207);\n"
                                           "    border-radius: 3px;\n"
                                           "}")
            # запись заголовка с использованием html, <h4> - заголовок4
            self.hints_label.setHtml("<h4>Имена пунктов формулы показателя</h4>\n")
            self.hints_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.hints_label.setObjectName("hints_label")
            self.verticalLayout_3.addWidget(self.hints_label)
            #

            self.gridLayout.addWidget(self.groupBox, 0, 0, 3, 2)
            self.point_group = QtWidgets.QGroupBox(self.custom_group)
            """(GroupBox)кнопки выбора пунктов и функции для формулы(свой показатель)"""
            self.point_group.setMinimumSize(QtCore.QSize(500, 0))
            self.point_group.setMaximumSize(QtCore.QSize(16777215, 500))
            self.point_group.setStyleSheet("QGroupBox{\n"
                                           "    border: none;\n"
                                           "}")
            self.point_group.setTitle("")
            self.point_group.setObjectName("point_group")

            self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.point_group)
            self.verticalLayout_5.setObjectName("verticalLayout_5")
            self.point_func_group = QtWidgets.QGroupBox(self.point_group)
            """(GroupBox)кнопки выбора функции для пункта(свой показатель)"""
            # self.point_func_group.setMinimumSize(QtCore.QSize(0, 170))
            self.point_func_group.setStyleSheet("QGroupBox {\n"
                                                "    border: 1px solid rgb(207, 207, 207);\n"
                                                "    border-radius: 3px;\n"
                                                "       /* padding: 1px 18px 1px 3px;\n"
                                                "    min-width: 6em;*/\n"
                                                "}")
            self.point_func_group.setObjectName("point_func_group")
            self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.point_func_group)
            self.horizontalLayout_4.setObjectName("horizontalLayout_4")
            self.no_func_rb = QtWidgets.QRadioButton(self.point_func_group)
            """кнопка нет_функции(свой показатель)"""
            self.no_func_rb.setLayoutDirection(QtCore.Qt.LeftToRight)
            self.no_func_rb.setObjectName("no_func_rb")
            self.horizontalLayout_4.addWidget(self.no_func_rb)
            self.average_rb = QtWidgets.QRadioButton(self.point_func_group)
            """кнопка функции среднего_по_дате(свой показатель)"""
            self.average_rb.setObjectName("average_rb")
            self.horizontalLayout_4.addWidget(self.average_rb)
            self.average_companies_rb = QtWidgets.QRadioButton(self.point_func_group)
            """кнопка функции среднего_по_ЛК(свой показатель)"""
            self.average_companies_rb.setObjectName("average_companies_rb")
            self.horizontalLayout_4.addWidget(self.average_companies_rb)
            self.sliding_year_rb = QtWidgets.QRadioButton(self.point_func_group)
            """кнопка функции скользящий год(свой показатель)"""
            self.sliding_year_rb.setObjectName("sliding_year_rb")
            self.horizontalLayout_4.addWidget(self.sliding_year_rb)
            self.diff_rb = QtWidgets.QRadioButton(self.point_func_group)
            """кнопка функции изменение за год(свой показатель)"""
            self.diff_rb.setObjectName("diff_rb")
            self.horizontalLayout_4.addWidget(self.diff_rb)
            self.q_diff_rb = QtWidgets.QRadioButton(self.point_func_group)
            """кнопка функции изменение за квартал(свой показатель)"""
            self.q_diff_rb.setObjectName("q_diff_rb")
            self.horizontalLayout_4.addWidget(self.q_diff_rb)
            self.verticalLayout_5.addWidget(self.point_func_group)

            self.point_num_group = QtWidgets.QGroupBox(self.point_group)
            """(GroupBox)группа с выбором номера пункта(свой показатель)"""
            self.point_num_group.setStyleSheet("QGroupBox {\n"
                                               "    border: 1px solid rgb(207, 207, 207);\n"
                                               "    border-radius: 3px;\n"
                                               "}")
            self.point_num_group.setObjectName("point_num_group")
            self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.point_num_group)
            self.verticalLayout_7.setObjectName("verticalLayout_7")
            self.point_name_comb = ExtendedComboBox(self.point_num_group)
            """(ExtendedComboBox)список пунктов анкет с функцией поиска(свой показатель)"""
            self.point_name_comb.setMinimumSize(QtCore.QSize(0, 0))
            self.point_name_comb.setObjectName("point_name_comb")
            self.verticalLayout_7.addWidget(self.point_name_comb)
            self.verticalLayout_5.addWidget(self.point_num_group)
            self.btns_group = QtWidgets.QGroupBox(self.point_group)
            self.verticalLayout_5.addWidget(self.btns_group)
            self.btns_group.setObjectName("btns_group")
            self.verticalLayout_6 = QtWidgets.QHBoxLayout(self.btns_group)
            self.verticalLayout_6.setObjectName("verticalLayout_6")
            self.pushButton = QtWidgets.QPushButton(self.btns_group)
            """кнопка добавить пункт и функцию в формулу(свой показатель)"""
            self.pushButton.setMinimumSize(QtCore.QSize(350, 50))
            self.pushButton.setMaximumSize(QtCore.QSize(450, 16777215))
            self.pushButton.setObjectName(u"pushButton")
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
            self.pushButton.setSizePolicy(sizePolicy)

            self.verticalLayout_6.addWidget(self.pushButton)

            self.pb_equals = QtWidgets.QPushButton(self.btns_group)
            """калькулятор кнопка = (свой показатель)"""
            self.pb_equals.setObjectName(u"pb_equals")
            self.pb_equals.setMinimumSize(QtCore.QSize(350, 50))
            self.pb_equals.setMaximumSize(QtCore.QSize(450, 16777215))
            self.pb_equals.setSizePolicy(sizePolicy)
            sizePolicy.setHeightForWidth(self.pb_equals.sizePolicy().hasHeightForWidth())
            self.pb_equals.setStyleSheet(u"QPushButton {\n"
                                         "	font-weight: 600;\n"
                                         "	background-color:rgb(221, 221, 221);\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton:hover {\n"
                                         "	background-color: rgb(194, 194, 194);\n"
                                         "}\n"
                                         "\n"
                                         "QPushButton:pressed {\n"
                                         "	background-color: rgb(232, 232, 232);\n"
                                         "}\n"
                                         "")

            self.verticalLayout_6.addWidget(self.pb_equals)
            self.verticalLayout_6.setAlignment(self.pb_equals, QtCore.Qt.AlignRight)
            self.gridLayout.addWidget(self.point_group, 5, 1, 2, 1)
            self.gridLayout_12.addWidget(self.custom_group, 0, 0, 1, 1)
            self.tabWidget.addTab(self.tab_custom_param, "")

            self.gridLayout_3.addWidget(self.tabWidget, 0, 0, 1, 1)
            self.tabWidget.setCurrentIndex(0)
            self.tabWidget.setTabVisible(1, False)
            self.tabWidget.setTabVisible(2, False)

            self.tab_data_func = QtWidgets.QWidget()
            """вкладка обработки данных ЛК"""
            self.tab_data_func.setObjectName("tab_data_func")
            self.vericalLayout = QtWidgets.QVBoxLayout(self.tab_data_func)
            self.vericalLayout.setObjectName("vericalLayout")
            self.data_btns_group = QtWidgets.QGroupBox(self.tab_data_func)
            self.vericalLayout.setAlignment(QtCore.Qt.AlignCenter)
            self.data_btns_group.setMinimumSize(200, 200)
            self.data_btns_group.setMaximumSize(300, 300)
            self.vericalLayout.addWidget(self.data_btns_group)
            self.vLayout = QtWidgets.QVBoxLayout(self.data_btns_group)
            self.data_btns_group.setLayout(self.vLayout)
            self.validate_pb = QtWidgets.QPushButton(self.data_btns_group)
            self.validate_pb.setMaximumSize(180, 180)
            self.vLayout.addWidget(self.validate_pb)
            self.collect_data_pb = QtWidgets.QPushButton(self.data_btns_group)
            self.collect_data_pb.setMaximumSize(180, 180)
            self.vLayout.addWidget(self.collect_data_pb)
            self.tabWidget.addTab(self.tab_data_func, "")

            self.collect_data_pb.clicked.connect(self.get_file_data)
            self.form_report_pb.clicked.connect(self.form_rep_func)
            self.export_excel.clicked.connect(self.export_func)
            self.build_graphs_rb.clicked.connect(self.build_graphs)
            self.validate_rb.clicked.connect(self.call_valid)
            self.retranslateUi(MainWindow)
            QtCore.QMetaObject.connectSlotsByName(MainWindow)

            # ----------------------------------------------------------
            # дефолтно выбранные кнопки
            self.rep_ecind_rb.setChecked(True)
            self.comparable_lk_rb.setChecked(True)
            self.type_cb_rb.setChecked(True)
            self.param_msfo_rb.setChecked(True)
            self.premade_param_rb.setChecked(True)
            self.point_comb.addItems(desire_parameter_2)
            self.ola_comb.setEnabled(False)
            self.product_comb.setEnabled(False)
            self.not_growth_rb.setChecked(True)
            self.no_func_rb.setChecked(True)
            self.date12.setChecked(True)
            self.desire_dates = [dates_list[-1]]
            self.sliding_check.setEnabled(False)
            self.label_full_input.setText('0')

            #добавление кнопок в ButtonGroupдля быстрого определения, какая отмечена
            # tab_main

            self.report_type_group = QtWidgets.QButtonGroup()
            """(ButtonGroup)группа кнопок типа отчета(главная вкладка)"""
            self.report_type_group.addButton(self.rep_ecind_rb)
            self.report_type_group.addButton(self.rep_datmanage_rb)
            self.report_type_group.addButton(self.rep_fsbu_rb)
            self.report_type_group.addButton(self.rep_msfo_rb)

            self.comp_type_group = QtWidgets.QButtonGroup()
            """(ButtonGroup)группа кнопок типа выборки ЛК(главная вкладка)"""
            self.comp_type_group.addButton(self.comparable_lk_rb)
            self.comp_type_group.addButton(self.cust_comparable_lk_rb)
            self.comp_type_group.addButton(self.all_lk_rb)
            self.comp_type_group.addButton(self.users_lk_rb)

            # выбор классификации типа собственности
            self.classprop_type_group = QtWidgets.QButtonGroup()
            """(ButtonGroup)группа кнопок типа классификации(главная вкладка)"""
            self.classprop_type_group.addButton(self.type_cb_rb)
            self.classprop_type_group.addButton(self.type_ola_rb)

            # МСФО/ФСБУ
            self.msfo_fsbu_group = QtWidgets.QButtonGroup()
            """(ButtonGroup)группа кнопок выбора параметр МСФО/ФСБУ(главная вкладка)"""
            self.msfo_fsbu_group.addButton(self.param_msfo_rb)
            self.msfo_fsbu_group.addButton(self.param_fsbu_rb)

            # запись последних дат экселя в чекбоксы
            self.date1.setText(dates_list[-12])
            self.date2.setText(dates_list[-11])
            self.date3.setText(dates_list[-10])
            self.date4.setText(dates_list[-9])
            self.date5.setText(dates_list[-8])
            self.date6.setText(dates_list[-7])
            self.date7.setText(dates_list[-6])
            self.date8.setText(dates_list[-5])
            self.date9.setText(dates_list[-4])
            self.date10.setText(dates_list[-3])
            self.date11.setText(dates_list[-2])
            self.date12.setText(dates_list[-1])

            self.cb_comb.addItems(desire_type_lk)
            self.ola_comb.addItems(desire_lk_type2)
            self.product_comb.addItems(desire_product)
            self.ola_comb.setCurrentIndex(4)
            self.cb_comb.setCurrentIndex(3)

            # соединение с функцией добавления/удаления даты
            # self.date1.stateChanged.connect(self.dates_state)
            # self.date2.stateChanged.connect(self.dates_state)
            # self.date3.stateChanged.connect(self.dates_state)
            # self.date4.stateChanged.connect(self.dates_state)
            # self.date5.stateChanged.connect(self.dates_state)
            # self.date6.stateChanged.connect(self.dates_state)
            # self.date7.stateChanged.connect(self.dates_state)
            # self.date8.stateChanged.connect(self.dates_state)
            # self.date9.stateChanged.connect(self.dates_state)
            # self.date10.stateChanged.connect(self.dates_state)
            # self.date11.stateChanged.connect(self.dates_state)
            # self.date12.stateChanged.connect(self.dates_state)


            # соединения с кнопками при помощи определения метода лямбда функцией
            # set_ability - доступность пользователю кнопки
            # set_check - установка галочки(отметки кнопки)
            # set_ind - ставит индекс в комбобксе(выбирает, какую строку поставить)
            # set_param - меняет список параметров, кот. виден пользователю
            # set_tab_vis - регулирует видимость вкладок окна
            self.param_fsbu_rb.pressed.connect(lambda: self.set_param(*[[self.point_comb, desire_parameter_2_fsbu]]))
            self.param_msfo_rb.pressed.connect(lambda: self.set_param(*[[self.point_comb, desire_parameter_2]]))

            self.product_comb.currentIndexChanged.connect(
                lambda: self.set_param(*[[self.point_comb, desire_parameter[self.product_comb.currentText()]]]))

            # rep_ecind_rb
            self.rep_ecind_rb.pressed.connect(lambda: self.set_ability(*[[self.sliding_check, False],
                                                                         [self.product_comb, False],
                                                                         [self.param_msfo_rb, True],
                                                                         [self.param_fsbu_rb, True]]))
            self.rep_ecind_rb.pressed.connect(lambda: self.set_check(*[[self.sliding_check, False],
                                                                       [self.param_msfo_rb, True]]))
            self.rep_ecind_rb.pressed.connect(lambda: self.set_ind(*[[self.product_comb, 2]]))
            self.rep_ecind_rb.pressed.connect(lambda: self.set_param(*[[self.point_comb, desire_parameter_2]]))

            # rep_datmanage_rb
            self.rep_datmanage_rb.pressed.connect(lambda: self.set_ability(*[[self.sliding_check, True],
                                                                             [self.product_comb, True],
                                                                             [self.param_msfo_rb, True],
                                                                             [self.param_fsbu_rb, False]]))
            self.rep_datmanage_rb.pressed.connect(lambda: self.set_check(*[[self.param_msfo_rb, True]]))
            self.rep_datmanage_rb.pressed.connect(lambda: self.set_ind(*[[self.product_comb, 2]]))
            self.rep_datmanage_rb.pressed.connect(
                lambda: self.set_param(*[[self.point_comb, desire_parameter[self.product_comb.currentText()]]]))

            # rep_msfo_rb
            self.rep_msfo_rb.pressed.connect(lambda: self.set_ability(*[[self.sliding_check, True],
                                                                        [self.product_comb, False],
                                                                        [self.param_msfo_rb, False],
                                                                        [self.param_fsbu_rb, False]]))
            self.rep_msfo_rb.pressed.connect(lambda: self.set_check(*[[self.param_msfo_rb, False],
                                                                      [self.param_fsbu_rb, False]]))
            self.rep_msfo_rb.pressed.connect(lambda: self.set_ind(*[[self.product_comb, 2]]))
            self.rep_msfo_rb.pressed.connect(
                lambda: self.set_param(*[[self.point_comb, desire_parameter_msfo_points]]))

            # rep_fsbu_rb
            self.rep_fsbu_rb.pressed.connect(lambda: self.set_ability(*[[self.sliding_check, True],
                                                                        [self.product_comb, False],
                                                                        [self.param_msfo_rb, False],
                                                                        [self.param_fsbu_rb, False]]))
            self.rep_fsbu_rb.pressed.connect(lambda: self.set_check(*[[self.param_msfo_rb, False],
                                                                      [self.param_fsbu_rb, False]]))
            self.rep_fsbu_rb.pressed.connect(lambda: self.set_ind(*[[self.product_comb, 2]]))
            self.rep_fsbu_rb.pressed.connect(
                lambda: self.set_param(*[[self.point_comb, desire_parameter_fsbu_points]]))

            # comparable_lk_rb

            self.comparable_lk_rb.pressed.connect(lambda: self.set_ability(*[[self.not_gtlk_check, True]]))
            self.comparable_lk_rb.pressed.connect(
                lambda: self.set_ind(*[[self.ola_comb, 4], [self.cb_comb, 3]]))
            self.comparable_lk_rb.pressed.connect(lambda: self.set_vis(*[[self.lk_type_group, True]]))
            self.comparable_lk_rb.pressed.connect(lambda: self.set_tab_vis(*[[1, False]]))

            # cust_comparable_lk_rb

            self.cust_comparable_lk_rb.clicked.connect(lambda: self.set_ability(*[[self.not_gtlk_check, True]]))
            self.cust_comparable_lk_rb.clicked.connect(
                lambda: self.set_ind(*[[self.ola_comb, 4], [self.cb_comb, 3]]))
            self.cust_comparable_lk_rb.clicked.connect(lambda: self.set_vis(*[[self.lk_type_group, True]]))
            self.cust_comparable_lk_rb.clicked.connect(lambda: self.set_tab_vis(*[[1, False]]))
            self.cust_comparable_lk_rb.clicked.connect(self.cust_comp_func)

            # all_lk_rb
            self.all_lk_rb.pressed.connect(lambda: self.set_ability(*[[self.not_gtlk_check, True]]))
            self.all_lk_rb.pressed.connect(
                lambda: self.set_ind(*[[self.ola_comb, 4], [self.cb_comb, 3]]))
            self.all_lk_rb.pressed.connect(lambda: self.set_vis(*[[self.lk_type_group, True]]))
            self.all_lk_rb.pressed.connect(lambda: self.set_tab_vis(*[[1, False]]))

            # users_lk_rb
            self.users_lk_rb.pressed.connect(lambda: self.set_ability(*[[self.not_gtlk_check, False]]))
            self.users_lk_rb.pressed.connect(
                lambda: self.set_ind(*[[self.ola_comb, 4], [self.cb_comb, 3]]))
            self.users_lk_rb.pressed.connect(lambda: self.set_vis(*[[self.lk_type_group, False]]))
            self.users_lk_rb.pressed.connect(lambda: self.set_tab_vis(*[[1, True]]))
            self.users_lk_rb.pressed.connect(lambda: self.set_check(*[[self.not_gtlk_check, False]]))

            # type_cb_rb
            self.type_cb_rb.pressed.connect(lambda: self.set_ability(*[[self.ola_comb, False],
                                                                       [self.cb_comb, True]]))
            self.type_cb_rb.pressed.connect(lambda: self.set_ind(*[[self.ola_comb, 4]]))

            # type_ola_rb
            self.type_ola_rb.pressed.connect(lambda: self.set_ability(*[[self.cb_comb, False],
                                                                        [self.ola_comb, True]]))
            self.type_ola_rb.pressed.connect(lambda: self.set_ind(*[[self.cb_comb, 3]]))

            # custom_param_rb
            self.label_full_input.textChanged.connect(self.f_check_hints)
            # добавляем кнопки выбора типа пользовательского параметра QButtonGroup,
            self.custom_type_group = QtWidgets.QButtonGroup()
            """(ButtonGroup)группа кнопок типа прироста(свой показатель)"""
            self.custom_type_group.addButton(self.not_growth_rb)
            self.custom_type_group.addButton(self.quater_growth_rb)
            self.custom_type_group.addButton(self.year_growth_rb)

            self.custom_param_rb.pressed.connect(lambda: self.set_ability(*[[self.param_fsbu_rb, False],
                                                                            [self.param_msfo_rb, False],
                                                                            [self.sliding_check, False],
                                                                            [self.product_comb, False],
                                                                            [self.point_comb, False],
                                                                            [self.rep_ecind_rb, False],
                                                                            [self.rep_datmanage_rb, False],
                                                                            [self.rep_msfo_rb, False],
                                                                            [self.rep_fsbu_rb, False]]))

            self.custom_param_rb.pressed.connect(lambda: self.set_check(*[[self.param_fsbu_rb, False],
                                                                          [self.param_msfo_rb, False],
                                                                          [self.sliding_check, False],
                                                                          [self.rep_ecind_rb, False],
                                                                          [self.rep_datmanage_rb, False],
                                                                          [self.rep_msfo_rb, False],
                                                                          [self.rep_fsbu_rb, False]]))
            self.custom_param_rb.pressed.connect(lambda: self.set_tab_vis(*[[2, True]]))

            # premade_param_rb
            self.premade_param_rb.pressed.connect(lambda: self.set_ability(*[[self.param_fsbu_rb, True],
                                                                             [self.param_msfo_rb, True],
                                                                             [self.sliding_check, True],
                                                                             [self.product_comb, False],
                                                                             [self.point_comb, True],
                                                                             [self.rep_ecind_rb, True],
                                                                             [self.rep_datmanage_rb, True],
                                                                             [self.rep_msfo_rb, True],
                                                                             [self.rep_fsbu_rb, True]]))

            self.premade_param_rb.pressed.connect(lambda: self.set_check(*[[self.rep_ecind_rb, True],
                                                                           [self.param_msfo_rb, True]]))
            self.premade_param_rb.pressed.connect(lambda: self.set_tab_vis(*[[2, False]]))
            self.premade_param_rb.pressed.connect(lambda: self.set_param(*[[self.point_comb, desire_parameter_2]]))

            self.calc_pb.pressed.connect(self.choose_calc)
            # ----------------------------------------------------------
            # tab_user_choice
            self.avcomp_list.setSortingEnabled(True)
            self.chosen_list.setSortingEnabled(True)
            #создаем список имен без кавычек и сокращений типа ООО
            sorted_names=[]
            for name in lk_names_list:
                tmp=name
                # убираем кавычки, если есть
                tmp=' '.join(re.findall("[а-яА-Я]+",tmp))
                l=tmp.split()
                #убираем приставку, если есть
                if l[0] in ('ООО','АО',"ЗАО","ГК","ОАО","ЛК"):
                    l.pop(0)
                tmp=' '.join(l)
                sorted_names.append(tmp)
            lk_names_list2=list(lk_names_list)
            for i in range(len(lk_names_list2)):
                it=QtWidgets.QListWidgetItem()
                it.setText(sorted_names[i])
                it.setData(QtCore.Qt.UserRole,lk_names_list2[i])
                self.avcomp_list.addItem(it)
            #self.avcomp_list.insertItems(0, lk_names_list)
            # при нажатии кнопки переноса в список выбранных лк из возможных
            # используется функция move_lk
            self.to_chosen_pb.clicked.connect(
                lambda: self.move_lk(self.avcomp_list.selectedItems(), self.chosen_list, self.avcomp_list))
            self.to_available_pb.clicked.connect(
                lambda: self.move_lk(self.chosen_list.selectedItems(), self.avcomp_list, self.chosen_list))

            # ----------------------------------------------------------
            # tab_custom_param
            # записываем в список имена пунктов из словаря
            self.list_point_names = list([str(i)+f' ({str(key)})' for key,i in dict_num_name.items()])
            print(list([str(i)+f' ({str(key)})' for key,i in dict_num_name.items()]))
            self.point_name_comb.addItems(self.list_point_names)
            self.point_name_comb.setCurrentIndex(-1)
            # добавляем подсказки на каждый пункт, кот. показывают полное имя пункта
            # для этого идем по каждой строке комбобокса
            for i in range(len(self.list_point_names)):
                # на iый элемент комбобокса записываем имя на i-ом месте из списка имен
                self.point_name_comb.setItemData(i, self.list_point_names[i], QtCore.Qt.ToolTipRole)

            self.func_group = QtWidgets.QButtonGroup()
            """(ButtonGroup)группа кнопок типа функции для пункта(свой показатель)"""
            self.func_group.addButton(self.no_func_rb)
            self.func_group.addButton(self.average_rb)
            self.func_group.addButton(self.average_companies_rb)
            self.func_group.addButton(self.diff_rb)
            self.func_group.addButton(self.q_diff_rb)
            self.func_group.addButton(self.sliding_year_rb)

            self.pb_0.clicked.connect(self.add_value)
            self.pb_1.clicked.connect(self.add_value)
            self.pb_2.clicked.connect(self.add_value)
            self.pb_3.clicked.connect(self.add_value)
            self.pb_4.clicked.connect(self.add_value)
            self.pb_5.clicked.connect(self.add_value)
            self.pb_6.clicked.connect(self.add_value)
            self.pb_7.clicked.connect(self.add_value)
            self.pb_8.clicked.connect(self.add_value)
            self.pb_9.clicked.connect(self.add_value)
            self.pb_bracket_open.clicked.connect(self.add_bracket_op)
            self.pb_bracket_close.clicked.connect(self.add_bracket_close)
            self.pb_point.clicked.connect(self.add_point)
            self.pb_clear.clicked.connect(self.clear_all)
            self.pb_clear_entry.clicked.connect(self.clear_entry)
            # кнопки операторов +*-/
            self.pb_add.clicked.connect(self.add_oper)
            self.pb_div.clicked.connect(self.add_oper)
            self.pb_multiply.clicked.connect(self.add_oper)
            self.pb_subtract.clicked.connect(self.add_oper)
            # кнопка расчета
            self.pb_equals.clicked.connect(self.choose_calc)
            # кнопка добавить пункт и функцию
            self.pushButton.clicked.connect(self.add_funcpoint)
            # список имен пунктов, кот. уже выведены в описание формулы
            self.hinted_pointnums= {}
            """словарь с указанными именами пунктов с расшифровками в подсказках(свой показатель)"""
            # словарь ЛК для экспорта excel
            self.dict_lk_excel = {}
            """словарь Лк с типами для экспорта в эксель"""
            self.concrete_lk_answ_excel={}
            """словарь результатов для каждого ЛК выборки в эксель"""
            #координаты графиков в окне
            self.placement_x = 0
            """расположение по горизонтали очередного графика из базового набора в окне"""
            self.placement_y = 0
            """расположение по вертикали очередного графика из базового набора в окне"""
            self.comp_btns_list=[]
            """список с указателями на кнопки удаления в окне настройки сопоставимой выборки"""
            self.comp_items_list=['(5.1)',]
            """список с пунктами настройки сопоставимой выборки"""

        def retranslateUi(self, MainWindow):
            _translate = QtCore.QCoreApplication.translate
            MainWindow.setWindowTitle(_translate("MainWindow", "Leasing_indicators_panel"))
            self.rep_type.setTitle(_translate("MainWindow", "Тип отчета"))
            self.rep_ecind_rb.setText(_translate("MainWindow", "Экономические индикаторы"))
            self.rep_datmanage_rb.setText(_translate("MainWindow", "Управленческие данные"))
            self.rep_msfo_rb.setText(_translate("MainWindow", "Данные МСФО"))
            self.rep_fsbu_rb.setText(_translate("MainWindow", "Данные ФСБУ"))
            self.answ_box.setTitle(_translate("MainWindow", "Результат"))
            self.lk_attribute_group.setTitle(_translate("MainWindow", "Признак выборки"))
            self.comparable_lk_rb.setText(_translate("MainWindow", "Сопоставимая выборка"))
            self.cust_comparable_lk_rb.setText(_translate("MainWindow", "Настраиваемая сопоставимая выборка"))
            self.comparable_hint_lbl.setText(_translate("MainWindow", "Условие сопоставимости:<br><b>7</b> дат подряд наличие ненулевых данных в пункте <b>5.1</b>"))
            self.all_lk_rb.setText(_translate("MainWindow", "Все лизинговые компании"))
            self.not_gtlk_check.setText(_translate("MainWindow", "Исключить АО ГТЛК"))
            self.users_lk_rb.setText(_translate("MainWindow", "Ручной выбор"))
            self.form_report_pb.setText(_translate("MainWindow", "Отчет по компании"))
            self.lk_type_group.setTitle(_translate("MainWindow", "Классификотор типа собственности"))
            self.type_cb_rb.setText(_translate("MainWindow", "Классификатор ЦБ"))
            self.type_ola_rb.setText(_translate("MainWindow", "Классификатор ОЛА"))
            self.dates_group.setTitle(_translate("MainWindow", "Даты "))
            self.param_group.setTitle(_translate("MainWindow", "Параметры показателя"))
            self.param_msfo_rb.setText(_translate("MainWindow", "По данным МСФО"))
            self.param_fsbu_rb.setText(_translate("MainWindow", "По данным ФСБУ"))
            self.sliding_check.setText(_translate("MainWindow", "Скользящий год"))
            self.prod_label.setText(_translate("MainWindow", "Продукт"))
            self.premade_param_rb.setText(_translate("MainWindow", "Готовый показатель"))
            self.custom_param_rb.setText(_translate("MainWindow", "Свой показатель"))
            self.validate_rb.setText(_translate("MainWindow", "Валидация"))
            self.export_excel.setText(_translate("MainWindow", "Экспорт в Excel"))
            self.calc_pb.setText(_translate("MainWindow", "Рассчитать"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_main), _translate("MainWindow", "Расчет"))
            self.avcomp_group.setTitle(_translate("MainWindow", "Доступные компании"))
            self.to_chosen_pb.setText(_translate("MainWindow", ">>>>>>>>"))
            self.to_available_pb.setText(_translate("MainWindow", "<<<<<<<<"))
            self.chosen_group.setTitle(_translate("MainWindow", "Выбранные компании"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_user_choice),
                                      _translate("MainWindow", "Ручной выбор"))
            self.pb_add.setText(_translate("MainWindow", "+"))
            self.pb_add.setShortcut(_translate("MainWindow", "+"))
            self.pb_3.setText(_translate("MainWindow", "3"))
            self.pb_3.setShortcut(_translate("MainWindow", "3"))
            self.pb_subtract.setText(_translate("MainWindow", "-"))
            self.pb_subtract.setShortcut(_translate("MainWindow", "-"))
            self.pb_9.setText(_translate("MainWindow", "9"))
            self.pb_9.setShortcut(_translate("MainWindow", "9"))
            self.pb_clear_entry.setText(_translate("MainWindow", "CE"))
            self.pb_clear_entry.setShortcut(_translate("MainWindow", "Backspace"))
            self.pb_8.setText(_translate("MainWindow", "8"))
            self.pb_8.setShortcut(_translate("MainWindow", "8"))
            self.pb_7.setText(_translate("MainWindow", "7"))
            self.pb_7.setShortcut(_translate("MainWindow", "7"))
            self.pb_clear.setText(_translate("MainWindow", "C"))
            self.pb_0.setText(_translate("MainWindow", "0"))
            self.pb_0.setShortcut(_translate("MainWindow", "0"))
            self.pb_equals.setText(_translate("MainWindow", "Рассчитать"))
            self.pb_equals.setShortcut(_translate("MainWindow", "="))
            self.pb_point.setText(_translate("MainWindow", "."))
            self.pb_point.setShortcut(_translate("MainWindow", "."))
            self.pb_bracket_open.setText(_translate("MainWindow", "("))
            self.pb_bracket_open.setShortcut(_translate("MainWindow", "("))
            self.pb_bracket_close.setText(_translate("MainWindow", ")"))
            self.pb_bracket_close.setShortcut(_translate("MainWindow", ")"))
            self.pb_multiply.setText(_translate("MainWindow", "*"))
            self.pb_multiply.setShortcut(_translate("MainWindow", "*"))
            self.pb_2.setText(_translate("MainWindow", "2"))
            self.pb_2.setShortcut(_translate("MainWindow", "2"))
            self.pb_4.setText(_translate("MainWindow", "4"))
            self.pb_4.setShortcut(_translate("MainWindow", "4"))
            self.pb_div.setText(_translate("MainWindow", "/"))
            self.pb_div.setShortcut(_translate("MainWindow", "/"))
            self.pb_1.setText(_translate("MainWindow", "1"))
            self.pb_1.setShortcut(_translate("MainWindow", "1"))
            self.pb_6.setText(_translate("MainWindow", "6"))
            self.pb_6.setShortcut(_translate("MainWindow", "6"))
            self.pb_5.setText(_translate("MainWindow", "5"))
            self.pb_5.setShortcut(_translate("MainWindow", "5"))
            self.custom_param_type_group.setTitle(_translate("MainWindow", "Тип показателя"))
            self.quater_growth_rb.setText(_translate("MainWindow", "Прирост квартал-к-кварталу"))
            self.year_growth_rb.setText(_translate("MainWindow", "Прирост год-к-году"))
            self.not_growth_rb.setText(_translate("MainWindow", "Не прирост"))
            self.point_func_group.setTitle(_translate("MainWindow", "Функция"))
            self.no_func_rb.setText(_translate("MainWindow", "без_функции"))
            self.average_rb.setText(_translate("MainWindow", "среднее_за_год"))
            self.average_companies_rb.setText(_translate("MainWindow", "среднее_по_ЛК"))
            self.sliding_year_rb.setText(_translate("MainWindow", "скользящий_год"))
            self.diff_rb.setText(_translate("MainWindow", "изменение_за_год"))
            self.q_diff_rb.setText(_translate("MainWindow", "изменение_за_квартал"))
            self.point_num_group.setTitle(_translate("MainWindow", "Пункт номер"))
            self.pushButton.setText(_translate("MainWindow", "Добавить пункт и функцию"))
            # self.line_edit_cur_input.setText(_translate("MainWindow", "0"))
            self.build_graphs_rb.setText(_translate("MainWindow", "Построить графики"))
            self.validate_pb.setText(_translate("MainWindow","Провести валидацию данных"))
            self.collect_data_pb.setText(_translate("MainWindow","Записать новые данные из анкет"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_custom_param),
                                      _translate("MainWindow", "Свой показатель"))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_data_func),
                                      _translate('MainWindow',"Обработка данных excel"))


        def func_rep_header(self, wb,ws, name):
            """
            функция записи шапки листа excel: имя лк и таблица с цветовыми обозначениями
            :param wb: файл excel (workbook)
            :param ws: лист excel (worksheet)
            :param name: str имя лк
            """
            # заголовок
            ws.write(0, 1, f"ОТЧЕТ ПО ЛИЗИНГОВОЙ КОМПАНИИ: {name}")
            # [голубой,фиол,красный,зеленый, желтый]
            color_names = ['#C8E9F4', '#D9C8F4', '#F4D7C8', '#DAF4C8', '#F3E290']
            # запись обозначений цветов
            for num, value in enumerate(['Баланс', 'ОПУ и финансовые результаты', 'Динамика лизингового бизнеса',
                                         'Качество лизингового портфеля', 'Фондирование', ]):
                format1 = wb.add_format()
                """"набор свойств ячейки excel; позволяет менять цвет, шрифт, рамку и тд"""
                format1.set_bg_color(color_names[num])
                if num == 0:
                    format1.set_top()#граница сверху
                format1.set_left()
                format1.set_right()
                ws.write(num + 2, 1, value, format1)#запись ячейки (ряд, столбик, что записываем, стиль ячейки)
            format1.set_bottom()#граница снизу


        def f_write_res(self,towrite):
            """
            заменяет в массиве результатов строки на числа или nan
            :param towrite: list/np.array
            :return: np.array (dtype= np.float64)
            """
            for i in range(len(towrite)):
                if isinstance(towrite[i],str):
                    if towrite[i].replace('.', '0').isnumeric():
                        towrite[i]=float(towrite[i])
                    else:
                        towrite[i]=np.nan
            return np.array(towrite,dtype=np.float64)


        def f_write_table_rep(self,**to_write):
            """

            :param to_write: словарь с параметрами для записи
            **{'wb': файл(workbook) excel,'ws':лист excel,'bg_color': цвет таблицы(str),
            'title': заголовок таблицы(str),'row_names': имена рядов таблицы в нулевом столбце (list of str),
                                                  'dates': даты - столбцы таблицы(list of str),
                                                  'res':массив результатов(np.array),
                                                  'cords': координаты левого верхнего угла таблицы(tuple of int),
                                                  'symb': символы, которые должны быть рядом с результатом в таблице(н-р: %)
                                                  (list of str)}
            """
            format1 = to_write['wb'].add_format()
            format1.set_bg_color(to_write['bg_color'])

            #закрашиваем таблицу
            for i in range(to_write['cords'][0],to_write['cords'][0] + len(to_write['row_names'])+2):#строки
                for j in range(to_write['cords'][1], to_write['cords'][1]+6):#столбцы
                    to_write['ws'].write_blank(i, j, '', format1)
            #даты
            for i,d in enumerate(to_write['dates']):
                to_write['ws'].write(to_write['cords'][0]+1, to_write['cords'][1] + i+1, d,format1)
            # заголовок
            format1.set_align('center')
            to_write['ws'].merge_range(to_write['cords'][0], to_write['cords'][1], to_write['cords'][0],
                                       to_write['cords'][1] + 5, to_write['title'], format1)
            #построчно записываем результаты
            for i,name in enumerate(to_write['row_names']):
                format1 = to_write['wb'].add_format()
                format1.set_bg_color(to_write['bg_color'])
                to_write['ws'].write(to_write['cords'][0]+2+i,to_write['cords'][1], name, format1)
                for j in range(5):
                    format1 = to_write['wb'].add_format()
                    format1.set_bg_color(to_write['bg_color'])
                    format1.set_border(7)#пунктирные границы таблиц
                    s=''
                    if 'symb' in to_write:
                        s=to_write['symb'][i]
                    if isinstance(to_write['res'][i][j],str):
                        if 'недостаточно данных' in to_write['res'][i][j]:
                            to_write['ws'].write(to_write['cords'][0] + 2 + i, to_write['cords'][1] + j + 1,
                                                 'недостаточно данных', format1)
                        elif 'nan' in to_write['res'][i][j]:
                            to_write['ws'].write(to_write['cords'][0] + 2 + i, to_write['cords'][1] + j + 1,
                                                 'недостаточно данных', format1)
                        elif len(s)>0:#если результат нужно написать с символом
                            format1.set_num_format('0.00##\%;[Red](0.00##\%)')#форматирование с проуентом
                            to_write['ws'].write(to_write['cords'][0] + 2 + i, to_write['cords'][1] + j + 1,
                                                 round(float(to_write['res'][i][j]), 4), format1)
                        else:
                            to_write['ws'].write(to_write['cords'][0] + 2 + i, to_write['cords'][1] + j + 1,
                                                 round(float(to_write['res'][i][j]), 2), format1)
                    elif np.isnan(to_write['res'][i][j]) or np.isinf(to_write['res'][i][j]):
                        to_write['ws'].write(to_write['cords'][0]+2+i, to_write['cords'][1]+j+1, 'недостаточно данных',format1)
                    elif len(s)>0:
                        format1.set_num_format('0.00##\%;[Red](0.00##\%)')
                        to_write['ws'].write(to_write['cords'][0]+2+i, to_write['cords'][1]+j+1, round(to_write['res'][i][j],4),format1)
                    else:
                        to_write['ws'].write(to_write['cords'][0] + 2 + i, to_write['cords'][1] + j + 1,
                                             round(to_write['res'][i][j], 2), format1)
        

        def f_nan_to_txt(self,res):
            """
            заменяем в списке результатов nan результаты на пояснение - недостаточно данных
            :param res: np.array
            :return: list
            """
            for i,rr in enumerate(res):
                res[i]=['недостаточно данных' if x is np.nan else x for x in res]
            return res
                

        def f_calc_perc(self, res, dat,rep_type, num,rep_type2, denom, lkn):
            """
            функция вычисления процентного соотношения значения
            :param res: список результатов, куда будет добавлено вычисление функции(np.array/list)
            :param dat: даты для вычисления(list of str)
            :param rep_type: имя типа отчета числителя - эк.индикаторы/упр.данные(str)
            :param num: имя параметра, который будет в числителе вычисления процента
            [('параметр', 'по данным мсфо/фсбу'), True/false(скользящий год)]
            :param rep_type2: имя типа отчета знаменателя
            :param denom: имя параметра в знаменателе вычисления процента
            :param lkn: имя ЛК (list of str)
            """
            tmpres=self.f_write_res(calculate(**{'desire_dates_choice': dat,
                                             'desire_report_type': rep_type,
                                             'desire_comparable': 'Ручной выбор',
                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                             'is_not_gtlk': False,
                                             'desire_type_lk': 'все ЛК',
                                             'desire_param': num,
                                             'selection_names_list': [lkn, ],
                                             'is_custom': False
                                             })[1]) * 100 / self.f_write_res(
                calculate(**{'desire_dates_choice': dat,
                             'desire_report_type': rep_type2,
                             'desire_comparable': 'Ручной выбор',
                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                             'is_not_gtlk': False,
                             'desire_type_lk': 'все ЛК',
                             'desire_param': denom,
                             'selection_names_list': [lkn, ],
                             'is_custom': False
                             })[1])
            res.append(tmpres)


        def f_weighted_av(self, **to_calc):
            """
            функция вычисления взвешенного среднего (за вес берутся значения лизингового портфеля)
            :param to_calc: словарь для вычислений
            **{'dates': даты (list of str),'param':[('ROE', по данным мсфо/фсбу), False(скользящий год)]}
            :return: list [результат для сопоставимой выборки (list), результат для всех ЛК(list)]
            """
            
            lk_list=[]
            for d in to_calc['dates']:#записываем сопоставимые выборки на даты вычислений
                lk_list.append(date_lk51[d])
            comp_res=[]
            """результат вычисления средних взвешенных сопоставимых выборок на все указанные даты"""
            #вычисляем взвешенное среднее для сопоставимых выборок
            for i,d in enumerate(to_calc['dates']):#идем в цикле по каждой дате
                s=0 #сумма в числителе
                s_d=0 #сумма в знаменателе
                flag=False #true - если во время вычисления сумм сало недостаточно данных
                j=0
                while not flag and j<len(lk_list[i]):
                    #вычисляем по каждому лк пока или не дойдем до конца выборки, или не окажется недостаточно данных
                    l=lk_list[i][j]#имя лк
                    #параметр
                    a=calculate(**{'desire_dates_choice': [d,],
                                             'desire_report_type': 'Экономические индикаторы',
                                             'desire_comparable': 'Ручной выбор',
                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                             'is_not_gtlk': False,
                                             'desire_type_lk': 'все ЛК',
                                             'desire_param': to_calc['param'],
                                             'selection_names_list': [l, ],
                                             'is_custom': False
                                             })[1][0]
                    if to_calc['param'][0][0] == 'ROE':
                        if isinstance(a, str):
                            if " (Чистая прибыль отрицательная.)" in a:
                                a = a.replace(" (Чистая прибыль отрицательная.)", "")
                                a = a.replace(" ", "")
                            elif " (Капитал отрицательный.)" in a:
                                a = "0"
                            elif " (Чистая прибыль и капитал отрицательны.)" in a:
                                a = "0"
                            else:
                                a = "0"
                        

                    #вес параметра
                    b=calculate(**{'desire_dates_choice': [d,],
                                             'desire_report_type': 'Экономические индикаторы',
                                             'desire_comparable': 'Ручной выбор',
                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                             'is_not_gtlk': False,
                                             'desire_type_lk': 'все ЛК',
                                             'desire_param': [('лизинговый портфель', 'все продукты'), False],
                                             'selection_names_list': [l, ],
                                             'is_custom': False
                                             })[1][0]
                    
                    
                    if isinstance(a,str):#если в результате вычислений была получена строка
                        #проверяем, что эта строка не указание на недостаточность данных
                        if 'недостаточно данных' in a:
                            a = 0
                    elif isinstance(b,str):
                        if 'недостаточно данных' in b:
                            b = 0
                    else:
                        a=float(a)
                        b=float(b)
                        s += a * b
                        s_d += b
                    j+=1 #сдвигаем счетчик лк
                
                comp_res.append(s/s_d)
            #вычисляем взвешенное среднее для всех лк
            # для всех лк список на каждуб дату одинаков, поэтому вычисляем сразу все пять дат без цикла по ним
            all_res=[]
            """результат вычисления средних взвешенных всех лк на все указанные даты"""
            s=np.zeros(5)
            s_d=np.zeros(5)
            flag=False
            i=0
            lkn=lk_names_list.to_list() #список всех лк
            while not flag and i<len(lkn):# цикл по ЛК
                l=lkn[i]
                a = np.array(calculate(**{'desire_dates_choice': to_calc['dates'],
                                 'desire_report_type': 'Экономические индикаторы',
                                 'desire_comparable': 'Ручной выбор',
                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                 'is_not_gtlk': False,
                                 'desire_type_lk': 'все ЛК',
                                 'desire_param': to_calc['param'],
                                 'selection_names_list': [l, ],
                                 'is_custom': False
                                 })[1])
                
                b = np.array(calculate(**{'desire_dates_choice': to_calc['dates'],
                                 'desire_report_type': 'Экономические индикаторы',
                                 'desire_comparable': 'Ручной выбор',
                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                 'is_not_gtlk': False,
                                 'desire_type_lk': 'все ЛК',
                                 'desire_param': [('лизинговый портфель', 'все продукты'), False],
                                 'selection_names_list': [l, ],
                                 'is_custom': False
                                 })[1])
                
                if to_calc['param'][0][0] == 'ROE':
                    a=graph_roe(list(a))
                else:
                    a = list(a)
                b=list(b)
                
                for j in range(len(a)):
                    if a[j] == 'недостаточно данных' or b[j] == 'недостаточно данных':
                        s[j]+=0
                    else:
                        s[j]+=float(a[j])*float(b[j])
                    if b[j] == 'недостаточно данных':
                        s_d[j]+=0
                    else:
                        s_d[j]+=float(b[j])
                i+=1
            for i in range(len(s)):
                if isinstance(s[i],str) or isinstance(s_d[i], str):
                    all_res.append('недостаточно данных')
                else:
                    all_res.append(s[i]/s_d[i])

            return [comp_res, all_res]


        def form_rep_func(self):
            """функция формирования отчета по ЛК"""
            if not self.chosen_list.count() == 1:  # проверка, чтов ручном выборе только одна ЛК
                # выдаем сообщение для пользователя о необходимости выбора одного ЛК
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Для формирования отчета необходимо выбрать ОДНУ компанию на вкладке 'Ручной выбор'")
                msg.setWindowTitle("Error")
                msg.exec_()
            else:  # если проверка пройдена, то можно формировать отчет
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Пожалуйста подождите, идёт формироание отчёта.")
                msg.setWindowTitle("Information")
                msg.setStandardButtons(QMessageBox.NoButton)
                msg.show()

                QApplication.processEvents()

                full_name = self.chosen_list.item(0).data(QtCore.Qt.UserRole)
                """имя ЛК без сокращений"""
                name = self.chosen_list.item(0).text()
                """сокращенное имя ЛК"""
                report_dates = dates_list[-7:-1]
                report_dates.append(dates_list[-1])
                """7 последних дат, по которым формируется отчет по ЛК"""
                # проверка наличия данных мсфо и фсбу
                msfo_flag = False
                """показатель сдачи данных для мсфо"""
                fsbu_flag = False
                """показатель сдачи данных для фсбу"""
                lk_df = full_df.loc[full_df['lk_name'] == full_name, ['point_number'] + [d for d in dates_list]]
                """дф со всеми датами нужной ЛК для формирования отчета"""
                tmpdf=lk_df.loc[lk_df['point_number'] == '5.1', [d for d in report_dates]]
                for d in report_dates:
                    el = tmpdf[d].to_list()[0]
                    if not np.isnan(el):
                        if not el=='недостаточно данных':
                            if not int(el)==0:
                                msfo_flag = True
                tmpdf = lk_df.loc[lk_df['point_number'] == '4.1', [d for d in report_dates]]
                for d in report_dates:
                    el = tmpdf[d].to_list()[0]
                    if not np.isnan(el):
                        if not el == 'недостаточно данных':
                            if not int(el) == 0:
                                fsbu_flag = True
                if not msfo_flag and not fsbu_flag:#если нет ни мсфо, ни фсбу данных
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(f"Данные по компании ({name}) за указанные периоды отсутствуют")
                    msg.setWindowTitle("Error")
                    msg.exec_()
                else:# есть данные для записи
                    new_time = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")#время для названия файла
                    fname = f'{name}_{new_time}.xlsx'#имя файла
                    if msfo_flag:
                        list_name='МСФО'
                        categ='По данным МСФО'
                        categ2='Данные МСФО'
                        full_cords=[(8,1),(8,8), (8,15),(15,15),
                                    (22,1),(22,8),(28,8),(22,15),(28,15),
                                    (34, 1), (34, 8), (34, 15), (40, 1), (40, 8), (40, 15), (46, 1), (46, 8), (46, 15),
                                    (58, 1), (58, 8), (58, 15), (68, 1), (68, 8), (75, 8),
                                    (68, 15), (74, 15)]
                        """список координат таблиц"""
                        fsbu_cords=[(8,1),(8,8),
                                    (22,1),(22,8),(28,8),(22,15),(28,15),
                                    (34,1),(34,8),
                                    (40,1),(40,8), (47,8)]
                    else:
                        list_name='ФСБУ'
                        categ='По данным ФСБУ'
                        categ2='Данные ФСБУ'
                        full_cords=[(8,1),(8,8),
                                    (22,1),(22,8),(28,8),(22,15),(28,15),
                                    (34,1),(34,8),(34,15), (40,1),(40,8),(40,15), (46,1), (46,8), (46, 15),
                                    (58,1), (58,8), (58, 15),(68,1), (68,8),(75,8),
                                    (68, 15),(74, 15)]
                    writer = pd.ExcelWriter(fname, engine="xlsxwriter")
                    wb= writer.book
                    if msfo_flag:
                        ws = wb.add_worksheet(list_name)
                        counter=0
                        #шапка листа
                        self.func_rep_header(wb, ws, full_name)
                        #таблица АКТИВ -------------------------------------
                        res=[]
                        self.f_calc_perc(res, report_dates[2:],'Экономические индикаторы', [('ЧИЛ', categ), False],
                                         'Экономические индикаторы',[('АКТИВЫ', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Оборудование для передачи в лизинг', categ2), False],'Экономические индикаторы',
                                         [('АКТИВЫ', categ2), False],full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Авансовые платежи поставщикам и подрядчикам',categ2), False],'Экономические индикаторы',
                                         [('АКТИВЫ', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:],'Экономические индикаторы',
                                         [('Имущество, переданное в операционную аренду',categ2), False],'Экономические индикаторы',
                                         [('АКТИВЫ', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:],'Экономические индикаторы',
                                         [('Займы выданные',categ2), False],'Экономические индикаторы',
                                         [('АКТИВЫ', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:],'Экономические индикаторы',
                                         [('Дебиторская задолженность по расторгнутым договорам лизинга',categ2), False],
                                         'Экономические индикаторы',[('АКТИВЫ', categ2), False], full_name)
                        s = [100 - (np.array([res[j][i] for j in range(len(res))])).sum() for i in range(5) ]
                        res.append(s)#Прочие активы
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                         'desire_report_type': 'Экономические индикаторы',
                                         'desire_comparable': 'Ручной выбор',
                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                         'is_not_gtlk': False,
                                         'desire_type_lk': 'все ЛК',
                                         'desire_param': [('АКТИВЫ', categ2), False],
                                         'selection_names_list': [full_name, ],
                                         'is_custom': False
                                         })[1]))
                        self.f_write_table_rep(**{'wb':wb,'ws':ws,'bg_color':'#C8E9F4','title':f'АКТИВ {list_name}',
                                                  'row_names':['ЧИЛ','Оборудование для передачи в лизинг',
                                                               'Авансовые платежи поставщикам',
                                                               'Имущество, переданное в операционную аренду','Займы выданные',
                                                               'ДЗ по расторгнутым договорам', 'Прочие активы', 'АКТИВЫ ВСЕГО'],
                                                  'dates':report_dates[2:],'res':res,'cords':full_cords[counter],
                                                  'symb':['%','%','%','%','%','%','%','']})
                        counter+=1
                        #таблица ПАССИВ -------------------------------------
                        res=[]
                        self.f_calc_perc(res, report_dates[2:],'Экономические индикаторы', [('КАПИТАЛ', categ2), False],
                                         'Экономические индикаторы',[('АКТИВЫ', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Нераспределенная прибыль', categ2), False],'Экономические индикаторы',
                                         [('АКТИВЫ', categ2), False],full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Кредиты полученные',categ2), False],'Экономические индикаторы',
                                         [('АКТИВЫ', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:],'Экономические индикаторы',
                                         [('Займы полученные',categ2), False],'Экономические индикаторы',
                                         [('АКТИВЫ', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:],'Экономические индикаторы',
                                         [('Выпущенные долговые ценные бумаги',categ2), False],'Экономические индикаторы',
                                         [('АКТИВЫ', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:],'Экономические индикаторы',
                                         [('Авансы от лизингополучателей',categ2), False],
                                         'Экономические индикаторы',[('АКТИВЫ', categ2), False], full_name)
                        s = [100 - (np.array([res[j][i] for j in range(len(res))])).sum() for i in range(5) ]
                        res.append(s)#Прочие обязательства
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                         'desire_report_type': 'Экономические индикаторы',
                                         'desire_comparable': 'Ручной выбор',
                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                         'is_not_gtlk': False,
                                         'desire_type_lk': 'все ЛК',
                                         'desire_param': [('АКТИВЫ', categ2), False],
                                         'selection_names_list': [full_name, ],
                                         'is_custom': False
                                         })[1]))
                        self.f_write_table_rep(**{'wb':wb,'ws':ws,'bg_color':'#C8E9F4','title':f'ПАССИВ {list_name}',
                                                  'row_names':['КАПИТАЛ ВСЕГО','Нераспределенная прибыль',
                                                               'Кредиты','Займы','Облигации',
                                                               'Авансы от лизингополучателей', 'Прочие обязательства', 'ПАССИВЫ ВСЕГО'],
                                                  'dates':report_dates[2:],'res':res,'cords':full_cords[counter],
                                                  'symb':['%','%','%','%','%','%','%','']})
                        counter+=1
                        # таблицы только для МСФО:
                        # таблица Валютная структура баланса -------------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Валютные требования', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Валютные обязательства', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('ОВП', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('доля ОВП в капитале', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(**{'wb': wb, 'ws': ws, 'bg_color': '#C8E9F4', 'title': f'Валютная структура баланса {list_name}',
                                                  'row_names': ['Валютные требования', 'Валютные обязательства',
                                                                'Чистая валютная позиция (ЧВП)', 'Отношение ЧВП/КАПИТАЛ',],
                                                  'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter],
                                                  })
                        counter+=1
                        # таблица Структура внебаланса-------------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Внебалансовые требования (Всего)', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('в т.ч. валютные требования', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Внебалансовые обязательства (Всего)', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('в т.ч. валютные обязательства', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#C8E9F4', 'title': 'Структура внебаланса',
                               'row_names': ['Внебалансовые требования (Всего)', 'в т.ч. валютные требования',
                                             'Внебалансовые обязательства (Всего)', 'в т.ч. валютные обязательства', ],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter],
                               })
                        counter+=1
                        #фиолетовые таблицы
                        #ОПУ (за квартал)----------------------------------
                        res=[]
                        tmp=categ if msfo_flag else categ2
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Выручка', tmp), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Процентные расходы', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Изменение резервов по договорам финансового лизинга', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Изменение резервов по договорам операционной аренды', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Изменение резервов по прочим видам активов', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Административные и операционные расходы', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Прочие доходы', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Прочие расходы', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Чистая прибыль (убыток)', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'ОПУ {list_name} (за квартал)',
                               'row_names': ['Выручка', 'Процентные расходы','Изменение резервов по финлизингу',
                                             'Изменение резервов по операренде', 'Изменение прочих резервов',
                                             'Административные и операционные расходы', 'Прочие доходы','Прочие расходы',
                                             'Чистая прибыль (убыток)'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter],})
                        counter+=1

                        #ROE ----------------------------------
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('ROE', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt=self.f_weighted_av(**{'dates': report_dates[2:],'param':[('ROE', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])

                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'ROE ({list_name})',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter],})
                        counter+=1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 23, 9, 23, 13],
                            'values': ['МСФО', 24, 9, 24, 13],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'}, 'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['МСФО', 23, 9, 23, 13],
                            'values': ['МСФО', 25, 9, 25, 13],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'}, 'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['МСФО', 23, 9, 23, 13],
                            'values': ['МСФО', 26, 9, 26, 13],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'ROE', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(137, 1, chart_line)
                        chart_line.set_x_axis({'crosses': 'between'})
                        # Leverage ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Leverage', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt = self.f_weighted_av(**{'dates': report_dates[2:], 'param': [('Leverage', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'Leverage ({list_name})',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 29, 9, 29, 13],
                            'values': ['МСФО', 30, 9, 30, 13],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'}, 'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['МСФО', 29, 9, 29, 13],
                            'values': ['МСФО', 31, 9, 31, 13],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'}, 'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['МСФО', 29, 9, 29, 13],
                            'values': ['МСФО', 32, 9, 32, 13],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'Финансовый рычаг', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(137, 8, chart_line)
                        # CIR ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('CIR', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt = self.f_weighted_av(**{'dates': report_dates[2:], 'param': [('CIR', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'CIR ({list_name})',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 23, 16, 23, 20],
                            'values': ['МСФО', 24, 16, 24, 20],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'}, 'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['МСФО', 23, 16, 23, 20],
                            'values': ['МСФО', 25, 16, 25, 20],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'}, 'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['МСФО', 23, 16, 23, 20],
                            'values': ['МСФО', 26, 16, 26, 20],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'CIR', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(137, 15, chart_line)
                        # Процентный спрэд ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('процентный спрэд', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt = self.f_weighted_av(**{'dates': report_dates[2:], 'param': [('процентный спрэд', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'Процентный спрэд ({list_name})',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 29, 16, 29, 20],
                            'values': ['МСФО', 30, 16, 30, 20],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'}, 'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['МСФО', 29, 16, 29, 20],
                            'values': ['МСФО', 31, 16, 31, 20],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'}, 'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['МСФО', 29, 16, 29, 20],
                            'values': ['МСФО', 32, 16, 32, 20],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'Процентный спрэд', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(155, 1, chart_line)
                        #красные таблицы
                        # НБ (фин.лизинг), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('новый бизнес', 'финансовый лизинг'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'финансовый лизинг'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'финансовый лизинг'), False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'НБ (фин.лизинг), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Новый бизнес (фин.лизинг)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 35, 2, 35, 6],
                            'values': ['МСФО', 36, 2, 36, 6],
                            'fill': {'color': '#B9BCBD'},
                        })
                        #'#F9AF1B'
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['МСФО', 35, 2, 35, 6],
                            'values': ['МСФО', 37, 2, 37, 6],
                            'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'}, 'border':{'color':'#F9AF1B'},'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['МСФО', 35, 2, 35, 6],
                            'values': ['МСФО', 38, 2, 38, 6],
                            'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},'border':{'color': '#1BB9F9'}, 'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title({'name': 'Новый бизнес (фин.лизинг)','name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(80, 1, chart_col)
                        # НБ (опер.лизинг), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('новый бизнес', 'операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'операционная аренда'), False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'НБ (опер.лизинг), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Новый бизнес (опер.аренда)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 35, 9, 35, 13],
                            'values': ['МСФО', 36, 9, 36, 13],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['МСФО', 35, 9, 35, 13],
                            'values': ['МСФО', 37, 9, 37, 13],
                            'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},'border':{'color': '#F9AF1B'}, 'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['МСФО', 35, 9, 35, 13],
                            'values': ['МСФО', 38, 9, 38, 13],
                            'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border':{'color': '#1BB9F9'},'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title({'name': 'Новый бизнес (опер.аренда)','name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(80, 8, chart_col)
                        # НБ (все продукты), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('новый бизнес', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'все продукты'), False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'НБ (все продукты), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        #график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Новый бизнес (все продукты)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 35, 16, 35, 20],
                            'values': ['МСФО', 36, 16, 36, 20],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['МСФО', 35, 16, 35, 20],
                            'values': ['МСФО', 37, 16, 37, 20],
                             'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle','fill': {'color':'#F9AF1B'},'border':{'color': '#F9AF1B'}, 'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['МСФО', 35, 16, 35, 20],
                            'values': ['МСФО', 38, 16, 38, 20],
                             'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle','fill': {'color':'#1BB9F9'},'border':{'color': '#1BB9F9'}, 'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title({'name': 'Новый бизнес (все продукты)','name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(80,15, chart_col)
                        # Лизинговый портфель (фин.лизинг), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('лизинговый портфель', 'финансовый лизинг'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста лизингового портфеля (год к году)', 'финансовый лизинг'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста лизингового портфеля (год к году)', 'финансовый лизинг'), False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'Лизинговый портфель (фин.лизинг), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Портфель (фин.лизинг)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 41, 2, 41, 6],
                            'values': ['МСФО', 42, 2, 42, 6],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['МСФО', 41, 2, 41, 6],
                            'values': ['МСФО', 43, 2, 43, 6],
                            'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},'border':{'color': '#F9AF1B'}, 'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['МСФО', 41, 2, 41, 6],
                            'values': ['МСФО', 44, 2, 44, 6],
                            'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},'border':{'color': '#1BB9F9'}, 'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title({'name': 'Портфель (фин.лизинг)','name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(95, 1, chart_col)
                        # Лизинговый портфель (опер.лизинг), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('лизинговый портфель', 'операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста лизингового портфеля (год к году)', 'операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста лизингового портфеля (год к году)', 'операционная аренда'), False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'Лизинговый портфель (опер.лизинг), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Портфель (опер.аренда)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 41, 9, 41, 13],
                            'values': ['МСФО', 42, 9, 42, 13],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['МСФО', 41, 9, 41, 43],
                            'values': ['МСФО', 43, 9, 43, 13],
                            'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},'border':{'color': '#F9AF1B'}, 'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['МСФО', 41, 9, 41, 43],
                            'values': ['МСФО', 44, 9, 44, 13],
                            'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},'border':{'color': '#1BB9F9'}, 'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title({'name': 'Портфель (опер.аренда)','name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(95, 8, chart_col)
                        # Лизинговый портфель (все продукты), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('лизинговый портфель', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста лизингового портфеля (год к году)', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста лизингового портфеля (год к году)', 'все продукты'), False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'Лизинговый портфель (все продукты), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Портфель (все продукты)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 41, 16, 41, 20],
                            'values': ['МСФО', 42, 16, 42, 20],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['МСФО', 41, 16, 41, 20],
                            'values': ['МСФО', 43, 16, 43, 20],
                            'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},'border':{'color': '#F9AF1B'}, 'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['МСФО', 41, 16, 41, 20],
                            'values': ['МСФО', 44, 16, 44, 20],
                            'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border':{'color': '#1BB9F9'},'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title({'name': 'Портфель (все продукты)','name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(95, 15, chart_col)
                        #Структура лизингового портфеля (фин.лизинг)
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('сегменты: легковые автомобили', 'финансовый лизинг'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: грузовые автомобили', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: ж/д', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: авиа', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: спецтехника', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: недвижимость', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: c/x', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('сегменты: суда', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: прочее', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'Структура лизингового портфеля (фин.лизинг)',
                               'row_names': ['Леговые автомобили','Грузовые автомобили','Ж/д техника','Авиа',
                                             'Спецтехника','Недвижимость','С/х техника','Суда','Прочее',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        #Структура лизингового портфеля (фин.лизинг)
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('сегменты: легковые автомобили', 'операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: грузовые автомобили', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: ж/д', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: авиа', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: спецтехника', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: недвижимость', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: c/x', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: суда', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: прочее', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'Структура лизингового портфеля (опер.лизинг)',
                               'row_names': ['Леговые автомобили','Грузовые автомобили','Ж/д техника','Авиа',
                                             'Спецтехника','Недвижимость','С/х техника','Суда','Прочее',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        #Структура лизингового портфеля (фин.лизинг)
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('сегменты: легковые автомобили', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: грузовые автомобили', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: ж/д', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: авиа', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: спецтехника', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: недвижимость', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: c/x', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: суда', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: прочее', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'Структура лизингового портфеля (все продукты)',
                               'row_names': ['Леговые автомобили','Грузовые автомобили','Ж/д техника','Авиа',
                                             'Спецтехника','Недвижимость','С/х техника','Суда','Прочее',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1

                        # график
                        chart_pie = wb.add_chart({'type': 'pie'})
                        chart_pie.add_series({
                            #'name': f'Легковые автомобили',
                            'categories': ['МСФО', 48, 8, 56, 8],
                            'values': ['МСФО', 48, 20, 56, 20],
                            #'fill': {'color': '#B9BCBD'},
                            'points': [
                                {'fill': {'color': '#5CD4FA'}},
                                {'fill': {'color': '#F3AD31'}},
                                {'fill': {'color': '#D0D0D0'}},
                                {'fill': {'color': 'yellow'}},
                                {'fill': {'color': '#3650F1'}},
                                {'fill': {'color': 'green'}},
                                {'fill': {'color': '#021AAD'}},
                                {'fill': {'color': 'brown'}},
                            ],
                            'data_labels': {'percentage':True, 'position': 'outside_end'},
                        })

                        chart_pie.set_size({'width': 700, 'height': 500})
                        chart_pie.set_title(
                            {'name': f'Структура портфеля (все продукты на последнюю дату) {name}', 'name_font': {'bold': False, 'size': 14}})
                        
                        ws.insert_chart(187, 15, chart_pie)

                        #зеленые таблички
                        #ПА (фин.лизинг)
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('расторжения', 'финансовый лизинг'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('реструктуризации', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие NPL90+ всеми резервами', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля NPL90+ в портфеле', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля NPL90+ в портфеле', 'финансовый лизинг'),
                                                             False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля проблемных активов', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля проблемных активов', 'финансовый лизинг'),
                                                             False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8', 'title': f'ПА (фин.лизинг)',
                               'row_names': [f'Расторгнутые договоры {name}',f'Обслуживаемая реструктуризация {name}',
                                             f'NPL90+ {name}',f'доля NPL90+ {name}, %',
                                             f'доля NPL90+ по сопоставимой выборке, %',f'доля проблемной задолженности в ЛП {name}, %',
                                             f'доля проблемной задолженности в ЛП по сопоставимой выборке, %',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        #график
                        chart_col=wb.add_chart({'type': 'column', 'subtype': 'stacked'})
                        chart_col.add_series({
                            'name': f'NPL90+ {name}',
                            'categories': ['МСФО', 59, 2, 59, 6],
                            'values': ['МСФО', 62, 2, 62, 6],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Обслуживаемая реструктуризация {name}',
                            'categories': ['МСФО', 59, 2, 59, 6],
                            'values': ['МСФО', 61, 2, 61, 6],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Расторгнутые договоры {name}',
                            'categories': ['МСФО', 59, 2, 59, 6],
                            'values': ['МСФО', 60, 2, 60, 6],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        #желтый
                        chart_line.add_series({
                            'name': f'доля NPL90+ {name}, %',
                            'categories': ['МСФО', 59, 2, 59, 6],
                            'values': ['МСФО', 63, 2, 63, 6],
                            'line': {'color': '#EFDD42'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EFDD42'},'border':{'color': '#EFDD42'}, 'size': 5},
                        })
                        #синий
                        chart_line.add_series({
                            'name': f'доля NPL90+ по сопоставимой выборке, %',
                            'categories': ['МСФО', 59, 2, 59, 6],
                            'values': ['МСФО', 64, 2, 64, 6],
                            'line': {'color': '#6988F1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#6988F1'},'border':{'color': '#6988F1'}, 'size': 5},
                        })
                        #зеленый
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по {name}, %',
                            'categories': ['МСФО', 59, 2, 59, 6],
                            'values': ['МСФО', 65, 2, 65, 6],
                            'line': {'color': '#7EC673'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#7EC673'},'border':{'color': '#7EC673'}, 'size': 5},
                        })
                        #темно-синий
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по сопоставимой выборке, %',
                            'categories': ['МСФО', 59, 2, 59, 6],
                            'values': ['МСФО', 66, 2, 66, 6],
                            'line': {'color': '#1D46D1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1D46D1'},'border':{'color': '#1D46D1'}, 'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 500})
                        chart_col.set_title(
                            {'name': 'Проблемные активы (фин.лизинг)', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(112, 1, chart_col)
                        #ПА (опер.лизинг)
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('расторжения', 'операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('реструктуризации', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие NPL90+ всеми резервами', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля NPL90+ в портфеле', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля NPL90+ в портфеле', 'операционная аренда'),
                                                             False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля проблемных активов', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля проблемных активов', 'операционная аренда'),
                                                             False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8', 'title': f'ПА (опер.лизинг)',
                               'row_names': [f'Расторгнутые договоры {name}',f'Обслуживаемая реструктуризация {name}',
                                             f'NPL90+ {name}',f'доля NPL90+ {name}, %',
                                             f'доля NPL90+ по сопоставимой выборке, %',f'доля проблемной задолженности в ЛП {name}, %',
                                             f'доля проблемной задолженности в ЛП по сопоставимой выборке, %',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'subtype': 'stacked'})
                        chart_col.add_series({
                            'name': f'NPL90+ {name}',
                            'categories': ['МСФО', 59, 9, 59, 13],
                            'values': ['МСФО', 60, 9, 60, 13],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Обслуживаемая реструктуризация {name}',
                            'categories': ['МСФО', 59, 9, 59, 13],
                            'values': ['МСФО', 61, 9, 61, 13],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Расторгнутые договоры {name}',
                            'categories': ['МСФО', 59, 9, 59, 13],
                            'values': ['МСФО', 62, 9, 62, 13],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        # желтый
                        chart_line.add_series({
                            'name': f'доля NPL90+ {name}, %',
                            'categories': ['МСФО', 59, 9, 59, 13],
                            'values': ['МСФО', 63, 9, 63, 13],
                            'line': {'color': '#EFDD42'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EFDD42'}, 'border': {'color': '#EFDD42'},
                                       'size': 5},
                        })
                        # синий
                        chart_line.add_series({
                            'name': f'доля NPL90+ по сопоставимой выборке, %',
                            'categories': ['МСФО', 59, 9, 59, 13],
                            'values': ['МСФО', 64, 9, 64, 13],
                            'line': {'color': '#6988F1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#6988F1'}, 'border': {'color': '#6988F1'},
                                       'size': 5},
                        })
                        # зеленый
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по {name}, %',
                            'categories': ['МСФО', 59, 9, 59, 13],
                            'values': ['МСФО', 65, 9, 65, 13],
                            'line': {'color': '#7EC673'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#7EC673'}, 'border': {'color': '#7EC673'},
                                       'size': 5},
                        })
                        # темно-синий
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по сопоставимой выборке, %',
                            'categories': ['МСФО', 59, 9, 59, 13],
                            'values': ['МСФО', 66, 9, 66, 13],
                            'line': {'color': '#1D46D1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1D46D1'}, 'border': {'color': '#1D46D1'},
                                       'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 500})
                        chart_col.set_title(
                            {'name': 'Проблемные активы (опер.лизинг)', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(112, 8, chart_col)
                        #ПА (все продукты)
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('расторжения', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('реструктуризации', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие NPL90+ всеми резервами', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля NPL90+ в портфеле', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля NPL90+ в портфеле', 'все продукты'),
                                                             False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля проблемных активов', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('доля проблемных активов', 'все продукты'),
                                                             False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8', 'title': f'ПА (все продукты)',
                               'row_names': [f'Расторгнутые договоры {name}',f'Обслуживаемая реструктуризация {name}',
                                             f'NPL90+ {name}',f'доля NPL90+ {name}, %',
                                             f'доля NPL90+ по сопоставимой выборке, %',f'доля проблемной задолженности в ЛП {name}, %',
                                             f'доля проблемной задолженности в ЛП по сопоставимой выборке, %',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'subtype': 'stacked'})
                        chart_col.add_series({
                            'name': f'NPL90+ {name}',
                            'categories': ['МСФО', 59, 16, 59, 20],
                            'values': ['МСФО', 60, 16, 60, 20],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Обслуживаемая реструктуризация {name}',
                            'categories': ['МСФО', 59, 16, 59, 20],
                            'values': ['МСФО', 61, 16, 61, 20],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Расторгнутые договоры {name}',
                            'categories': ['МСФО', 59, 16, 59, 20],
                            'values': ['МСФО', 62, 16, 62, 20],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        # желтый
                        chart_line.add_series({
                            'name': f'доля NPL90+ {name}, %',
                            'categories': ['МСФО', 59, 16, 59, 20],
                            'values': ['МСФО', 63, 16, 63, 20],
                            'line': {'color': '#EFDD42'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EFDD42'}, 'border': {'color': '#EFDD42'},
                                       'size': 5},
                        })
                        # синий
                        chart_line.add_series({
                            'name': f'доля NPL90+ по сопоставимой выборке, %',
                            'categories': ['МСФО', 59, 16, 59, 20],
                            'values': ['МСФО', 64, 16, 64, 20],
                            'line': {'color': '#6988F1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#6988F1'}, 'border': {'color': '#6988F1'},
                                       'size': 5},
                        })
                        # зеленый
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по {name}, %',
                            'categories': ['МСФО', 59, 16, 59, 20],
                            'values': ['МСФО', 65, 16, 65, 20],
                            'line': {'color': '#7EC673'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#7EC673'}, 'border': {'color': '#7EC673'},
                                       'size': 5},
                        })
                        # темно-синий
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по сопоставимой выборке, %',
                            'categories': ['МСФО', 59, 16, 59, 20],
                            'values': ['МСФО', 66, 16, 66, 20],
                            'line': {'color': '#1D46D1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1D46D1'}, 'border': {'color': '#1D46D1'},
                                       'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 500})
                        chart_col.set_title(
                            {'name': 'Проблемные активы (все продукты)', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(112, 15, chart_col)
                        #Данные по резервам мсфо
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Резервы по договорам финансового лизинга', 'Данные МСФО'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Резервы по договорам операционной аренды', 'Данные МСФО'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Прочие резервы', 'Данные МСФО'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие NPL90+ всеми резервами', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие проблемных активов всеми резервами', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие NPL90+ всеми резервами', 'все продукты'),
                                                             False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие проблемных активов всеми резервами', 'все продукты'),
                                                             False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8', 'title': f'Данные по резервам МСФО',
                               'row_names': ['Резервы по финлизингу','Резервы по операренде','Прочие резервы',
                                             f'Покрытие NPL90+ всеми резервами {name}',
                                             f'Покрыие проблемных активов всеми резервами {name}',
                                             f'Покрытие NPL90+ всеми резервами(сопоставимая выборка)',
                                             f'Покрытие проблемных активов всеми резервами(сопоставимая выборка)'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1

                        #график
                        chart_col=wb.add_chart({'type': 'column',})
                        chart_col.add_series({
                            'name': f'Резервы по финлизингу',
                            'categories': ['МСФО', 69, 2, 69, 6],
                            'values': ['МСФО', 70, 2, 70, 6],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Резервы по операренде',
                            'categories': ['МСФО', 69, 2, 69, 6],
                            'values': ['МСФО', 71, 2, 71, 6],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Прочие резервы',
                            'categories': ['МСФО', 69, 2, 69, 6],
                            'values': ['МСФО', 72, 2, 72, 6],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        #желтый
                        chart_line.add_series({
                            'name': f'Покрытие NPL90+ всеми резервами {name}, %',
                            'categories': ['МСФО', 69, 2, 69, 6],
                            'values': ['МСФО', 73, 2, 73, 6],
                            'line': {'color': '#EFDD42'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EFDD42'},'border':{'color': '#EFDD42'}, 'size': 5},
                        })
                        #красный
                        chart_line.add_series({
                            'name': f'Покрытие проблемных активов всеми резервами {name}, %',
                            'categories': ['МСФО', 69, 2, 69, 6],
                            'values': ['МСФО', 74, 2, 74, 6],
                            'line': {'color': '#EF4242'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EF4242'},'border':{'color': '#EF4242'}, 'size': 5},
                        })
                        #зеленый
                        chart_line.add_series({
                            'name': f'Покрытие NPL90+ всеми резервами (сопоставимая выборка), %',
                            'categories': ['МСФО', 69, 2, 69, 6],
                            'values': ['МСФО', 75, 2, 75, 6],
                            'line': {'color': '#7EC673'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#7EC673'},'border':{'color': '#7EC673'}, 'size': 5},
                        })
                        # синий
                        chart_line.add_series({
                            'name': f'Покрытие проблемных активов всеми резервами (сопоставимая выборка), %',
                            'categories': ['МСФО', 59, 2, 59, 6],
                            'values': ['МСФО', 76, 2, 76, 6],
                            'line': {'color': '#6988F1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#6988F1'}, 'border': {'color': '#6988F1'},
                                       'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 500})
                        chart_col.set_title(
                            {'name': 'Резервы', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(171, 8, chart_col)

                        #объем изъятых активов по остаточногй и фактической стоимости(за квартал)--------
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Объем изъятых активов по остаточной стоимости', 'По данным МСФО'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Объем изъятых активов по фактической стоимости', 'По данным МСФО'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Активы, предназначенные для продажи по расторгнутым договорам лизинга', 'Данные МСФО'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Активы, предназначенные для продажи по расторгнутым договорам лизинга', 'Данные МСФО'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1])/self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('КАПИТАЛ', 'Данные МСФО'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8',
                               'title': f'Объем изъятых активов по остаточной и фактической стоимости (за квартал)',
                               'row_names': ['Объем изъятых активов по остаточной стоимости',
                                             'Объем изъятых активов по фактической стоимости',
                                             'Активы, предназначенные для продажи по расторгнутым договорам лизинга',
                                             f'Отношение активов для продажи к капиталу',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        #график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Объем изъятых активов по остаточной и фактической стоимости'})
                        chart_col.add_series({
                            'name': f'Объем изъятых активов по остаточной стоимости',
                            'categories': ['МСФО', 69, 9, 69, 13],
                            'values': ['МСФО', 70, 9, 70, 13],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Объем изъятых активов по фактической стоимости',
                            'categories': ['МСФО', 69, 9, 69, 13],
                            'values': ['МСФО', 71, 9, 71, 13],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Активы, предназначенные для продажи по расторгнутым договорам лизинга',
                            'categories': ['МСФО', 69, 9, 69, 13],
                            'values': ['МСФО', 72, 9, 72, 13],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Отношение активов для продажи к капиталу',
                            'categories': ['МСФО', 69, 9, 69, 13],
                            'values': ['МСФО', 73, 9, 73, 13],
                            'line': {'color': '#EFDD42'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EFDD42'}, 'border': {'color': '#EFDD42'},
                                       'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title(
                            {'name': 'Объем изъятых активов по остаточной и фактической стоимости', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(171, 1, chart_col)
                        #Досрочный выкуп и замороженные активы (за квартал)--------
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('объем досрочно выкупленного имущества', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('объем замороженных активов', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8',
                               'title': f'Досрочный выкуп и замороженные активы (за квартал)',
                               'row_names': ['Объем досрочно выкупленного имущества',
                                             'Объем замороженных активов',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1


                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': 'Млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'Объем досрочно выкупленного имущества',
                            'categories': ['МСФО', 76, 9, 76, 13],
                            'values': ['МСФО', 77, 9, 77, 13],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'}, 'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Объем замороженных активов',
                            'categories': ['МСФО', 76, 9, 76, 13],
                            'values': ['МСФО', 78, 9, 78, 13],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'Досрочка и выкупы', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(171, 15, chart_line)

                        #желтые таблицы -----------------------------
                        #Стоимость фондирования МСФО ----------------------------------
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('стоимость фондирования', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt=self.f_weighted_av(**{'dates': report_dates[2:],'param':[('стоимость фондирования', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F3E290', 'title': f'Стоимость фондирования {list_name}',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter],})
                        counter+=1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['МСФО', 69, 16, 69, 20],
                            'values': ['МСФО', 70, 16, 70, 20],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'}, 'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['МСФО', 69, 16, 69, 20],
                            'values': ['МСФО', 71, 16, 71, 20],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'}, 'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['МСФО', 69, 16, 69, 20],
                            'values': ['МСФО', 72, 16, 72, 20],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'Стоимость фондирования', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(155, 8, chart_line)
                        #Структура фондирования (МСФО)
                        res=[]
                        for cc in ("Ручной выбор","Сопоставимая выборка", "Все лизинговые компании"):
                            a=self.f_write_res(calculate(**{'desire_dates_choice': report_dates[5:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': cc,
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('Кредиты полученные', categ2), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1])
                            b=self.f_write_res(calculate(**{'desire_dates_choice': report_dates[5:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': cc,
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('Займы полученные', categ2), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1])
                            c=self.f_write_res(calculate(**{'desire_dates_choice': report_dates[5:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': cc,
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('Выпущенные долговые ценные бумаги', categ2), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1])
                            su=a+b+c
                            res.append(a*100/su)
                            res.append(b*100/su)
                            res.append(c*100/su)
                        tn=f'Структура фондирования ({list_name})'
                        rn=[f'Кредиты', 'Займы', 'Облигации']
                        format1 = wb.add_format()
                        format1.set_bg_color('#F3E290')
                        # закрашиваем таблицу
                        for i in range(full_cords[counter][0],
                                       full_cords[counter][0] + len(rn) + 2):  # строки
                            for j in range(full_cords[counter][1], full_cords[counter][1] + 7):  # столбцы
                                ws.write_blank(i, j, '', format1)
                        ws.merge_range(full_cords[counter][0]+1,full_cords[counter][1]+1,
                                       full_cords[counter][0]+1,full_cords[counter][1]+2, f"{name}",format1)
                        ws.merge_range(full_cords[counter][0] + 1, full_cords[counter][1] + 3,
                                       full_cords[counter][0] + 1, full_cords[counter][1] + 4, f"Сопоставимая выборка",format1)
                        ws.merge_range(full_cords[counter][0] + 1, full_cords[counter][1] + 5,
                                       full_cords[counter][0] + 1, full_cords[counter][1] + 6, f"Все ЛК",format1)
                        # даты
                        for i in range(6):
                            ws.write(full_cords[counter][0]+2,full_cords[counter][1]+i+1,report_dates[5:][int(i%2)], format1)
                        # заголовок
                        format1.set_align('center')
                        ws.merge_range(full_cords[counter][0], full_cords[counter][1], full_cords[counter][0],
                                       full_cords[counter][1] + 5, tn,
                                       format1)
                        # построчно записываем результаты
                        for i, nn in enumerate(rn):
                            format1 = wb.add_format()
                            format1.set_bg_color('#F3E290')
                            ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1], nn, format1)
                            for j in range(6):
                                format1 = wb.add_format()
                                format1.set_bg_color('#F3E290')
                                format1.set_border(7)
                                s = '%'
                                if isinstance(res[i+int(3*(j//2))][int(j%2)], str):
                                    if 'недостаточно данных' in res[i+int(3*(j//2))][int(j%2)]:
                                        ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                                             'недостаточно данных', format1)
                                    else:
                                        format1.set_num_format('0.0##\%;[Red](0.0##\%)')
                                        ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                                             round(float(res[i+int(3*(j//2))][int(j%2)]), 1), format1)
                                elif np.isnan(res[i+int(3*(j//2))][int(j%2)]) or np.isinf(res[i+int(3*(j//2))][int(j%2)]):
                                    ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                                         'недостаточно данных', format1)
                                else:
                                    format1.set_num_format('0.0##\%;[Red](0.0##\%)')
                                    ws.write(full_cords[counter][0] +3 + i, full_cords[counter][1] + j + 1,
                                                         round(res[i+int(3*(j//2))][int(j%2)], 1), format1)
                        #график
                        chart_col = wb.add_chart({'type': 'column', 'subtype': 'percent_stacked'})
                        chart_col.add_series({
                            'name': f'Кредиты',
                            'categories': ['МСФО', 75, 16, 76, 21],
                            'values': ['МСФО', 77, 16, 77, 21],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Займы',
                            'categories': ['МСФО', 75, 16, 76, 21],
                            'values': ['МСФО', 78, 16, 78, 21],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Облигации',
                            'categories': ['МСФО', 75, 16, 76, 21],
                            'values': ['МСФО', 79, 16, 79, 21],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title(
                            {'name': 'Структура фондирования', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(155, 15, chart_col)
                        ws.autofit()
                        
                        #если при наличии мсфо есть фсбу, то записываем страницу с таблицами только фсбу
                        if fsbu_flag:
                            list_name = 'ФСБУ'
                            categ = 'По данным ФСБУ'
                            categ2 = 'Данные ФСБУ'
                            full_cords = [(8, 1), (8, 8), (8, 15), 
                                          (22, 1), (28, 1), (22, 8), (28, 8),
                                          (34, 1), (34, 8),
                                          (31, 15), (18, 15), (24, 15)]
                            ws = wb.add_worksheet(list_name)
                            counter = 0
                            # шапка листа
                            self.func_rep_header(wb, ws, full_name)
                            # таблица АКТИВ -------------------------------------
                            res = []
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы', [('в т.ч. чистые инвестиции в лизинг (по договорам финансового лизинга)', categ2), False],
                                             'Экономические индикаторы', [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Основные средства', categ2), False],
                                             'Экономические индикаторы',
                                             [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Нематериальные активы', categ2), False],
                                             'Экономические индикаторы',
                                             [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('в т.ч. стоимость имущества, переданного в операционную аренду', 'Данные ФСБУ'), False],
                                             'Экономические индикаторы',
                                             [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Займы выданные', categ2), False], 'Экономические индикаторы',
                                             [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Дебиторская задолженность по расторгнутым договорам лизинга', categ2),
                                              False],
                                             'Экономические индикаторы', [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Денежные средства', categ2),
                                              False],
                                             'Экономические индикаторы', [('Активы', categ2), False], full_name)
                            #np.genfromtxt
                            s = [100 - (np.array([res[j][i] for j in range(len(res))])).sum() for i in range(5)]
                            res.append(s)  # Прочие активы
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('Активы', categ2), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#C8E9F4', 'title': f'АКТИВ {list_name}',
                                   'row_names': ['Чистые инвестиции в лизинг', 'Основные средства',
                                                 'Нематериальные активы',
                                                 'Стоимость имущества, переданного в операционную аренду', 'Займы выданные',
                                                 'ДЗ по расторгнутым договорам', 'Денежные средства','Прочие активы', 'АКТИВЫ ВСЕГО'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter],
                                   'symb': ['%', '%', '%', '%', '%', '%', '%', '%', '']})
                            counter += 1
                            # таблица ПАССИВ -------------------------------------
                            res = []
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('ИТОГО КАПИТАЛ', categ2), False],
                                             'Экономические индикаторы', [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Нераспределенная прибыль', categ2), False], 'Экономические индикаторы',
                                             [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Кредиты полученные', categ2), False], 'Экономические индикаторы',
                                             [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Займы полученные', categ2), False], 'Экономические индикаторы',
                                             [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Выпущенные долговые ценные бумаги', categ2), False],
                                             'Экономические индикаторы',
                                             [('Активы', categ2), False], full_name)
                            self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                             [('Дебиторская задолженность по расторгнутым договорам лизинга', categ2), False],
                                             'Экономические индикаторы', [('Активы', categ2), False], full_name)
                            s = [100 - (np.array([res[j][i] for j in range(len(res))])).sum() for i in range(5)]
                            res.append(s)  # Прочие обязательства
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('Активы', categ2), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#C8E9F4', 'title': f'ПАССИВ {list_name}',
                                   'row_names': ['КАПИТАЛ ВСЕГО', 'Нераспределенная прибыль',
                                                 'Кредиты', 'Займы', 'Облигации',
                                                 'Кредиторская задолженность', 'Прочие обязательства',
                                                 'ПАССИВЫ ВСЕГО'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter],
                                   'symb': ['%', '%', '%', '%', '%', '%', '%', '']})
                            counter += 1
                            # фиолетовые таблицы
                            # ОПУ (за квартал)----------------------------------
                            res = []
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('Выручка', categ2), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('Себестоимость продаж', categ2), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [(
                                                                              'Управленческие расходы',
                                                                              categ2), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [(
                                                                              'Проценты к уплате',
                                                                              categ2), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [
                                                                 ('Прибыль (убыток) от продаж', categ2),
                                                                 False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [
                                                                 ('в т.ч. переоценка стоимости имущества, переданного в операционную аренду', categ2),
                                                                 False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'ОПУ {list_name} (за квартал)',
                                   'row_names': ['Выручка', 'Себестоимость продаж', 'Управленческие расходы',
                                                 'Проценты к уплате', 'Чистая прибыль (убыток)',
                                                 'Переоценка стоимости имущества по операренде',],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                            counter += 1

                            # ROE ----------------------------------
                            res = []
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('ROE', categ), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            tt = self.f_weighted_av(**{'dates': report_dates[2:], 'param': [('ROE', categ), False]})
                            res.append(tt[0])
                            res.append(tt[1])

                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'ROE ({list_name})',
                                   'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                                 'Средневзвешенная всех ЛК'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                            counter += 1
                            # график
                            chart_line = wb.add_chart({'type': 'line'})
                            chart_line.set_y_axis({
                                'name': '%',
                                'name_font': {'bold': False}
                            })
                            chart_line.add_series({
                                'name': f'{name}',
                                'categories': ['ФСБУ', 23, 2, 23, 6],
                                'values': ['ФСБУ', 24, 2, 24, 6],
                                'line': {'color': '#B9BCBD'},
                                'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                           'border': {'color': '#B9BCBD'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная сопоставимой выборки',
                                'categories': ['ФСБУ', 23, 2, 23, 6],
                                'values': ['ФСБУ', 25, 2, 25, 6],
                                'line': {'color': '#F9AF1B'},
                                'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                           'border': {'color': '#F9AF1B'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная всех ЛК',
                                'categories': ['ФСБУ', 23, 2, 23, 6],
                                'values': ['ФСБУ', 26, 2, 26, 6],
                                'line': {'color': '#1BB9F9'},
                                'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                           'border': {'color': '#1BB9F9'},
                                           'size': 5},
                            })
                            chart_line.set_size({'width': 700, 'height': 300})
                            chart_line.set_title(
                                {'name': 'ROE', 'name_font': {'bold': False, 'size': 14}})
                            chart_line.set_legend({'position': 'bottom'})
                            chart_line.set_x_axis({'crosses': 'between'})
                            ws.insert_chart(60, 1, chart_line)
                            # Leverage ----------------------------------
                            res = []
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('Leverage', categ), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            tt = self.f_weighted_av(
                                **{'dates': report_dates[2:], 'param': [('Leverage', categ), False]})
                            res.append(tt[0])
                            res.append(tt[1])
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'Leverage ({list_name})',
                                   'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                                 'Средневзвешенная всех ЛК'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                            counter += 1
                            # график
                            chart_line = wb.add_chart({'type': 'line'})
                            chart_line.set_y_axis({
                                'name': '%',
                                'name_font': {'bold': False}
                            })
                            chart_line.add_series({
                                'name': f'{name}',
                                'categories': ['ФСБУ', 29, 2, 29, 6],
                                'values': ['ФСБУ', 30, 2, 30, 6],
                                'line': {'color': '#B9BCBD'},
                                'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                           'border': {'color': '#B9BCBD'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная сопоставимой выборки',
                                'categories': ['ФСБУ', 29, 2, 29, 6],
                                'values': ['ФСБУ', 31, 2, 31, 6],
                                'line': {'color': '#F9AF1B'},
                                'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                           'border': {'color': '#F9AF1B'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная всех ЛК',
                                'categories': ['ФСБУ', 29, 2, 29, 6],
                                'values': ['ФСБУ', 32, 2, 32, 6],
                                'line': {'color': '#1BB9F9'},
                                'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                           'border': {'color': '#1BB9F9'},
                                           'size': 5},
                            })
                            chart_line.set_size({'width': 700, 'height': 300})
                            chart_line.set_title(
                                {'name': 'Финансовый рычаг', 'name_font': {'bold': False, 'size': 14}})
                            chart_line.set_legend({'position': 'bottom'})
                            ws.insert_chart(60, 8, chart_line)
                            # CIR ----------------------------------
                            res = []
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('CIR', categ), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            tt = self.f_weighted_av(**{'dates': report_dates[2:], 'param': [('CIR', categ), False]})
                            res.append(tt[0])
                            res.append(tt[1])
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'CIR ({list_name})',
                                   'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                                 'Средневзвешенная всех ЛК'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                            counter += 1
                            # график
                            chart_line = wb.add_chart({'type': 'line'})
                            chart_line.set_y_axis({
                                'name': '%',
                                'name_font': {'bold': False}
                            })
                            chart_line.add_series({
                                'name': f'{name}',
                                'categories': ['ФСБУ', 23, 9, 23, 13],
                                'values': ['ФСБУ', 24, 9, 24, 13],
                                'line': {'color': '#B9BCBD'},
                                'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                           'border': {'color': '#B9BCBD'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная сопоставимой выборки',
                                'categories': ['ФСБУ', 23, 9, 23, 13],
                                'values': ['ФСБУ', 25, 9, 25, 13],
                                'line': {'color': '#F9AF1B'},
                                'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                           'border': {'color': '#F9AF1B'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная всех ЛК',
                                'categories': ['ФСБУ', 23, 9, 23, 13],
                                'values': ['ФСБУ', 26, 9, 26, 13],
                                'line': {'color': '#1BB9F9'},
                                'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                           'border': {'color': '#1BB9F9'},
                                           'size': 5},
                            })
                            chart_line.set_size({'width': 700, 'height': 300})
                            chart_line.set_title(
                                {'name': 'CIR', 'name_font': {'bold': False, 'size': 14}})
                            chart_line.set_legend({'position': 'bottom'})
                            ws.insert_chart(44, 15, chart_line)
                            # Процентный спрэд ----------------------------------
                            res = []
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('процентный спрэд', categ), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            tt = self.f_weighted_av(
                                **{'dates': report_dates[2:], 'param': [('процентный спрэд', categ), False]})
                            res.append(tt[0])
                            res.append(tt[1])
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4',
                                   'title': f'Процентный спрэд ({list_name})',
                                   'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                                 'Средневзвешенная всех ЛК'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                            counter += 1
                            # график
                            chart_line = wb.add_chart({'type': 'line'})
                            chart_line.set_y_axis({
                                'name': '%',
                                'name_font': {'bold': False}
                            })
                            chart_line.add_series({
                                'name': f'{name}',
                                'categories': ['ФСБУ', 29, 9, 29, 13],
                                'values': ['ФСБУ', 30, 9, 30, 13],
                                'line': {'color': '#B9BCBD'},
                                'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                           'border': {'color': '#B9BCBD'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная сопоставимой выборки',
                                'categories': ['ФСБУ', 29, 9, 29, 13],
                                'values': ['ФСБУ', 31, 9, 31, 13],
                                'line': {'color': '#F9AF1B'},
                                'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                           'border': {'color': '#F9AF1B'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная всех ЛК',
                                'categories': ['ФСБУ', 29, 9, 29, 13],
                                'values': ['ФСБУ', 32, 9, 32, 13],
                                'line': {'color': '#1BB9F9'},
                                'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                           'border': {'color': '#1BB9F9'},
                                           'size': 5},
                            })
                            chart_line.set_size({'width': 700, 'height': 300})
                            chart_line.set_title(
                                {'name': 'Процентный спрэд', 'name_font': {'bold': False, 'size': 14}})
                            chart_line.set_legend({'position': 'bottom'})
                            ws.insert_chart(76, 1, chart_line)
                            # красные таблицы
                            #TODO: пересчитать
                            
                            # Лизинговый портфель (опер.лизинг), скг ----------------------------------
                            res = []
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [
                                                                 ('лизинговый портфель', 'операционная аренда'), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [(
                                                                              'темп прироста лизингового портфеля (год к году)',
                                                                              'операционная аренда'), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Сопоставимая выборка',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [(
                                                                              'темп прироста лизингового портфеля (год к году)',
                                                                              'операционная аренда'), False],
                                                             # 'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8',
                                   'title': f'Лизинговый портфель (опер.лизинг), скг',
                                   'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                                 f'Темп прироста по сопоставимой выборке (г./г.), %'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                            counter += 1
                            # график
                            chart_col = wb.add_chart({'type': 'column', 'name': 'Портфель (опер.аренда)'})
                            chart_col.add_series({
                                'name': f'{name}',
                                'categories': ['ФСБУ', 35, 2, 35, 6],
                                'values': ['ФСБУ', 36, 2, 36, 6],
                                'fill': {'color': '#B9BCBD'},
                            })
                            chart_col.set_y_axis({
                                'name': 'млн руб.',
                                'name_font': {'bold': False}
                            })
                            chart_line = wb.add_chart({'type': 'line'})
                            chart_line.set_y2_axis({
                                'name': '%',
                            })
                            chart_line.add_series({
                                'name': f'Темп прироста по {name} (г./г.), %',
                                'categories': ['ФСБУ', 35, 2, 35, 6],
                                'values': ['ФСБУ', 37, 2, 37, 6],
                                'line': {'color': '#F9AF1B'},
                                'y2_axis': True,
                                'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                           'border': {'color': '#F9AF1B'}, 'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                                'categories': ['ФСБУ', 35, 2, 35, 6],
                                'values': ['ФСБУ', 38, 2, 38, 6],
                                'line': {'color': '#1BB9F9'},
                                'y2_axis': True,
                                'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                           'border': {'color': '#1BB9F9'}, 'size': 5},
                            })
                            chart_col.combine(chart_line)
                            chart_col.set_size({'width': 700, 'height': 300})
                            chart_col.set_title(
                                {'name': 'Портфель (опер.аренда)', 'name_font': {'bold': False, 'size': 14}})
                            chart_col.set_legend({'position': 'bottom'})
                            ws.insert_chart(44, 1, chart_col)
                            # Лизинговый портфель (все продукты), скг ----------------------------------
                            res = []
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('лизинговый портфель', 'все продукты'),
                                                                              False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [(
                                                                              'темп прироста лизингового портфеля (год к году)',
                                                                              'все продукты'), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Сопоставимая выборка',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [(
                                                                              'темп прироста лизингового портфеля (год к году)',
                                                                              'все продукты'), False],
                                                             # 'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8',
                                   'title': f'Лизинговый портфель (все продукты), скг',
                                   'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                                 f'Темп прироста по сопоставимой выборке (г./г.), %'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                            counter += 1
                            # график
                            chart_col = wb.add_chart({'type': 'column', 'name': 'Портфель (все продукты)'})
                            chart_col.add_series({
                                'name': f'{name}',
                                'categories': ['ФСБУ', 35, 9, 35, 13],
                                'values': ['ФСБУ', 36, 9, 36, 13],
                                'fill': {'color': '#B9BCBD'},
                            })
                            chart_col.set_y_axis({
                                'name': 'млн руб.',
                                'name_font': {'bold': False}
                            })
                            chart_line = wb.add_chart({'type': 'line'})
                            chart_line.set_y2_axis({
                                'name': '%',
                            })
                            chart_line.add_series({
                                'name': f'Темп прироста по {name} (г./г.), %',
                                'categories': ['ФСБУ', 35, 9, 35, 13],
                                'values': ['ФСБУ', 37, 9, 37, 13],
                                'line': {'color': '#F9AF1B'},
                                'y2_axis': True,
                                'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                           'border': {'color': '#F9AF1B'}, 'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                                'categories': ['ФСБУ', 35, 9, 35, 13],
                                'values': ['ФСБУ', 38, 9, 38, 13],
                                'line': {'color': '#1BB9F9'},
                                'y2_axis': True,
                                'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                           'border': {'color': '#1BB9F9'}, 'size': 5},
                            })
                            chart_col.combine(chart_line)
                            chart_col.set_size({'width': 700, 'height': 300})
                            chart_col.set_title(
                                {'name': 'Портфель (все продукты)', 'name_font': {'bold': False, 'size': 14}})
                            chart_col.set_legend({'position': 'bottom'})
                            ws.insert_chart(44, 8, chart_col)
                            
                            # зеленые таблички
                            
                            # Данные по резервам
                            res = []
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [(
                                                                              'Резервы по договорам финансового лизинга',
                                                                              'Данные ФСБУ'), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [
                                                                 ('Резервы по договорам операционной аренды',
                                                                  'Данные ФСБУ'),
                                                                 False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [
                                                                 ('Прочие резервы', 'Данные ФСБУ'),
                                                                 False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [
                                                                 ('покрытие NPL90+ всеми резервами', 'все продукты'),
                                                                 False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [
                                                                 ('покрытие проблемных активов всеми резервами',
                                                                  'все продукты'),
                                                                 False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Сопоставимая выборка',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [
                                                                 ('покрытие NPL90+ всеми резервами', 'все продукты'),
                                                                 False],
                                                             # 'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Управленческие данные',
                                                             'desire_comparable': 'Сопоставимая выборка',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [
                                                                 ('покрытие проблемных активов всеми резервами',
                                                                  'все продукты'),
                                                                 False],
                                                             # 'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8', 'title': f'Данные по резервам ФСБУ',
                                   'row_names': ['Резервы по финлизингу', 'Резервы по операренде', 'Прочие резервы',
                                                 f'Покрытие NPL90+ всеми резервами {name}',
                                                 f'Покрытие проблемных активов всеми резервами {name}',
                                                 f'Покрытие NPL90+ всеми резервами(сопоставимая выборка)',
                                                 f'Покрытие проблемных активов всеми резервами(сопоставимая выборка)'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                            counter += 1

                            # график
                            chart_col = wb.add_chart({'type': 'column', })
                            chart_col.add_series({
                                'name': f'Резервы по финлизингу',
                                'categories': ['ФСБУ', 32, 16, 32, 20],
                                'values': ['ФСБУ', 33, 16, 33, 20],
                                'fill': {'color': '#B9BCBD'},
                            })
                            chart_col.add_series({
                                'name': f'Резервы по операренде',
                                'categories': ['ФСБУ', 32, 16, 32, 20],
                                'values': ['ФСБУ', 34, 16, 34, 20],
                                'fill': {'color': '#F9AF1B'},
                            })
                            chart_col.add_series({
                                'name': f'Прочие резервы',
                                'categories': ['ФСБУ', 32, 16, 32, 20],
                                'values': ['ФСБУ', 35, 16, 35, 20],
                                'fill': {'color': '#1BB9F9'},
                            })
                            chart_col.set_y_axis({
                                'name': 'млн руб.',
                                'name_font': {'bold': False}
                            })
                            chart_line = wb.add_chart({'type': 'line'})
                            chart_line.set_y2_axis({
                                'name': '%',
                            })
                            # желтый
                            chart_line.add_series({
                                'name': f'Покрытие NPL90+ всеми резервами {name}, %',
                                'categories': ['ФСБУ', 32, 16, 32, 20],
                                'values': ['ФСБУ', 36, 16, 36, 20],
                                'line': {'color': '#EFDD42'},
                                'y2_axis': True,
                                'marker': {'type': 'circle', 'fill': {'color': '#EFDD42'},
                                           'border': {'color': '#EFDD42'}, 'size': 5},
                            })
                            # красный
                            chart_line.add_series({
                                'name': f'Покрытие проблемных активов всеми резервами {name}, %',
                                'categories': ['ФСБУ', 32, 16, 32, 20],
                                'values': ['ФСБУ', 37, 16, 37, 20],
                                'line': {'color': '#EF4242'},
                                'y2_axis': True,
                                'marker': {'type': 'circle', 'fill': {'color': '#EF4242'},
                                           'border': {'color': '#EF4242'}, 'size': 5},
                            })
                            # зеленый
                            chart_line.add_series({
                                'name': f'Покрытие NPL90+ всеми резервами (сопоставимая выборка), %',
                                'categories': ['ФСБУ', 32, 16, 32, 20],
                                'values': ['ФСБУ', 38, 16, 38, 20],
                                'line': {'color': '#7EC673'},
                                'y2_axis': True,
                                'marker': {'type': 'circle', 'fill': {'color': '#7EC673'},
                                           'border': {'color': '#7EC673'}, 'size': 5},
                            })
                            # синий
                            chart_line.add_series({
                                'name': f'Покрытие проблемных активов всеми резервами (сопоставимая выборка), %',
                                'categories': ['ФСБУ', 32, 16, 32, 20],
                                'values': ['ФСБУ', 39, 16, 39, 20],
                                'line': {'color': '#6988F1'},
                                'y2_axis': True,
                                'marker': {'type': 'circle', 'fill': {'color': '#6988F1'},
                                           'border': {'color': '#6988F1'},
                                           'size': 5},
                            })
                            chart_col.combine(chart_line)
                            chart_col.set_size({'width': 700, 'height': 500})
                            chart_col.set_title(
                                {'name': 'Резервы', 'name_font': {'bold': False, 'size': 14}})
                            chart_col.set_legend({'position': 'bottom'})
                            ws.insert_chart(92, 8, chart_col)
                            # желтые таблицы -----------------------------
                            # Стоимость фондирования  ----------------------------------
                            res = []
                            res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                             'desire_report_type': 'Экономические индикаторы',
                                                             'desire_comparable': 'Ручной выбор',
                                                             'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                             'is_not_gtlk': False,
                                                             'desire_type_lk': 'все ЛК',
                                                             'desire_param': [('стоимость фондирования', categ), False],
                                                             'selection_names_list': [full_name, ],
                                                             'is_custom': False
                                                             })[1]))
                            tt = self.f_weighted_av(
                                **{'dates': report_dates[2:], 'param': [('стоимость фондирования', categ), False]})
                            res.append(tt[0])
                            res.append(tt[1])
                            self.f_write_table_rep(
                                **{'wb': wb, 'ws': ws, 'bg_color': '#F3E290',
                                   'title': f'Стоимость фондирования {list_name}',
                                   'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                                 'Средневзвешенная всех ЛК'],
                                   'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                            counter += 1
                            # график
                            chart_line = wb.add_chart({'type': 'line'})
                            chart_line.set_y_axis({
                                'name': '%',
                                'name_font': {'bold': False}
                            })
                            chart_line.add_series({
                                'name': f'{name}',
                                'categories': ['ФСБУ', 19, 16, 19, 20],
                                'values': ['ФСБУ', 20, 16, 20, 20],
                                'line': {'color': '#B9BCBD'},
                                'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                           'border': {'color': '#B9BCBD'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная сопоставимой выборки',
                                'categories': ['ФСБУ', 19, 16, 19, 20],
                                'values': ['ФСБУ', 21, 16, 21, 20],
                                'line': {'color': '#F9AF1B'},
                                'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                           'border': {'color': '#F9AF1B'},
                                           'size': 5},
                            })
                            chart_line.add_series({
                                'name': f'Средневзвешенная всех ЛК',
                                'categories': ['ФСБУ', 19, 16, 19, 20],
                                'values': ['ФСБУ', 22, 16, 22, 20],
                                'line': {'color': '#1BB9F9'},
                                'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                           'border': {'color': '#1BB9F9'},
                                           'size': 5},
                            })
                            chart_line.set_size({'width': 700, 'height': 300})
                            chart_line.set_title(
                                {'name': 'Стоимость фондирования', 'name_font': {'bold': False, 'size': 14}})
                            chart_line.set_legend({'position': 'bottom'})
                            ws.insert_chart(76, 8, chart_line)
                            # Структура фондирования 
                            res = []
                            for cc in ("Ручной выбор", "Сопоставимая выборка", "Все лизинговые компании"):
                                a = self.f_write_res(calculate(**{'desire_dates_choice': report_dates[5:],
                                                          'desire_report_type': 'Экономические индикаторы',
                                                          'desire_comparable': cc,
                                                          'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                          'is_not_gtlk': False,
                                                          'desire_type_lk': 'все ЛК',
                                                          'desire_param': [('Кредиты полученные', categ2), False],
                                                          'selection_names_list': [full_name, ],
                                                          'is_custom': False
                                                          })[1])
                                b = self.f_write_res(calculate(**{'desire_dates_choice': report_dates[5:],
                                                          'desire_report_type': 'Экономические индикаторы',
                                                          'desire_comparable': cc,
                                                          'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                          'is_not_gtlk': False,
                                                          'desire_type_lk': 'все ЛК',
                                                          'desire_param': [('Займы полученные', categ2), False],
                                                          'selection_names_list': [full_name, ],
                                                          'is_custom': False
                                                          })[1])
                                c = self.f_write_res(calculate(**{'desire_dates_choice': report_dates[5:],
                                                          'desire_report_type': 'Экономические индикаторы',
                                                          'desire_comparable': cc,
                                                          'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                          'is_not_gtlk': False,
                                                          'desire_type_lk': 'все ЛК',
                                                          'desire_param': [
                                                              ('Выпущенные долговые ценные бумаги', categ2), False],
                                                          'selection_names_list': [full_name, ],
                                                          'is_custom': False
                                                          })[1])
                                su = a + b + c
                                res.append(a * 100 / su)
                                res.append(b * 100 / su)
                                res.append(c * 100 / su)
                            tn = f'Структура фондирования ({list_name})'
                            rn = [f'Кредиты', 'Займы', 'Облигации']
                            format1 = wb.add_format()
                            format1.set_bg_color('#F3E290')
                            # закрашиваем таблицу
                            for i in range(full_cords[counter][0],
                                           full_cords[counter][0] + len(rn) + 2):  # строки
                                for j in range(full_cords[counter][1], full_cords[counter][1] + 7):  # столбцы
                                    ws.write_blank(i, j, '', format1)
                            ws.merge_range(full_cords[counter][0] + 1, full_cords[counter][1] + 1,
                                           full_cords[counter][0] + 1, full_cords[counter][1] + 2, f"{name}", format1)
                            ws.merge_range(full_cords[counter][0] + 1, full_cords[counter][1] + 3,
                                           full_cords[counter][0] + 1, full_cords[counter][1] + 4,
                                           f"Сопоставимая выборка", format1)
                            ws.merge_range(full_cords[counter][0] + 1, full_cords[counter][1] + 5,
                                           full_cords[counter][0] + 1, full_cords[counter][1] + 6, f"Все ЛК", format1)
                            # даты
                            for i in range(6):
                                ws.write(full_cords[counter][0] + 2, full_cords[counter][1] + i + 1,
                                         report_dates[5:][int(i % 2)], format1)
                            # заголовок
                            format1.set_align('center')
                            ws.merge_range(full_cords[counter][0], full_cords[counter][1], full_cords[counter][0],
                                           full_cords[counter][1] + 5, tn,
                                           format1)
                            # построчно записываем результаты
                            for i, nn in enumerate(rn):
                                format1 = wb.add_format()
                                format1.set_bg_color('#F3E290')
                                ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1], nn, format1)
                                for j in range(6):
                                    format1 = wb.add_format()
                                    format1.set_bg_color('#F3E290')
                                    format1.set_border(7)
                                    s = '%'
                                    if isinstance(res[i + int(3 * (j // 2))][int(j % 2)], str):
                                        if 'недостаточно данных' in res[i + int(3 * (j // 2))][int(j % 2)]:
                                            ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                                     'недостаточно данных', format1)
                                        else:
                                            format1.set_num_format('0.0##\%;[Red](0.0##\%)')
                                            ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                                     round(float(res[i + int(3 * (j // 2))][int(j % 2)]), 1),
                                                     format1)
                                    elif np.isnan(res[i + int(3 * (j // 2))][int(j % 2)]) or np.isinf(
                                            res[i + int(3 * (j // 2))][int(j % 2)]):
                                        ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                                 'недостаточно данных', format1)
                                    else:
                                        format1.set_num_format('0.0##\%;[Red](0.0##\%)')
                                        ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                                 round(res[i + int(3 * (j // 2))][int(j % 2)], 1), format1)
                            # график
                            chart_col = wb.add_chart({'type': 'column', 'subtype': 'percent_stacked'})
                            chart_col.add_series({
                                'name': f'Кредиты',
                                'categories': ['ФСБУ', 25, 16, 26, 21],
                                'values': ['ФСБУ', 27, 16, 27, 21],
                                'fill': {'color': '#B9BCBD'},
                            })
                            chart_col.add_series({
                                'name': f'Займы',
                                'categories': ['ФСБУ', 25, 16, 26, 21],
                                'values': ['ФСБУ', 28, 16, 28, 21],
                                'fill': {'color': '#F9AF1B'},
                            })
                            chart_col.add_series({
                                'name': f'Облигации',
                                'categories': ['ФСБУ', 25, 16, 26, 21],
                                'values': ['ФСБУ', 29, 16, 29, 21],
                                'fill': {'color': '#1BB9F9'},
                            })
                            chart_col.set_y_axis({
                                'name': '%',
                                'name_font': {'bold': False}
                            })
                            chart_col.set_size({'width': 700, 'height': 300})
                            chart_col.set_title(
                                {'name': 'Структура фондирования', 'name_font': {'bold': False, 'size': 14}})
                            chart_col.set_legend({'position': 'bottom'})
                            ws.insert_chart(60, 15, chart_col)
                            ws.autofit()
                    else:
                      # данных мсфо нет, указываем управленческие данные на стр фсбу
                        list_name = 'ФСБУ'
                        categ = 'По данным ФСБУ'
                        categ2 = 'Данные ФСБУ'
                        full_cords = [(8, 1), (8, 8),
                                      (22, 1), (22, 8), (28, 8), (22, 15), (28, 15),
                                      (34, 1), (34, 8), (34, 15), (40, 1), (40, 8), (40, 15), (46, 1), (46, 8),
                                      (52, 15),
                                      (58, 1), (58, 8), (62, 15), (68, 1), (68, 8), (75, 8),
                                      (68, 15), (74, 15)]
                        writer = pd.ExcelWriter(fname, engine="xlsxwriter")
                        wb = writer.book
                        ws = wb.add_worksheet(list_name)
                        counter = 0
                        # шапка листа
                        self.func_rep_header(wb, ws, full_name)
                        # таблица АКТИВ -------------------------------------
                        res = []
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы', [('в т.ч. чистые инвестиции в лизинг (по договорам финансового лизинга)', categ2), False],
                                         'Экономические индикаторы', [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Основные средства', categ2), False],
                                         'Экономические индикаторы',
                                         [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Нематериальные активы', categ2), False],
                                         'Экономические индикаторы',
                                         [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('в т.ч. стоимость имущества, переданного в операционную аренду', categ2), False],
                                         'Экономические индикаторы',
                                         [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Займы выданные', categ2), False], 'Экономические индикаторы',
                                         [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Дебиторская задолженность по расторгнутым договорам лизинга', categ2),
                                          False],
                                         'Экономические индикаторы', [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Денежные средства', categ2),
                                          False],
                                         'Экономические индикаторы', [('Активы', categ2), False], full_name)
                        s = [100 - (np.array([res[j][i] for j in range(len(res))])).sum() for i in range(5)]
                        res.append(s)  # Прочие Активы
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Активы', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#C8E9F4', 'title': f'АКТИВ {list_name}',
                               'row_names': ['Чистые инвестиции в лизинг', 'Основные средства',
                                             'Нематериальные активы',
                                             'Стоимость имущества, переданного в операционную аренду', 'Займы выданные',
                                             'ДЗ по расторгнутым договорам', 'Денежные средства','Прочие активы', 'Активы ВСЕГО'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter],
                               'symb': ['%', '%', '%', '%', '%', '%', '%', '%', '']})
                        counter += 1
                        # таблица ПАССИВ -------------------------------------
                        res = []
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('ИТОГО КАПИТАЛ', categ2), False],
                                         'Экономические индикаторы', [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Нераспределенная прибыль', categ2), False], 'Экономические индикаторы',
                                         [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Кредиты полученные', categ2), False], 'Экономические индикаторы',
                                         [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Займы полученные', categ2), False], 'Экономические индикаторы',
                                         [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Выпущенные долговые ценные бумаги', categ2), False],
                                         'Экономические индикаторы',
                                         [('Активы', categ2), False], full_name)
                        self.f_calc_perc(res, report_dates[2:], 'Экономические индикаторы',
                                         [('Дебиторская задолженность по расторгнутым договорам лизинга', categ2), False],
                                         'Экономические индикаторы', [('Активы', categ2), False], full_name)
                        s = [100 - (np.array([res[j][i] for j in range(len(res))])).sum() for i in range(5)]
                        res.append(s)  # Прочие обязательства
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Активы', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#C8E9F4', 'title': f'ПАССИВ {list_name}',
                               'row_names': ['КАПИТАЛ ВСЕГО', 'Нераспределенная прибыль',
                                             'Кредиты', 'Займы', 'Облигации',
                                             'Кредиторская задолженность', 'Прочие обязательства',
                                             'ПАССИВЫ ВСЕГО'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter],
                               'symb': ['%', '%', '%', '%', '%', '%', '%', '']})
                        counter += 1
                        # фиолетовые таблицы
                        # ОПУ (за квартал)----------------------------------
                        res = []
                        tmp = categ if msfo_flag else categ2
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Выручка', tmp), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Себестоимость продаж', categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [(
                                                                          'Управленческие расходы',
                                                                          categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [(
                                                                          'Проценты к уплате',
                                                                          categ2), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Прибыль (убыток) от продаж', categ2),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('в т.ч. переоценка стоимости имущества, переданного в операционную аренду', categ2),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))

                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'ОПУ {list_name} (за квартал)',
                               'row_names': ['Выручка', 'Себестоимость продаж', 'Управленческие расходы',
                                             'Проценты к уплате', 'Чистая прибыль (убыток)',
                                             'Переоценка стоимости имущества по операренде',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1

                        # ROE ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('ROE', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt = self.f_weighted_av(**{'dates': report_dates[2:], 'param': [('ROE', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])

                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'ROE ({list_name})',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 23, 9, 23, 13],
                            'values': ['ФСБУ', 24, 9, 24, 13],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                       'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['ФСБУ', 23, 9, 23, 13],
                            'values': ['ФСБУ', 25, 9, 25, 13],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                       'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['ФСБУ', 23, 9, 23, 13],
                            'values': ['ФСБУ', 26, 9, 26, 13],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                       'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'ROE', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(99, 1, chart_line)
                        # Leverage ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Leverage', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt = self.f_weighted_av(
                            **{'dates': report_dates[2:], 'param': [('Leverage', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'Leverage ({list_name})',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 29, 9, 29, 13],
                            'values': ['ФСБУ', 30, 9, 30, 13],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                       'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['ФСБУ', 29, 9, 29, 13],
                            'values': ['ФСБУ', 31, 9, 31, 13],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                       'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['ФСБУ', 29, 9, 29, 13],
                            'values': ['ФСБУ', 32, 9, 32, 13],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                       'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'Финансовый рычаг', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(141, 8, chart_line)
                        # CIR ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('CIR', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt = self.f_weighted_av(**{'dates': report_dates[2:], 'param': [('CIR', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4', 'title': f'CIR ({list_name})',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 23, 16, 23, 20],
                            'values': ['ФСБУ', 24, 16, 24, 20],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                       'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['ФСБУ', 23, 16, 23, 20],
                            'values': ['ФСБУ', 25, 16, 25, 20],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                       'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['ФСБУ', 23, 16, 23, 20],
                            'values': ['ФСБУ', 26, 16, 26, 20],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                       'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'CIR', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(141, 15, chart_line)
                        # Процентный спрэд ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('процентный спрэд', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt = self.f_weighted_av(
                            **{'dates': report_dates[2:], 'param': [('процентный спрэд', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#D9C8F4',
                               'title': f'Процентный спрэд ({list_name})',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 29, 16, 29, 20],
                            'values': ['ФСБУ', 30, 16, 30, 20],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                       'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['ФСБУ', 29, 16, 29, 20],
                            'values': ['ФСБУ', 31, 16, 31, 20],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                       'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['ФСБУ', 29, 16, 29, 20],
                            'values': ['ФСБУ', 32, 16, 32, 20],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                       'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'Процентный спрэд', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(115, 1, chart_line)
                        # красные таблицы
                        # НБ (фин.лизинг), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('новый бизнес', 'финансовый лизинг'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'финансовый лизинг'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'финансовый лизинг'), False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'НБ (фин.лизинг), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Новый бизнес (фин.лизинг)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 35, 2, 35, 6],
                            'values': ['ФСБУ', 36, 2, 36, 6],
                            'fill': {'color': '#B9BCBD'},
                        })
                        #'#F9AF1B'
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['ФСБУ', 35, 2, 35, 6],
                            'values': ['ФСБУ', 37, 2, 37, 6],
                            'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'}, 'border':{'color':'#F9AF1B'},'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['ФСБУ', 35, 2, 35, 6],
                            'values': ['ФСБУ', 38, 2, 38, 6],
                            'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},'border':{'color': '#1BB9F9'}, 'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title({'name': 'Новый бизнес (фин.лизинг)','name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(83, 1, chart_col)
                        # НБ (опер.лизинг), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('новый бизнес', 'операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'операционная аренда'), False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'НБ (опер.лизинг), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Новый бизнес (опер.аренда)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 35, 9, 35, 13],
                            'values': ['ФСБУ', 36, 9, 36, 13],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['ФСБУ', 35, 9, 35, 13],
                            'values': ['ФСБУ', 37, 9, 37, 13],
                            'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},'border':{'color': '#F9AF1B'}, 'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['ФСБУ', 35, 9, 35, 13],
                            'values': ['ФСБУ', 38, 9, 38, 13],
                            'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border':{'color': '#1BB9F9'},'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title({'name': 'Новый бизнес (опер.аренда)','name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(83, 8, chart_col)
                        # НБ (все продукты), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('новый бизнес', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('темп прироста нового бизнеса скользящий год (год к году)', 'все продукты'), False],
                                                         #'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'НБ (все продукты), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        #график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Новый бизнес (все продукты)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 35, 16, 35, 20],
                            'values': ['ФСБУ', 36, 16, 36, 20],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['ФСБУ', 35, 16, 35, 20],
                            'values': ['ФСБУ', 37, 16, 37, 20],
                             'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle','fill': {'color':'#F9AF1B'},'border':{'color': '#F9AF1B'}, 'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['ФСБУ', 35, 16, 35, 20],
                            'values': ['ФСБУ', 38, 16, 38, 20],
                             'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle','fill': {'color':'#1BB9F9'},'border':{'color': '#1BB9F9'}, 'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title({'name': 'Новый бизнес (все продукты)','name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(83,15, chart_col)
                        # Лизинговый портфель (опер.лизинг), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('лизинговый портфель', 'Данные ФСБУ: операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [(
                                                                          'темп прироста лизингового портфеля (год к году)',
                                                                          'Данные ФСБУ: операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [(
                                                                          'темп прироста лизингового портфеля (год к году)',
                                                                          'Данные ФСБУ: операционная аренда'), False],
                                                         # 'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8',
                               'title': f'Лизинговый портфель (опер.лизинг), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Портфель (опер.аренда)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 41, 2,41, 6],
                            'values': ['ФСБУ', 42, 2, 42, 6],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['ФСБУ', 41, 2, 41, 6],
                            'values': ['ФСБУ', 43, 2, 43, 6],
                            'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                       'border': {'color': '#F9AF1B'}, 'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['ФСБУ', 41,2, 41, 6],
                            'values': ['ФСБУ', 44, 2, 44, 6],
                            'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                       'border': {'color': '#1BB9F9'}, 'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title(
                            {'name': 'Портфель (опер.аренда)', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(99, 8, chart_col)
                        # Лизинговый портфель (все продукты), скг ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('лизинговый портфель', 'Данные ФСБУ: все продукты'),
                                                                          False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [(
                                                                          'темп прироста лизингового портфеля (год к году)',
                                                                          'Данные ФСБУ: все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [(
                                                                          'темп прироста лизингового портфеля (год к году)',
                                                                          'Данные ФСБУ: все продукты'), False],
                                                         # 'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8',
                               'title': f'Лизинговый портфель (все продукты), скг',
                               'row_names': [f'{name}', f'Темп прироста по {name} (г./г.), %',
                                             f'Темп прироста по сопоставимой выборке (г./г.), %'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Портфель (все продукты)'})
                        chart_col.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 41, 9, 41, 13],
                            'values': ['ФСБУ', 42, 9, 42, 13],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по {name} (г./г.), %',
                            'categories': ['ФСБУ', 41, 9, 41, 13],
                            'values': ['ФСБУ', 43, 9, 43, 13],
                            'line': {'color': '#F9AF1B'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                       'border': {'color': '#F9AF1B'}, 'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Темп прироста по сопоставимой выборке (г./г.), %',
                            'categories': ['ФСБУ', 41, 9, 41, 13],
                            'values': ['ФСБУ', 44, 9, 44, 13],
                            'line': {'color': '#1BB9F9'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                       'border': {'color': '#1BB9F9'}, 'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title(
                            {'name': 'Портфель (все продукты)', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(99, 15, chart_col)
                        #Структура лизингового портфеля (фин.лизинг)
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('сегменты: легковые автомобили', 'финансовый лизинг'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: грузовые автомобили', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: ж/д', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: авиа', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: спецтехника', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: недвижимость', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: c/x', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('сегменты: суда', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: прочее', 'финансовый лизинг'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'Структура лизингового портфеля (фин.лизинг)',
                               'row_names': ['Леговые автомобили','Грузовые автомобили','Ж/д техника','Авиа',
                                             'Спецтехника','Недвижимость','С/х техника','Суда','Прочее',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        #Структура лизингового портфеля (опер.лизинг)
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('сегменты: легковые автомобили', 'операционная аренда'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: грузовые автомобили', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: ж/д', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: авиа', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: спецтехника', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: недвижимость', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: c/x', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: суда', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: прочее', 'операционная аренда'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'Структура лизингового портфеля (опер.лизинг)',
                               'row_names': ['Леговые автомобили','Грузовые автомобили','Ж/д техника','Авиа',
                                             'Спецтехника','Недвижимость','С/х техника','Суда','Прочее',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        #Структура лизингового портфеля (все продукты)
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('сегменты: легковые автомобили', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: грузовые автомобили', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: ж/д', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: авиа', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: спецтехника', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: недвижимость', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: c/x', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: суда', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('сегменты: прочее', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F4D7C8', 'title': f'Структура лизингового портфеля (все продукты)',
                               'row_names': ['Леговые автомобили','Грузовые автомобили','Ж/д техника','Авиа',
                                             'Спецтехника','Недвижимость','С/х техника','Суда','Прочее',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1

                        # график
                        chart_pie = wb.add_chart({'type': 'pie'})
                        chart_pie.add_series({
                            #'name': f'Легковые автомобили',
                            'categories': ['ФСБУ', 48, 8, 56, 8],
                            'values': ['ФСБУ', 48, 13, 56, 13],
                            #'fill': {'color': '#B9BCBD'},
                            'points': [
                                {'fill': {'color': '#5CD4FA'}},
                                {'fill': {'color': '#F3AD31'}},
                                {'fill': {'color': '#D0D0D0'}},
                                {'fill': {'color': 'yellow'}},
                                {'fill': {'color': '#3650F1'}},
                                {'fill': {'color': 'green'}},
                                {'fill': {'color': '#021AAD'}},
                                {'fill': {'color': 'brown'}},
                            ],
                            'data_labels': {'percentage':True, 'position': 'outside_end'},
                        })

                        chart_pie.set_size({'width': 700, 'height': 500})
                        chart_pie.set_title(
                            {'name': f'Структура портфеля (все продукты на последнюю дату) {name}', 'name_font': {'bold': False, 'size': 14}})

                        ws.insert_chart(189, 15, chart_pie)
                        # зеленые таблички
                        # ПА (опер.лизинг)
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [('расторжения', 'операционная аренда'),
                                                                                  False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('реструктуризации', 'операционная аренда'),
                                                                     False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('покрытие NPL90+ всеми резервами',
                                                                      'операционная аренда'),
                                                                     False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('доля NPL90+ в портфеле', 'операционная аренда'),
                                                                     False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Сопоставимая выборка',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('доля NPL90+ в портфеле', 'операционная аренда'),
                                                                     False],
                                                                 # 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('доля проблемных активов', 'Данные ФСБУ: операционная аренда'),
                                                                     False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Сопоставимая выборка',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('доля проблемных активов', 'Данные ФСБУ: операционная аренда'),
                                                                     False],
                                                                 # 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8', 'title': f'ПА (опер.лизинг)',
                               'row_names': [f'Расторгнутые договоры {name}', f'Обслуживаемая реструктуризация {name}',
                                             f'NPL90+ {name}', f'доля NPL90+ {name}, %',
                                             f'доля NPL90+ по сопоставимой выборке, %',
                                             f'доля проблемной задолженности в ЛП {name}, %',
                                             f'доля проблемной задолженности в ЛП по сопоставимой выборке, %', ],
                               'dates': report_dates[2:], 'res': res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'subtype': 'stacked'})
                        chart_col.add_series({
                            'name': f'NPL90+ {name}',
                            'categories': ['ФСБУ', 53, 16, 53, 20],
                            'values': ['ФСБУ', 56, 16, 56, 20],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Обслуживаемая реструктуризация {name}',
                            'categories': ['ФСБУ', 53, 16, 53, 20],
                            'values': ['ФСБУ', 55, 16, 55, 20],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Расторгнутые договоры {name}',
                            'categories': ['ФСБУ', 53, 16, 53, 20],
                            'values': ['ФСБУ', 54, 16, 54, 20],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        # желтый
                        chart_line.add_series({
                            'name': f'доля NPL90+ {name}, %',
                            'categories': ['ФСБУ', 53, 16, 53, 20],
                            'values': ['ФСБУ', 57, 9, 57, 13],
                            'line': {'color': '#EFDD42'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EFDD42'}, 'border': {'color': '#EFDD42'},
                                       'size': 5},
                        })
                        # синий
                        chart_line.add_series({
                            'name': f'доля NPL90+ по сопоставимой выборке, %',
                            'categories': ['ФСБУ', 53, 16, 53, 20],
                            'values': ['ФСБУ', 58, 16, 58, 20],
                            'line': {'color': '#6988F1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#6988F1'}, 'border': {'color': '#6988F1'},
                                       'size': 5},
                        })
                        # зеленый
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по {name}, %',
                            'categories': ['ФСБУ', 53, 16, 53, 20],
                            'values': ['ФСБУ', 59, 16, 59, 20],
                            'line': {'color': '#7EC673'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#7EC673'}, 'border': {'color': '#7EC673'},
                                       'size': 5},
                        })
                        # темно-синий
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по сопоставимой выборке, %',
                            'categories': ['ФСБУ', 53, 16, 53, 20],
                            'values': ['ФСБУ', 60, 16, 60, 20],
                            'line': {'color': '#1D46D1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1D46D1'}, 'border': {'color': '#1D46D1'},
                                       'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 500})
                        chart_col.set_title(
                            {'name': 'Проблемные активы (опер.лизинг)', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(115, 8, chart_col)
                        # ПА (все продукты)
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [('расторжения', 'все продукты'), False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('реструктуризации', 'все продукты'),
                                                                     False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('покрытие NPL90+ всеми резервами', 'все продукты'),
                                                                     False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('доля NPL90+ в портфеле', 'все продукты'),
                                                                     False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Сопоставимая выборка',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('доля NPL90+ в портфеле', 'все продукты'),
                                                                     False],
                                                                 # 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Ручной выбор',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('доля проблемных активов', 'Данные ФСБУ: все продукты'),
                                                                     False],
                                                                 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                                 'desire_report_type': 'Управленческие данные',
                                                                 'desire_comparable': 'Сопоставимая выборка',
                                                                 'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                                 'is_not_gtlk': False,
                                                                 'desire_type_lk': 'все ЛК',
                                                                 'desire_param': [
                                                                     ('доля проблемных активов', 'Данные ФСБУ: все продукты'),
                                                                     False],
                                                                 # 'selection_names_list': [full_name, ],
                                                                 'is_custom': False
                                                                 })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8', 'title': f'ПА (все продукты)',
                               'row_names': [f'Расторгнутые договоры {name}', f'Обслуживаемая реструктуризация {name}',
                                             f'NPL90+ {name}', f'доля NPL90+ {name}, %',
                                             f'доля NPL90+ по сопоставимой выборке, %',
                                             f'доля проблемной задолженности в ЛП {name}, %',
                                             f'доля проблемной задолженности в ЛП по сопоставимой выборке, %', ],
                               'dates': report_dates[2:], 'res': res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'subtype': 'stacked'})
                        chart_col.add_series({
                            'name': f'NPL90+ {name}',
                            'categories': ['ФСБУ', 59, 2, 59, 6],
                            'values': ['ФСБУ', 62, 2, 62, 6],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Обслуживаемая реструктуризация {name}',
                            'categories': ['ФСБУ', 59, 2, 59, 6],
                            'values': ['ФСБУ', 61, 2, 61, 6],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Расторгнутые договоры {name}',
                            'categories': ['ФСБУ', 59, 2, 59, 6],
                            'values': ['ФСБУ', 60, 2, 60, 6],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        # желтый
                        chart_line.add_series({
                            'name': f'доля NPL90+ {name}, %',
                            'categories': ['ФСБУ', 59, 2, 59, 6],
                            'values': ['ФСБУ', 63, 2, 63, 6],
                            'line': {'color': '#EFDD42'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EFDD42'}, 'border': {'color': '#EFDD42'},
                                       'size': 5},
                        })
                        # синий
                        chart_line.add_series({
                            'name': f'доля NPL90+ по сопоставимой выборке, %',
                            'categories': ['ФСБУ', 59, 2, 59, 6],
                            'values': ['ФСБУ', 64, 2, 64, 6],
                            'line': {'color': '#6988F1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#6988F1'}, 'border': {'color': '#6988F1'},
                                       'size': 5},
                        })
                        # зеленый
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по {name}, %',
                            'categories': ['ФСБУ', 59, 2, 59, 6],
                            'values': ['ФСБУ', 65, 2, 65, 6],
                            'line': {'color': '#7EC673'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#7EC673'}, 'border': {'color': '#7EC673'},
                                       'size': 5},
                        })
                        # темно-синий
                        chart_line.add_series({
                            'name': f'доля проблемной задолженности в ЛП по сопоставимой выборке, %',
                            'categories': ['ФСБУ', 59, 2, 59, 6],
                            'values': ['ФСБУ', 66, 2, 66, 6],
                            'line': {'color': '#1D46D1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#1D46D1'}, 'border': {'color': '#1D46D1'},
                                       'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 500})
                        chart_col.set_title(
                            {'name': 'Проблемные активы (все продукты)', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(115, 15, chart_col)
                        # Данные по резервам
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [(
                                                                          'Резервы по договорам финансового лизинга',
                                                                          'Данные ФСБУ'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Резервы по договорам операционной аренды',
                                                              'Данные ФСБУ'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Прочие резервы', 'Данные ФСБУ'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие NPL90+ всеми резервами', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие проблемных активов всеми резервами',
                                                              'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие NPL90+ всеми резервами', 'все продукты'),
                                                             False],
                                                         # 'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Сопоставимая выборка',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('покрытие проблемных активов всеми резервами',
                                                              'все продукты'),
                                                             False],
                                                         # 'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8', 'title': f'Данные по резервам ФСБУ',
                               'row_names': ['Резервы по финлизингу', 'Резервы по операренде', 'Прочие резервы',
                                             f'Покрытие NPL90+ всеми резервами {name}',
                                             f'Покрытие проблемных активов всеми резервами {name}',
                                             f'Покрытие NPL90+ всеми резервами(сопоставимая выборка)',
                                             f'Покрытие проблемных активов всеми резервами(сопоставимая выборка)'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_col = wb.add_chart({'type': 'column', })
                        chart_col.add_series({
                            'name': f'Резервы по финлизингу',
                            'categories': ['ФСБУ', 59, 9, 59, 13],
                            'values': ['ФСБУ', 60, 9, 60, 13],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Резервы по операренде',
                            'categories': ['ФСБУ', 59, 9, 59, 13],
                            'values': ['ФСБУ',61, 9, 61, 13],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Прочие резервы',
                            'categories': ['ФСБУ',59, 9, 59, 13],
                            'values': ['ФСБУ', 62, 9, 62, 13],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y2_axis({
                            'name': '%',
                        })
                        # желтый
                        chart_line.add_series({
                            'name': f'Покрытие NPL90+ всеми резервами {name}, %',
                            'categories': ['ФСБУ', 59, 9, 59, 13],
                            'values': ['ФСБУ', 63, 9, 63, 13],
                            'line': {'color': '#EFDD42'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EFDD42'},
                                       'border': {'color': '#EFDD42'}, 'size': 5},
                        })
                        # красный
                        chart_line.add_series({
                            'name': f'Покрытие проблемных активов всеми резервами {name}, %',
                            'categories': ['ФСБУ',59, 9, 59, 13],
                            'values': ['ФСБУ', 64, 9, 64, 13],
                            'line': {'color': '#EF4242'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#EF4242'},
                                       'border': {'color': '#EF4242'}, 'size': 5},
                        })
                        # зеленый
                        chart_line.add_series({
                            'name': f'Покрытие NPL90+ всеми резервами (сопоставимая выборка), %',
                            'categories': ['ФСБУ', 59, 9, 59, 13],
                            'values': ['ФСБУ', 65, 9, 65, 13],
                            'line': {'color': '#7EC673'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#7EC673'},
                                       'border': {'color': '#7EC673'}, 'size': 5},
                        })
                        # синий
                        chart_line.add_series({
                            'name': f'Покрытие проблемных активов всеми резервами (сопоставимая выборка), %',
                            'categories': ['ФСБУ', 59, 9, 59, 13],
                            'values': ['ФСБУ', 66, 9, 66, 13],
                            'line': {'color': '#6988F1'},
                            'y2_axis': True,
                            'marker': {'type': 'circle', 'fill': {'color': '#6988F1'},
                                       'border': {'color': '#6988F1'},
                                       'size': 5},
                        })
                        chart_col.combine(chart_line)
                        chart_col.set_size({'width': 700, 'height': 500})
                        chart_col.set_title(
                            {'name': 'Резервы', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(173, 8, chart_col)
                        #Объем, досрочный
                        #объем изъятых активов по остаточногй и фактической стоимости(за квартал)--------
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('Объем изъятых активов по остаточной стоимости', 'По данным ФСБУ'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('Объем изъятых активов по фактической стоимости', 'По данным ФСБУ'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8',
                               'title': f'Объем изъятых активов по остаточной и фактической стоимости (за квартал)',
                               'row_names': ['Объем изъятых активов по остаточной стоимости',
                                             'Объем изъятых активов по фактической стоимости',
                                             #'Активы, предназначенные для продажи по расторгнутым договорам лизинга',
                                             ],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        #график
                        chart_col = wb.add_chart({'type': 'column', 'name': 'Объем изъятых активов по остаточной и фактической стоимости'})
                        chart_col.add_series({
                            'name': f'Объем изъятых активов по остаточной стоимости',
                            'categories': ['ФСБУ', 63, 16, 63, 20],
                            'values': ['ФСБУ', 64, 16, 64, 20],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Объем изъятых активов по фактической стоимости',
                            'categories': ['ФСБУ', 63, 16, 63, 20],
                            'values': ['ФСБУ', 65, 16, 65, 20],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.set_y_axis({
                            'name': 'млн руб.',
                            'name_font': {'bold': False}
                        })

                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title(
                            {'name': 'Объем изъятых активов по остаточной и фактической стоимости', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(131, 1, chart_col)
                        #Досрочный выкуп и замороженные активы (за квартал)--------
                        res=[]
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('объем досрочно выкупленного имущества', 'все продукты'), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Управленческие данные',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [
                                                             ('объем замороженных активов', 'все продукты'),
                                                             False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#DAF4C8',
                               'title': f'Досрочный выкуп и замороженные активы (за квартал)',
                               'row_names': ['Объем досрочно выкупленного имущества',
                                             'Объем замороженных активов',],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': 'Млн руб.',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'Объем досрочно выкупленного имущества',
                            'categories': ['ФСБУ', 69, 2, 69, 6],
                            'values': ['ФСБУ',   70, 2, 70, 6],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'}, 'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Объем замороженных активов',
                            'categories': ['ФСБУ',  69, 2, 69, 6],
                            'values': ['ФСБУ',   71, 2, 71, 6],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'}, 'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'Досрочка и выкупы', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(173, 15, chart_line)

                        # желтые таблицы -----------------------------
                        # Стоимость фондирования  ----------------------------------
                        res = []
                        res.append(self.f_write_res(calculate(**{'desire_dates_choice': report_dates[2:],
                                                         'desire_report_type': 'Экономические индикаторы',
                                                         'desire_comparable': 'Ручной выбор',
                                                         'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                         'is_not_gtlk': False,
                                                         'desire_type_lk': 'все ЛК',
                                                         'desire_param': [('стоимость фондирования', categ), False],
                                                         'selection_names_list': [full_name, ],
                                                         'is_custom': False
                                                         })[1]))
                        tt = self.f_weighted_av(
                            **{'dates': report_dates[2:], 'param': [('стоимость фондирования', categ), False]})
                        res.append(tt[0])
                        res.append(tt[1])
                        self.f_write_table_rep(
                            **{'wb': wb, 'ws': ws, 'bg_color': '#F3E290',
                               'title': f'Стоимость фондирования {list_name}',
                               'row_names': [f'{name}', 'Средневзвешенная сопоставимой выборки',
                                             'Средневзвешенная всех ЛК'],
                               'dates': report_dates[2:], 'res':res, 'cords': full_cords[counter], })
                        counter += 1
                        # график
                        chart_line = wb.add_chart({'type': 'line'})
                        chart_line.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_line.add_series({
                            'name': f'{name}',
                            'categories': ['ФСБУ', 69, 9, 69, 13],
                            'values': ['ФСБУ', 70, 9, 70, 13],
                            'line': {'color': '#B9BCBD'},
                            'marker': {'type': 'circle', 'fill': {'color': '#B9BCBD'},
                                       'border': {'color': '#B9BCBD'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная сопоставимой выборки',
                            'categories': ['ФСБУ', 69, 9, 69, 13],
                            'values': ['ФСБУ', 71, 9, 71, 13],
                            'line': {'color': '#F9AF1B'},
                            'marker': {'type': 'circle', 'fill': {'color': '#F9AF1B'},
                                       'border': {'color': '#F9AF1B'},
                                       'size': 5},
                        })
                        chart_line.add_series({
                            'name': f'Средневзвешенная всех ЛК',
                            'categories': ['ФСБУ', 69, 9, 69, 13],
                            'values': ['ФСБУ', 72, 9, 72, 13],
                            'line': {'color': '#1BB9F9'},
                            'marker': {'type': 'circle', 'fill': {'color': '#1BB9F9'},
                                       'border': {'color': '#1BB9F9'},
                                       'size': 5},
                        })
                        chart_line.set_size({'width': 700, 'height': 300})
                        chart_line.set_title(
                            {'name': 'Стоимость фондирования', 'name_font': {'bold': False, 'size': 14}})
                        chart_line.set_legend({'position': 'bottom'})
                        ws.insert_chart(157, 8, chart_line)
                        # Структура фондирования
                        res = []
                        for cc in ("Ручной выбор", "Сопоставимая выборка", "Все лизинговые компании"):
                            a = self.f_write_res(calculate(**{'desire_dates_choice': report_dates[5:],
                                                      'desire_report_type': 'Экономические индикаторы',
                                                      'desire_comparable': cc,
                                                      'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                      'is_not_gtlk': False,
                                                      'desire_type_lk': 'все ЛК',
                                                      'desire_param': [('Кредиты полученные', categ2), False],
                                                      'selection_names_list': [full_name, ],
                                                      'is_custom': False
                                                      })[1])
                            b = self.f_write_res(calculate(**{'desire_dates_choice': report_dates[5:],
                                                      'desire_report_type': 'Экономические индикаторы',
                                                      'desire_comparable': cc,
                                                      'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                      'is_not_gtlk': False,
                                                      'desire_type_lk': 'все ЛК',
                                                      'desire_param': [('Займы полученные', categ2), False],
                                                      'selection_names_list': [full_name, ],
                                                      'is_custom': False
                                                      })[1])
                            c = self.f_write_res(calculate(**{'desire_dates_choice': report_dates[5:],
                                                      'desire_report_type': 'Экономические индикаторы',
                                                      'desire_comparable': cc,
                                                      'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                                      'is_not_gtlk': False,
                                                      'desire_type_lk': 'все ЛК',
                                                      'desire_param': [
                                                          ('Выпущенные долговые ценные бумаги', categ2), False],
                                                      'selection_names_list': [full_name, ],
                                                      'is_custom': False
                                                      })[1])
                            su = a + b + c
                            res.append(a * 100 / su)
                            res.append(b * 100 / su)
                            res.append(c * 100 / su)
                        tn = f'Структура фондирования ({list_name})'
                        rn = [f'Кредиты', 'Займы', 'Облигации']
                        format1 = wb.add_format()
                        format1.set_bg_color('#F3E290')
                        # закрашиваем таблицу
                        for i in range(full_cords[counter][0],
                                       full_cords[counter][0] + len(rn) + 2):  # строки
                            for j in range(full_cords[counter][1], full_cords[counter][1] + 7):  # столбцы
                                ws.write_blank(i, j, '', format1)
                        ws.merge_range(full_cords[counter][0] + 1, full_cords[counter][1] + 1,
                                       full_cords[counter][0] + 1, full_cords[counter][1] + 2, f"{name}", format1)
                        ws.merge_range(full_cords[counter][0] + 1, full_cords[counter][1] + 3,
                                       full_cords[counter][0] + 1, full_cords[counter][1] + 4,
                                       f"Сопоставимая выборка", format1)
                        ws.merge_range(full_cords[counter][0] + 1, full_cords[counter][1] + 5,
                                       full_cords[counter][0] + 1, full_cords[counter][1] + 6, f"Все ЛК", format1)
                        # даты
                        for i in range(6):
                            ws.write(full_cords[counter][0] + 2, full_cords[counter][1] + i + 1,
                                     report_dates[5:][int(i % 2)], format1)
                        format1.set_align('center')
                        # заголовок
                        ws.merge_range(full_cords[counter][0], full_cords[counter][1], full_cords[counter][0],
                                       full_cords[counter][1] + 5, tn,
                                       format1)
                        # построчно записываем результаты
                        for i, nn in enumerate(rn):
                            format1 = wb.add_format()
                            format1.set_bg_color('#F3E290')
                            ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1], nn, format1)
                            for j in range(6):
                                format1 = wb.add_format()
                                format1.set_bg_color('#F3E290')
                                format1.set_border(7)
                                s = '%'
                                if isinstance(res[i + int(3 * (j // 2))][int(j % 2)], str):
                                    if 'недостаточно данных' in res[i + int(3 * (j // 2))][int(j % 2)]:
                                        ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                                 'недостаточно данных', format1)
                                    else:
                                        format1.set_num_format('0.0##\%;[Red](0.0##\%)')
                                        ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                                 round(float(res[i + int(3 * (j // 2))][int(j % 2)]), 1),
                                                 format1)
                                elif np.isnan(res[i + int(3 * (j // 2))][int(j % 2)]) or np.isinf(
                                        res[i + int(3 * (j // 2))][int(j % 2)]):
                                    ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                             'недостаточно данных', format1)
                                else:
                                    ws.write(full_cords[counter][0] + 3 + i, full_cords[counter][1] + j + 1,
                                             round(res[i + int(3 * (j // 2))][int(j % 2)]/100, 1), format1)
                        # график
                        chart_col = wb.add_chart({'type': 'column', 'subtype': 'percent_stacked'})
                        chart_col.add_series({
                            'name': f'Кредиты',
                            'categories': ['ФСБУ', 76, 9, 77, 14],
                            'values': ['ФСБУ', 78, 9, 78, 14],
                            'fill': {'color': '#B9BCBD'},
                        })
                        chart_col.add_series({
                            'name': f'Займы',
                            'categories': ['ФСБУ', 76, 9, 77, 14],
                            'values': ['ФСБУ', 79, 9, 79, 14],
                            'fill': {'color': '#F9AF1B'},
                        })
                        chart_col.add_series({
                            'name': f'Облигации',
                            'categories': ['ФСБУ',76, 9, 77, 14],
                            'values': ['ФСБУ', 80, 9, 80, 14],
                            'fill': {'color': '#1BB9F9'},
                        })
                        chart_col.set_y_axis({
                            'name': '%',
                            'name_font': {'bold': False}
                        })
                        chart_col.set_size({'width': 700, 'height': 300})
                        chart_col.set_title(
                            {'name': 'Структура фондирования', 'name_font': {'bold': False, 'size': 14}})
                        chart_col.set_legend({'position': 'bottom'})
                        ws.insert_chart(157, 15, chart_col)
                        ws.autofit()
                    writer.close()
                    
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText(f"Данные по компании ({name}) сформированы в файл: {fname}")
                    msg.setWindowTitle("Info")
                    msg.exec_()

                    writer.close()


        # функция для ручного выбора
        # переноса лк из доступного списка в выбранный
        # (self, выбранные лк, список, в кот. переносим лк, список, из кот. переносим)
        def move_lk(self, selected_items, list_to_move, cur_list):
            """
            функция для вкладки ручного выбора: перенос лк из одного списка в другой
            :param selected_items: выбранные лк
            :param list_to_move: список, в который переносим лк
            :param cur_list: список, из которого переносим
            """
            btn = self.sender()
            # получаем список текстовых названий лк
            names_txt = [name.data(QtCore.Qt.UserRole) for name in selected_items]
            # добавляем этот список имен в нужный
            for item in selected_items:
                new_it=QtWidgets.QListWidgetItem()
                new_it.setText(item.text())
                new_it.setData(QtCore.Qt.UserRole,item.data(QtCore.Qt.UserRole))
                list_to_move.addItem(new_it)
            # в цикле удаляем имена из старого списка
            for item in selected_items:
                cur_list.takeItem(cur_list.row(item))
            # редактируем список selection_names_list,
            # который передается в функции из calculations.py
            if btn == self.to_chosen_pb:
                for n in names_txt:
                    self.selection_names_list.append(n)
            else:
                for n in names_txt:
                    self.selection_names_list.remove(n)


        def dates_state(self):
            """
            записывает или удаляет выбранные даты в финальном списке desire_dates
            """

            if self.date1.isChecked() == True and self.date1.text() not in self.desire_dates:
                self.desire_dates.append(self.date1.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date2.isChecked() == True and self.date2.text() not in self.desire_dates:
                self.desire_dates.append(self.date2.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date3.isChecked() == True and self.date3.text() not in self.desire_dates:
                self.desire_dates.append(self.date3.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date4.isChecked() == True and self.date4.text() not in self.desire_dates:
                self.desire_dates.append(self.date4.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date5.isChecked() == True and self.date5.text() not in self.desire_dates:
                self.desire_dates.append(self.date5.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date6.isChecked() == True and self.date6.text() not in self.desire_dates:
                self.desire_dates.append(self.date6.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date7.isChecked() == True and self.date7.text() not in self.desire_dates:
                self.desire_dates.append(self.date7.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date8.isChecked() == True and self.date8.text() not in self.desire_dates:
                self.desire_dates.append(self.date8.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date9.isChecked() == True and self.date9.text() not in self.desire_dates:
                self.desire_dates.append(self.date9.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date10.isChecked() == True and self.date10.text() not in self.desire_dates:
                self.desire_dates.append(self.date10.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date11.isChecked() == True and self.date11.text() not in self.desire_dates:
                self.desire_dates.append(self.date11.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date12.isChecked() == True and self.date12.text() not in self.desire_dates:
                self.desire_dates.append(self.date12.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date1.isChecked() == False and self.date1.text() in self.desire_dates:
                self.desire_dates.remove(self.date1.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date2.isChecked() == False and self.date2.text() in self.desire_dates:
                self.desire_dates.remove(self.date2.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date3.isChecked() == False and self.date3.text() in self.desire_dates:
                self.desire_dates.remove(self.date3.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date4.isChecked() == False and self.date4.text() in self.desire_dates:
                self.desire_dates.remove(self.date4.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date5.isChecked() == False and self.date5.text() in self.desire_dates:
                self.desire_dates.remove(self.date5.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date6.isChecked() == False and self.date6.text() in self.desire_dates:
                self.desire_dates.remove(self.date6.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date7.isChecked() == False and self.date7.text() in self.desire_dates:
                self.desire_dates.remove(self.date7.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date8.isChecked() == False and self.date8.text() in self.desire_dates:
                self.desire_dates.remove(self.date8.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date9.isChecked() == False and self.date9.text() in self.desire_dates:
                self.desire_dates.remove(self.date9.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date10.isChecked() == False and self.date10.text() in self.desire_dates:
                self.desire_dates.remove(self.date10.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date11.isChecked() == False and self.date11.text() in self.desire_dates:
                self.desire_dates.remove(self.date11.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))

            if self.date12.isChecked() == False and self.date12.text() in self.desire_dates:
                self.desire_dates.remove(self.date12.text())
                self.desire_dates.sort(key=lambda date: datetime.strptime(date, '%d_%m_%Y'))


        def f_comp_params(self):
            """
                записывает параметры comp_period ; comp_point
                с проверкой численного параметра
                меняет текст в окне
            """
            symb=self.tedit_cust_comp.toPlainText()
            try:
                if symb.isnumeric():
                    self.comp_period=int(symb)
                    self.comp_point=', '
                    self.comp_point=self.comp_point.join(self.comp_items_list)
                    self.comparable_hint_lbl.setText( f"Условие сопоставимости:<br><b>{self.comp_period}</b> дат подряд наличие ненулевых данных в пункте <b>{self.comp_point}</b>")
                    #TODO: добавить hints при наведении на пункты экрана в QLabel
                    self.window_cust_comp.close()
                else:
                    raise ArithmeticError(
                        f'Ошибка ввода параметра: В условии "дат подряд" должно быть число, но получено {symb}')
            except ArithmeticError as msg_err:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(msg_err.args[0])
                msg.setWindowTitle("Error")
                msg.exec_()

        def del_comp_point(self):
            """
                Удаление строки с пунктом из списка сопоставимых
            """
            btn=self.sender()
            l = [n.objectName() for n in self.comp_btns_list]#список имен кнопок
            r=l.index(btn.objectName())
            self.comp_point_txt.removeRow(r)
            self.comp_btns_list.pop(r)
            self.comp_items_list.pop(r)


        def f_addpoint_compar(self):
            """
                Добавляет пункт сопоставимой выборки
            """
            tool_tip = self.cb_cust_comp.currentText()
            print(tool_tip)
            #если строка уже записана
            if tool_tip.split()[-1] in self.comp_items_list:
                return
            if tool_tip not in self.list_point_names:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(f"Неправильно введён параметр для выборки. Пожалуйста, проверьте корректность ввода.")
                msg.setWindowTitle("Info")
                msg.exec_()
                return
            self.comp_point_txt.insertRow(self.comp_point_txt.rowCount())
            # создаем item
            new_item = QtWidgets.QTableWidgetItem()
            new_item.setText(tool_tip.split()[-1])
            self.comp_point_txt.setItem(self.comp_point_txt.rowCount() - 1, 0, new_item)
            # в соседний столбец ставим кнопку переноса на другую ось
            new_btn = QPushButton()
            #ставим картинку для кнопки удаления пункта
            pixmapi = getattr(QStyle, "SP_TitleBarCloseButton")
            icon = self.style().standardIcon(pixmapi)
            new_btn.setIcon(icon)
            new_btn.setObjectName(f"{self.comp_point_txt.rowCount() - 1}")
            self.comp_btns_list.append(new_btn)
            self.comp_items_list.append(tool_tip.split()[-1])
            self.comp_point_txt.setCellWidget(self.comp_point_txt.rowCount() - 1, 1, new_btn)
            self.comp_btns_list[-1].clicked.connect(self.del_comp_point)
            # подсказка при наведении
            self.comp_point_txt.item(self.comp_point_txt.rowCount() - 1, 0).setToolTip(tool_tip)

        def cust_comp_func(self):
            self.comp_btns_list=[]
            """
            создает всплывающее окно с настройками периода и пункта сопоставимой выборки
            """
            #окно
            self.window_cust_comp = SecondWindow()
            """окно настройки сопоставимой выборки"""
            self.window_cust_comp.setFixedSize(400,400)
            self.vlayout=QtWidgets.QVBoxLayout()
            self.grbox_cust_comp=QtWidgets.QGroupBox(self.window_cust_comp)
            self.window_cust_comp.setCentralWidget(self.grbox_cust_comp)
            self.grbox_cust_comp.setLayout(self.vlayout)
            #верхняя группа окна(даты)
            self.hlayout1 = QtWidgets.QHBoxLayout()
            self.grbox1_cust_comp = QtWidgets.QGroupBox(self.grbox_cust_comp)
            self.grbox1_cust_comp.setLayout(self.hlayout1)
            self.vlayout.addWidget(self.grbox1_cust_comp)
            self.comp_param_hint=QtWidgets.QLabel(self.grbox1_cust_comp)
            self.comp_param_hint.setText("Дат подряд<br> (количество периодов с ненулевыми<br> значениями в пункте)")
            self.tedit_cust_comp=QtWidgets.QTextEdit(self.grbox1_cust_comp)
            """(TextEdit)ввод количества периодов для сопоставимой выборки"""
            self.tedit_cust_comp.setText(f'{self.comp_period}')
            self.tedit_cust_comp.setMaximumSize(QtCore.QSize(70, 30))
            self.hlayout1.addWidget(self.comp_param_hint)
            self.hlayout1.addWidget(self.tedit_cust_comp)
            #вторая группа: выбор пунктов
            self.grbox3_cust_comp = QtWidgets.QGroupBox(self.grbox_cust_comp)
            self.vlayout3 = QtWidgets.QVBoxLayout()
            self.grbox3_cust_comp.setLayout(self.vlayout3)
            self.vlayout.addWidget(self.grbox3_cust_comp)
            self.cb_cust_comp=ExtendedComboBox(self.grbox3_cust_comp)
            """(ExtendedComboBox)список пунктов в окне настройки сопоставимой выборки с поиском"""
            self.cb_cust_comp.addItems(self.list_point_names)
            self.addpoint_compar_pb=QtWidgets.QPushButton(self.grbox3_cust_comp)
            """кнопка добавления пункта в пункты сопоставимой выборки"""
            self.addpoint_compar_pb.setText("Добавить в список пунктов сопоставимости")
            self.addpoint_compar_pb.clicked.connect(self.f_addpoint_compar)
            self.comp_point_txt=QtWidgets.QTableWidget(self.grbox3_cust_comp)
            """(TableWidget)в стркое таблицы: пункт и кнопка удаления его"""
            self.comp_point_txt.insertColumn(0)
            self.comp_point_txt.insertColumn(1)
            for pn in self.comp_items_list:
                self.comp_point_txt.insertRow(self.comp_point_txt.rowCount())
                # создаем item
                new_item = QtWidgets.QTableWidgetItem()
                new_item.setText(pn)
                self.comp_point_txt.setItem(self.comp_point_txt.rowCount() - 1, 0, new_item)
                # в соседний столбец ставим кнопку удаления
                new_btn = QPushButton()
                pixmapi = getattr(QStyle, "SP_TitleBarCloseButton")
                icon = self.style().standardIcon(pixmapi)
                new_btn.setIcon(icon)
                new_btn.setObjectName(f"{self.comp_point_txt.rowCount() - 1}")
                self.comp_btns_list.append(new_btn)
                self.comp_point_txt.setCellWidget(self.comp_point_txt.rowCount() - 1, 1, new_btn)
                self.comp_btns_list[-1].clicked.connect(self.del_comp_point)
                # подсказка при наведении
                tool_tip=dict_num_name[pn.split('(')[1][:-1]]
                self.comp_point_txt.item(self.comp_point_txt.rowCount() - 1, 0).setToolTip(tool_tip)
            header = self.comp_point_txt.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.comp_point_txt.horizontalHeader().hide()
            self.comp_point_txt.verticalHeader().hide()
            self.comp_point_txt.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
            self.vlayout3.addWidget(self.cb_cust_comp)
            self.vlayout3.addWidget(self.addpoint_compar_pb)
            self.vlayout3.addWidget(self.comp_point_txt)
            #кнопка сохранения
            self.ok_pb_cust_comp=QtWidgets.QPushButton(self.grbox_cust_comp)
            """кнопка сохранения настроек сопоставимой выборки"""
            self.ok_pb_cust_comp.setText("ОК")
            self.ok_pb_cust_comp.clicked.connect(self.f_comp_params)
            self.vlayout.addWidget(self.ok_pb_cust_comp)
            self.window_cust_comp.show()

        def set_vis(self, *buttons):
            """
            функция настройки видимости объекта
            :param buttons:list of lists  [[указатель на кнопку, True(видимый)/False(невидимый)],[]]
            """
            for b in buttons:
                b[0].setVisible(b[1])

        def set_ind(self, *buttons):
            """
            функция установки текущего индекса у combobox
            :param buttons:list of lists [[кнопка, индекс],[]]
            """
            for b in buttons:
                b[0].setCurrentIndex(b[1])

        def set_ability(self, *buttons):
            """
            функция настройки возможности нажатия кнопки
            :param buttons: list of lists [[кнопка, True/False],[]]
            """
            for b in buttons:
                b[0].setEnabled(b[1])

        def set_check(self, *buttons):  # передаем list of lists [[кнопка, True/False]]
            """
            функция настройки отметки у кнопки(галочка)
            :param buttons: list of lists [[кнопка, True(поставить галочку)/False(убрать)],[]]
            """
            for b in buttons:
                b[0].setChecked(b[1])

        def set_param(self, *buttons):
            """
            функция настройки параметров(список опций в combobox)
            :param buttons: list of lists [[кнопка, [новые параметры]],[]]
            """
            for b in buttons:
                b[0].clear()
                b[0].addItems(b[1])

        def set_tab_vis(self, *buttons):
            """
            функция настройки видимости вкладок
            :param buttons: list of lists [[индекс вкладки, [True(видимая)/False(невидимая)]],[]]
            """
            for b in buttons:
                self.tabWidget.setTabVisible(b[0], b[1])

        def add_value(self):
            """
            (вкладка свой показатель)
            функция добавления в строку формулы цифры
            """
            btn = self.sender()
            # кнопки с цифрами
            digit_buttons = ('pb_0', 'pb_1', 'pb_2', 'pb_3', 'pb_4',
                             'pb_5', 'pb_6', 'pb_7', 'pb_8', 'pb_9')
            if btn.objectName() in digit_buttons:
                # если текущий ввод на данный момент пуст(т.е. там записан 0)
                if self.label_full_input.toPlainText() == '0':
                    self.label_full_input.setText(' ' + btn.text())
                # если в текущем вводе что-то уже написано, мы это оставляем в setText
                # при этом проверяем, что был написан оператор или число, а не функция
                else:
                    try:
                        symb = self.label_full_input.toPlainText().split()[-1]
                        if symb in ('+', '-', '/', '*','(') or symb[-1].isnumeric() or symb[-1] == '.':
                            self.label_full_input.setText(self.label_full_input.toPlainText() + btn.text())
                        else:
                            raise ArithmeticError(
                                f'Ошибка ввода показателя: не удалось добавить число к {symb}\nВозможно пропущен оператор(+-/*)')
                    except ArithmeticError as msg_err:
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Warning)
                        msg.setText(msg_err.args[0])
                        msg.setWindowTitle("Error")
                        msg.exec_()

        def add_bracket_op(self):
            """
            (вкладка свой показатель)
            функция добавления в строку формулы открывающейся скобки
            """
            btn = self.sender()
            if not self.label_full_input.toPlainText() == '0':
                self.label_full_input.setText(self.label_full_input.toPlainText() + btn.text() + ' ')
            else:
                self.label_full_input.setText(btn.text() + ' ')

        def add_bracket_close(self):
            """
            (вкладка свой показатель)
            функция добавления в строку формулы закрывающейся скобки
            """
            btn = self.sender()
            self.label_full_input.setText(self.label_full_input.toPlainText() + ' ' + btn.text() + ' ')

        def add_point(self):
            """
            (вкладка свой показатель)
            функция добавления в строку формулы точки
            """
            btn = self.sender()
            try:
                if btn.objectName() == 'pb_point':
                    # последний введенный символ
                    symb = self.label_full_input.toPlainText().split()[-1]
                    # если последний символ - число без ., то добавляем
                    if '.' not in symb and symb.isnumeric():
                        self.label_full_input.setText(self.label_full_input.toPlainText() + btn.text())
                    else:
                        raise ArithmeticError(f'Ошибка ввода показателя: не удалось добавить "." к {symb}')
            except ArithmeticError as msg_err:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(msg_err.args[0])
                msg.setWindowTitle("Error")
                msg.exec_()

        def add_funcpoint(self):
            """
            (вкладка свой показатель)
            функция добавления в текущий ввод функ(номер пункта)
            """
            # если в текущем вводе есть "(", то ее нужно сохранить
            # dict_name_num[self.point_name_comb.currentText()] - достаем из словаря dict_name_num(из read_data)
            # номер пункта по имени
            new = ''
            if self.label_full_input.toPlainText() == '0' or len(self.label_full_input.toPlainText().strip())==0:
                ch=self.point_name_comb.currentText().split('(')
                num=ch[-1]
                num=num.replace(')','').strip()
                del ch[-1]
                pname=new.join(ch).strip()
                self.label_full_input.setText(
                    self.func_group.checkedButton().text() + f"[{num}]" + ' ')
            else:  # проверяем, что пользователь пишет функцию после оператора, а не подряд с числом/другой функцией
                try:
                    symb = re.findall('[0-9\.]+|[+\-*^/]+|[А-Яа-я_0-9\.[]]+|[(]+|[)]]', self.label_full_input.toPlainText())[-1]
                    #list_of_char = [s.strip() for s in list_of_char]
                    #symb = self.label_full_input.toPlainText().split()[-1]
                    if symb in ('+', '-', '/', '*'):
                        ch = self.point_name_comb.currentText().split('(')
                        num = ch[-1]
                        num = num.replace(')', '').strip()
                        del ch[-1]
                        pname = new.join(ch).strip()
                        self.label_full_input.setText(
                            self.label_full_input.toPlainText() + self.func_group.checkedButton().text() + f"[{num}]" + ' ')
                    else:
                        raise ArithmeticError(
                            f'Ошибка ввода показателя: не удалось добавить функцию и пункт к {symb}\nВозможно пропущен оператор(+-/*)')
                except ArithmeticError as msg_err:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText(msg_err.args[0])
                    msg.setWindowTitle("Error")
                    msg.exec_()

        def f_check_hints(self):
            txt=self.label_full_input.toPlainText()
            #'[0-9\.]+|[+\-*^/]+|[А-Яа-я_]+|[\]]+|[\[]+|[(]+|[)]'
            l=re.findall('\[[0-9\.]+\]',txt)
            """список из пунктов для подсказок ['[5.7]', '[3]'] """
            new_hint_txt = '<h4>Имена пунктов формулы показателя</h4>'
            self.hints_label.setHtml(new_hint_txt)
            self.hinted_pointnums.clear()
            if not len(l)==0:
                for pn in l:
                    #проверка, что такой номер пункта существует
                    if pn[1:-1] in point_number_list:
                        if pn[1:-1] not in self.hinted_pointnums.keys():  # проверяем, что имя еще не было занесено в подсказку
                            new_hint_txt = new_hint_txt + f'<b>{pn[1:-1]}</b>' + '-' + dict_num_name[pn[1:-1]] + '<br>' + '\n'
                            # записываем num в hinted
                            self.hinted_pointnums[pn[1:-1]] = 1
                        else:  # увеличиваем счетчик упоминаний пункта
                            self.hinted_pointnums[pn[1:-1]] += 1
            self.hints_label.setHtml(new_hint_txt)

        def add_oper(self):
            """
            (вкладка свой показатель)
            функция записи в строку формулы операторае(+*-)
            :param num: номер пункта
            :param point_name_to_hint: название пункта
            """
            btn = self.sender()
            try:
                if self.label_full_input.toPlainText() == '0' and not btn.objectName() == 'pb_subtract':
                    raise ArithmeticError(
                        f'Ошибка ввода показателя: попытка поставить в начало выражения знак, отличный от "-" ')
                else:
                    self.label_full_input.setText(self.label_full_input.toPlainText() + ' ' + f'{btn.text()}' + ' ')
                    # переход на следующую строку, если превышает норм длину
                    if len(self.label_full_input.toPlainText()) > 80:
                        self.label_full_input.setText(self.label_full_input.toPlainText() + '\n')
            except ArithmeticError as msg_err:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(msg_err.args[0])
                msg.setWindowTitle("Error")
                msg.exec_()

        def clear_all(self):  # удалить все
            """
            (свой показатель)
            удалить всю формулу пользователя
            """
            # чистим подсказки, оставляем только заголовок
            self.hints_label.setHtml("<h4>Имена пунктов формулы показателя</h4>")
            # чистим полный ввод
            self.label_full_input.setText('0')
            # освобождаем списки названий, кот. надо записать в hint и тех, кот. уже записаны
            self.hinted_pointnums = {}

        def clear_entry(self):
            """
            (свой показатель)
            удалить последний ввод в формулу пользователя
            """
            # делим ввод на блоки символов
            inp = self.label_full_input.toPlainText().strip().split()
            new = ''
            # получаем последний введенный блок
            entry = inp[-1]
            # если это дробное число с точкой, убираем, чтобы функция могла проверить, что это число
            tmp = entry
            if '.' in entry:
                tmp = entry.replace('.', '')
            # если последний блок не функция с пунктом, то мы его просто удаляем
            if entry in ('+', '-', '*', '/','(',')') or tmp.isnumeric():
                txt = self.label_full_input.toPlainText()
                self.label_full_input.setText(new.join(txt.rsplit(entry,1)))
            else:  # надо удалить функцию
                txt = self.label_full_input.toPlainText()
                self.label_full_input.setText(new.join(txt.rsplit(entry,1)))
                # из entry достаем номер пункта
                entry = entry.split('[')[1]
                # убираем скобку )
                entry = entry.replace(']', '')
                # если подсказка к пункту встречалась только 1 раз, то ее удаляем
                if self.hinted_pointnums[entry] == 1:
                    self.hinted_pointnums.pop(entry)
                    new_hint_txt = '<h4>Имена пунктов формулы показателя</h4>'
                    for num in self.hinted_pointnums.keys():
                        new_hint_txt = new_hint_txt + '<br>' + f'<b>{num}</b>' + '-' + dict_num_name[num] + '<br>'
                    self.hints_label.setHtml(new_hint_txt)
            # проверяем, осталось ли еще выражение, иначе надо очистить и занулить текст
            if not self.label_full_input.toPlainText().strip():
                self.label_full_input.setText('0')

        def get_fin_choices(self):
            """
            функция для получения окончательных выборов пользователя
             - тип лк(гос инст/небанковская)
             - сортировка списка выбранных дат
            """
            # тип лк из комбобокса(гос институт/ небанковская и тд)
            self.desire_type_lk = self.get_lk_type(
                self.classprop_type_group.checkedButton().text())
            # сортировка списка дат------
            # переводим строки дат в формат дат питона
            for i in range(len(self.desire_dates)):
                self.desire_dates[i] = time.strptime(self.desire_dates[i], "%d_%m_%Y")
            # встроенная функция сортировки дат
            self.desire_dates = sorted(self.desire_dates)
            # переводим даты обратно в строчный формат
            for i in range(len(self.desire_dates)):
                self.desire_dates[i] = time.strftime("%d_%m_%Y", self.desire_dates[i])


        def get_comp_type(self, choice):
            """
            :param choice: все Лк/Ручной выбор/сопост выборка
            :return: число из ui_dict, кот. соответствует все Лк/Ручной выбор/сопост выборка
            """
            return comp_type_dict[choice]

        def get_param(self):
            """
            формируем tuple для выбранного готового параметра для расчета
            :return: [key (param, 'По данным МСФО'/'По данным ФСБУ'/
            'все продукты/финансовый лизинг/операционная аренда/'данные МСФО/данные ФСБУ''), True(ск год)/False]
            """
            # получаем выбранный тип отчета(эк инд/ данные мсфо и тд)
            choice = self.report_type_group.checkedButton().text()
            # для отчета типа экон инд
            # returns [key (param, 'По данным МСФО'/'По данным ФСБУ'), True(ск год)/False]
            if choice == 'Экономические индикаторы':
                return [(self.point_comb.currentText(), self.msfo_fsbu_group.checkedButton().text()),
                        self.sliding_check.isChecked()]
            # для отчета типа упр данные
            # returns [key (param, 'все продукты/финансовый лизинг/операционная аренда'), True(ск год)/False]
            if choice == 'Управленческие данные':
                return [(self.point_comb.currentText(), self.product_comb.currentText()),
                        self.sliding_check.isChecked()]
            # для отчета типа данные МСФО или ФСБУ
            # returns [key (param, 'данные МСФО/данные ФСБУ'), True(ск год)/False]
            if choice == 'Данные МСФО':
                return [(self.point_comb.currentText(), choice), self.sliding_check.isChecked()]
            if choice == 'Данные ФСБУ':
                return [(self.point_comb.currentText(), choice), self.sliding_check.isChecked()]

        def get_classprop_type(self):  # получаем тип классификации
            """
            :return: тип классификации

            ['lk_type', 'Классификатор ЦБ']

            ['lk_type2', 'Классификатор ОЛА']
            """
            if self.type_cb_rb.isChecked():
                return ['lk_type', 'Классификатор ЦБ']
            else:
                return ['lk_type2', 'Классификатор ОЛА']

        def get_lk_type(self, des_typing):
            """
            :param des_typing: выбранный тип классификации(цб/ола)
            :return: соответствующая классификация(баноквская гос...)
            """
            if self.type_cb_rb.text() == des_typing:
                return str(self.cb_comb.currentText())
            else:
                return str(self.ola_comb.currentText())

        def choose_calc(self):
            """
            вызывает функцию вычисления готового или своего показателя в зависимости от выбора
            :return:
            """
            if self.custom_param_rb.isChecked():
                self.calculate_custom()
            else:
                self.calculate_data()

        def calculate_custom(self):
            """
            функция вызова функции calculate из calculations.py для вычисления своего показателя
            """
            # убираем '\n'
            inp_str = self.label_full_input.toPlainText().replace('\n', ' ')
            for i in range(len(inp_str)-1):
                if inp_str[i] in ('(',')'):
                    if inp_str[i+1]==inp_str[i]:
                        t=inp_str[:i+1]+' '+inp_str[i+1:]
                        inp_str=t
            # print(f"inp={inp_str}")
            #list_of_char = inp_str.split()  # деление строки по пробелам
            #'[0-9.]+|[+\-*^/()]' - убирает слова
            #'[0-9\.]+|[+\-*^/]+|[А-Яа-я_(0-9\.)]+|[()]]'
            list_of_char= re.findall('[0-9\.]+|[+\-*^/]+|[А-Яа-я_]+|[\]]+|[\[]+|[(]+|[)]', inp_str )
            list_of_char = [s.strip() for s in list_of_char]
            self.get_fin_choices()  # получаем выборы пользователя по датам и типу лк
            # вызываем функцию вычислений из calculate.py
            # она возвращает текст результата, кот. мы выводим пользователю на экран
            self.tabWidget.setCurrentIndex(0)
            try:

                self.dates_state()

                if len(self.desire_dates) == 0:
                    raise ArithmeticError('Ошибка ввода: выберите хотя бы одну дату')
                res = calculate(**{'desire_dates_choice': self.desire_dates,
                                   # тип отчета(эконом.инд и тд)
                                   'desire_report_type': self.report_type_group.checkedButton().text(),
                                   # сопоставимая выборка/все ЛК/ручной выбор
                                   'desire_comparable': self.comp_type_group.checkedButton().text(),
                                   'comp_params': [self.comp_period,self.comp_items_list],
                                   # Классификация ЦБ или ОЛА
                                   'classprop_type': self.get_classprop_type(),  # is_ola
                                   # True(убрать гтлк)/False
                                   'is_not_gtlk': self.not_gtlk_check.isChecked(),
                                   # тип лк(гос институт/небанковская и тд)
                                   'desire_type_lk': self.desire_type_lk,
                                   # выбранный готовый параметр
                                   'desire_param': self.get_param(),
                                   # список имен лк, пустой если не ручной выбор
                                   'selection_names_list': self.selection_names_list,
                                   # выбран ли пункт свой показатель
                                   'is_custom': self.custom_param_rb.isChecked(),
                                   # список символов полного ввода пользовательского показателя
                                   'custom': list_of_char,
                                   # выбор не прирост/прирост год-к-году/прирост квартал-к-кварталу
                                   'custom_type': self.custom_type_group.checkedButton().text(),
                                   'full_form_txt': self.label_full_input.toPlainText(),
                                   # %s % self.hints_label.toHtml()
                                   'hints': "<style type='text/css'>h4{ font-size: 90%%;font-weight:200; font-family: Rubic; color: black;}</style><body>%s<body>" % self.hints_label.toHtml(), })
                self.result_label.setHtml(res[0])
                self.final_answer = res[1]
                self.final_dates = self.desire_dates.copy()
                self.dict_lk_excel = res[2].copy()
                self.concrete_lk_answ_excel = res[3].copy()
            except ArithmeticError as msg_err:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(msg_err.args[0])
                msg.setWindowTitle("Error")
                msg.exec_()

        def calculate_data(self):
            """
            функция вызова функции calculate из calculations.py для вычисления своего показателя
            """
            self.get_fin_choices()
            # вызов функции вычислений
            # вывод результата на главную вкладку
            try:
                self.dates_state()

                if len(self.desire_dates) == 0:
                    raise ArithmeticError('Ошибка ввода: выберите хотя бы одну дату')
                res = calculate(**{'desire_dates_choice': self.desire_dates,
                                   # тип отчета(эконом.инд и тд)
                                   'desire_report_type': self.report_type_group.checkedButton().text(),
                                   # сопоставимая выборка/все ЛК/ручной выбор
                                   'desire_comparable': self.comp_type_group.checkedButton().text(),
                                   'comp_params': [self.comp_period, self.comp_items_list],
                                   # Классификация ЦБ или ОЛА
                                   'classprop_type': self.get_classprop_type(),  # is_ola
                                   # True(убрать гтлк)/False
                                   'is_not_gtlk': self.not_gtlk_check.isChecked(),
                                   # тип лк(гос институт/небанковская и тд)
                                   'desire_type_lk': self.desire_type_lk,
                                   # выбранный готовый параметр
                                   'desire_param': self.get_param(),
                                   # список имен лк, пустой еслит не ручной выбор
                                   'selection_names_list': self.selection_names_list,
                                   # выбран ли пункт свой показатель
                                   'is_custom': self.custom_param_rb.isChecked()
                                   })
                self.result_label.setText(res[0])
                self.final_answer = res[1]
                self.final_dates = self.desire_dates.copy()
                self.dict_lk_excel = res[2].copy()
                self.concrete_lk_answ_excel = res[3].copy()
            except ArithmeticError as msg_err:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(msg_err.args[0])
                msg.setWindowTitle("Error")
                msg.exec_()

        def export_func(self):
            """
            экспорт результата расчета в эксель файл
            """
            try:
                if len(self.dict_lk_excel) ==0:
                    raise ArithmeticError('Ошибка ввода: для экспорта результата,получите значение, нажав кнопку рассчитать.Затем нажмите экспорт еще раз')
                if len(self.final_dates) == 0:
                    raise ArithmeticError('Ошибка ввода: выберите хотя бы одну дату')
                # экспорт даты и результата
                dict_to_exp = {'Дата': self.final_dates, 'Результат': self.final_answer}
                df_to_export = pd.DataFrame(dict_to_exp)
                new_time = datetime.now().strftime("%H_%M_%d_%m_%Y")
                df_to_export.to_excel('res_%s.xlsx' % (new_time), sheet_name='1')

                # экспорт списка ЛК с типами
                df_to_export = pd.DataFrame(self.dict_lk_excel)
                # строка с датой над ЛК
                header = pd.MultiIndex.from_product([[self.final_dates[-1]], list(df_to_export.columns)])
                tmp_df = pd.DataFrame(df_to_export.to_numpy(), None, columns=header)
                tmp_df.to_excel('lk_%s.xlsx' % (new_time), sheet_name='1')

                #экспорт значений с каждым ЛК выборки отдельно
                #orient='index' - ключи словаря- именя рядов
                df_to_export = pd.DataFrame.from_dict(self.concrete_lk_answ_excel,orient='index',columns=self.final_dates)
                df_to_export.to_excel('concrete_lk_%s.xlsx' % (new_time), sheet_name='1')

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(
                    f'Файл Результатов сохранен c именем res_{new_time}\nФайл ЛК с типами сохранен с именем lk_{new_time}\n'
                    f'Файл значений параметра каждого ЛК сохранен с именем concrete_lk_{new_time}')
                msg.setWindowTitle("Info")
                msg.exec_()
            except ArithmeticError as msg_err:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(msg_err.args[0])
                msg.setWindowTitle("Error")
                msg.exec_()

        def calculate_3lines_graph(self,d,**kwargs):
            """
            функция вычисления значений для построения графика с 3 прямыми
            :param d: даты для построения графиков
            :param kwargs:  **{'desire_param': [('NIM', 'По данным МСФО'), False],}
            :return: res=[Расчет1, Расчет2, Расчет3] для каждой прямой по расчету
            """
            res=[]
            if 'special' in kwargs and kwargs['special']:
                #случай когда 3 прямых не являются вариациями ('прочие собственники','кредитная организация','государственный институт')
                if kwargs['desire_param'][0][0]==('доля проблемных активов','все продукты'):
                    res.append(graph_roe(calculate(**{'desire_dates_choice': d,
                                            'desire_report_type': 'Экономические индикаторы',
                                            'desire_comparable': 'Сопоставимая выборка',
                                            'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                            'is_not_gtlk': False,
                                            'desire_type_lk': 'все ЛК',
                                            'desire_param': kwargs['desire_param'][0],
                                            'selection_names_list': [],
                                            'is_custom': False
                                            })[1]))
                    res.append(graph_roe(calculate(**{'desire_dates_choice': d,
                                            'desire_report_type': 'Экономические индикаторы',
                                            'desire_comparable': 'Сопоставимая выборка',
                                            'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                            'is_not_gtlk': True,
                                            'desire_type_lk': 'все ЛК',
                                            'desire_param': kwargs['desire_param'][0],
                                            'selection_names_list': [],
                                            'is_custom': False
                                            })[1]))
                for p in kwargs['desire_param']:
                    res.append(graph_roe(calculate(**{'desire_dates_choice': d,
                                      'desire_report_type': 'Экономические индикаторы',
                                      'desire_comparable': 'Сопоставимая выборка',
                                      'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                      'is_not_gtlk': False,
                                      'desire_type_lk': 'все ЛК',
                                      'desire_param': p,
                                      'selection_names_list': [],
                                      'is_custom': False
                                      })[1]))
            else:
                for i in ('прочие собственники','кредитная организация','государственный институт'):
                    res.append(graph_roe(calculate(**{'desire_dates_choice': d,
                                      'desire_report_type': 'Экономические индикаторы',
                                      'desire_comparable': 'Сопоставимая выборка',
                                      'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                      'is_not_gtlk': False,
                                      'desire_type_lk': i,
                                      'desire_param': kwargs['desire_param'],
                                      'selection_names_list': [],
                                      'is_custom': False
                                      })[1]))
            return res

        def calculate_bars_graph(self,d,**kwargs):
            """
            функция вычисления значений для построения гистограммы(столбики строются один поверх другого)
            :param d: даты для построения графиков
            :param kwargs: **{'desire_param': ([('новый бизнес', 'финансовый лизинг'), True],}
            :return: res=[Расчет1, Расчет2, Расчет3] для каждого столбика
            """
            res=[]
            #если переданы особые параметры (не гос, банк, час)
            if 'special' in kwargs and kwargs['special']:
                for p in kwargs['desire_param']:
                    res.append(graph_roe(calculate(**{'desire_dates_choice': d,
                                            'desire_report_type': 'Управленческие данные',
                                            'desire_comparable': 'Сопоставимая выборка',
                                            'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                            'is_not_gtlk': False,
                                            'desire_type_lk': 'все ЛК',
                                            'desire_param': p,
                                            'selection_names_list': [],
                                            'is_custom': False
                                            })[1]))

            else:
                for i in ('прочие собственники','кредитная организация','государственный институт'):
                    res.append(graph_roe(calculate(**{'desire_dates_choice': d,
                                          'desire_report_type': 'Управленческие данные',
                                          'desire_comparable': 'Сопоставимая выборка',
                                          'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                          'is_not_gtlk': False,
                                          'desire_type_lk': i,
                                          'desire_param': kwargs['desire_param'][0],
                                          'selection_names_list': [],
                                          'is_custom': False
                                          })[1]))
                #вычисляем темп прироста: год-к-году  'темп прироста нового бизнеса скользящий год (год к году)', 'все продукты'
                res.append(graph_roe(calculate(**{'desire_dates_choice': d,
                                        'desire_report_type': 'Управленческие данные',
                                        'desire_comparable': 'Сопоставимая выборка',
                                        'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                        'is_not_gtlk': False,
                                        'desire_type_lk': 'все ЛК',
                                        'desire_param': kwargs['desire_param'][1],
                                        'selection_names_list': [],
                                        'is_custom': False
                                        })[1]))
            return res

        def calculate_stacked_graph(self, d, **kwargs):
            """
            функция вычисления значений для построения гистограммы структуры фондирования(столбики строются один поверх другого)
            :param d: даты для построения графиков
            :param kwargs: **{'desire_param': ([('Кредиты полученные', 'Данные МСФО'), False],}
            :return: res=[Расчет1, Расчет2, Расчет3] для каждого столбика
            """
            res=[]
            for i in ( 'государственный институт','прочие собственники', 'кредитная организация',):
                sum=np.zeros(2)
                for p in kwargs['desire_param']:
                    res.append(graph_roe(calculate(**{'desire_dates_choice': d,#передаем первую и последнюю дату
                                        'desire_report_type': 'Управленческие данные',
                                        'desire_comparable': 'Сопоставимая выборка',
                                        'classprop_type': ['lk_type', 'Классификатор ЦБ'],
                                        'is_not_gtlk': False,
                                        'desire_type_lk': i,
                                        'desire_param': p,
                                        'selection_names_list': [],
                                        'is_custom': False
                                        })[1]))
                    sum+=res[-1]
                for j in range(1,4):
                    res[(-j)]=res[(-j)]*100/sum
            return res

        def dec_stacked_graph(self,**kwargs):
            """
            функция оформления гистограммы струтуры фондирования(один столбик строится на другом)
            :param kwargs: **{'title': 'название графика', 'x': [даты по оси х], 'y': [значения по оси у],
                                       'colors': [цвета столбиков],
                                       'labels': [подписи в легенде],
                                       'y_label': 'подпись оси у', 'type': 'bars',
                                       'layout': где расположен график(fin_layout_bars)}
            :return layout - разметка окна вмсете с построенным графиком
            """
            fig = Figure(figsize=(4, 3), dpi=100)
            canv = FigureCanvasQTAgg(fig)
            canv.axes = fig.add_subplot(211)
            width = 0.5
            spacing=np.array([0,0.7,1.4,2.1,2.8,3.5])
            start =0
            stop=9
            bottom = np.zeros(6)
            # проверяем на наличие отрицательных значений в первых трех блоках, заменяем на 0
            for i in range(3):
                for j in range(len(kwargs['y'][i])):
                    if kwargs['y'][i][j] < 0:
                        kwargs['y'][i][j] = 0
            for k in range(3):
                t_y=[]
                for j in range(start, stop, 3):
                    t_y.append(kwargs['y'][j][0])
                    t_y.append(kwargs['y'][j][1])
                canv.axes.bar(spacing, t_y, width, bottom=bottom, color=kwargs['colors'][k])
                bottom += t_y
                start += 1
                stop += 1
            canv.axes.set_frame_on(False)
            canv.axes.tick_params(left=False, bottom=False)  # убираем точки на осях
            canv.axes.grid(axis='y')  # линии по оси у ,labelpad=1
            canv.axes.tick_params(labelsize=7.0)
            spacing[1:]+=0.25*width
            canv.axes.set_xticks(spacing)
            canv.axes.set_xticklabels((kwargs['x'][0],kwargs['x'][1],kwargs['x'][0],kwargs['x'][1],kwargs['x'][0],kwargs['x'][1]))
            canv.axes.locator_params(axis='y', nbins=5)
            canv.axes.set_yticklabels((f'0%', f'25%', f'50%', '75%', '100%'))
            canv.axes.legend(kwargs['labels'], bbox_to_anchor=(0.5, 0.2), borderaxespad=-0.4, loc='lower center',
                             frameon=False,
                             bbox_transform=fig.transFigure, ncol=3, fontsize=7.0)
            canv.axes.set_title(kwargs['title'], fontsize=7.0)
            lbl_txt=('Гос ЛК','Частные ЛК', 'Банковские ЛК')
            for i,xpos in enumerate(canv.axes.get_xticks()):
                if i%2==0:
                    canv.axes.text(xpos+0.3,-40,lbl_txt[int(i/2)],ha='center')

            toolbar = NavigationToolbar(canv, self)
            layout = kwargs['layout']
            tool_graph_layout = QtWidgets.QVBoxLayout()
            tool_graph_layout.addWidget(toolbar)
            tool_graph_layout.addWidget(canv)

            layout.addLayout(tool_graph_layout, self.placement_y_bars, self.placement_x_bars)

            # меняем координаты следующего графика
            self.placement_x_bars += 1  # столбцы: расположение по строке
            if self.placement_x_bars >= 4:
                self.placement_y_bars += 1  # номер строки
                self.placement_x_bars = 0

            return layout

        def dec_graph_bars(self, **kwargs):
            """
            функция оформления гистограммы(один столбик строится на другом)
            :param kwargs: **{'title': 'название графика', 'x': [даты по оси х], 'y': [значения по оси у],
                                       'colors': [цвета столбиков],
                                       'labels': [подписи в легенде],
                                       'y_label': 'подпись оси у', 'type': 'bars',
                                       'layout': где расположен график(fin_layout_bars)}
            :return layout - разметка окна вмсете с построенным графиком
            """
            if kwargs['type']=='bars':
                fig = Figure(figsize=(4, 3), dpi=100)
                canv = FigureCanvasQTAgg(fig)
                canv.axes = fig.add_subplot(211)
                #вторая вертикальная ось справа
                canv.axes2 = canv.axes.twinx()
                #перевод в млрд
                kwargs['y'][0]=kwargs['y'][0]/1000
                kwargs['y'][1] = kwargs['y'][1] / 1000
                kwargs['y'][2] = kwargs['y'][2] / 1000
                #проверяем на наличие отрицательных значений в первых трех блоках, заменяем на 0
                for i in range(3):
                    for j in range(len(kwargs['y'][i])):
                        if kwargs['y'][i][j]<0:
                            kwargs['y'][i][j]=0
                b=[]
                #stacked
                bottom = 0
                width=0.5
                for i in range(3):
                    t_y = kwargs['y'][i]
                    #b1,=canv.axes.bar(kwargs['x'][i], kwargs['y'][j][i],width=0.5, color=kwargs['colors'][j], label=kwargs['labels'][j])
                    b1,=canv.axes.bar(kwargs['x'][0], t_y[0], width, bottom=bottom, color=kwargs['colors'][i],
                                  label=kwargs['labels'][i])
                    b.append(b1)
                    bottom += t_y[0]
                #other 4 bars
                for i in range(1,5):
                    bottom=0
                    for k in range(3):
                        t_y = kwargs['y'][k]
                        t_y = kwargs['y'][k]
                        canv.axes.bar(kwargs['x'][i], t_y[i], width, bottom=bottom, color=kwargs['colors'][k],label=kwargs['labels'][k])
                        bottom += t_y[i]

                # убираем рамку
                canv.axes.set_frame_on(False)
                canv.axes.tick_params(left=False, bottom=False)  # убираем точки на осях
                canv.axes.grid(axis='y')  # линии по оси у ,labelpad=1
                canv.axes.set_ylabel(kwargs['y_label'], fontsize=6.0,rotation=90,)
                canv.axes.tick_params(labelsize=7.0)

                #вторая ось
                line1, = canv.axes2.plot(kwargs['x'], kwargs['y'][3], color=kwargs['colors'][3],
                                         label=kwargs['labels'][3])
                b.append(line1)
                canv.axes2.set_frame_on(False)
                canv.axes2.tick_params(right=False)
                canv.axes2.set_ylabel('%',fontsize=6.0,rotation=90, )
                canv.axes2.tick_params(labelsize=7.0)
                # подпись последней точки графика
                canv.axes2.annotate(str(round(kwargs['y'][3][-1], 2)), xy=(kwargs['x'][-1], kwargs['y'][3][-1]))

                if 'special_lbl' in kwargs and kwargs['special_lbl']:
                    nc=1
                    space=-1
                else:
                    nc=2
                    space=-0.4
                names=kwargs['labels']
                canv.axes.legend(b,names,bbox_to_anchor=(0.5, 0.2),borderaxespad =space,loc='lower center', frameon=False,
                                 bbox_transform=fig.transFigure,ncol=nc, fontsize=7.0)
                canv.axes.set_title(kwargs['title'], fontsize=7.0)

                toolbar = NavigationToolbar(canv, self)
                layout = kwargs['layout']
                tool_graph_layout=QtWidgets.QVBoxLayout()
                tool_graph_layout.addWidget(toolbar)
                tool_graph_layout.addWidget(canv)

                layout.addLayout(tool_graph_layout,self.placement_y_bars, self.placement_x_bars)

                #меняем координаты следующего графика
                self.placement_x_bars += 1#столбцы: расположение по строке
                if self.placement_x_bars>=4:
                    self.placement_y_bars += 1#номер строки
                    self.placement_x_bars=0
            return layout

        def dec_graph_lines(self,**kwargs):
            """
            функция оформления графика прямых(один столбик строится на другом)
            :param kwargs: **{'title': 'название графика', 'x': [даты по оси х], 'y': [значения по оси у],
                                       'colors': [цвета прямых],
                                       'labels': [подписи в легенде],
                                       'y_label': 'подпись оси у', 'type': 'bars',
                                       'layout': где расположен график(fin_layout_lines)}
            :return layout - разметка окна вмсете с построенным графиком
            """
            if kwargs['type']=='lines':
                fig = Figure(figsize=(4, 3), dpi=100)
                canv = FigureCanvasQTAgg(fig)
                canv.axes = fig.add_subplot(211)
                if 'special' in kwargs and kwargs['special']:
                    if kwargs['title']=='ЧИЛ и Выручка':
                        # перевод в млрд
                        kwargs['y'][0] = kwargs['y'][0] / 1000
                        kwargs['y'][1] = kwargs['y'][1] / 1000
                        canv.axes.plot(kwargs['x'], kwargs['y'][0], color=kwargs['colors'][0], label=kwargs['labels'][0],linestyle='dashed',**{ 'marker': 'o'})
                        canv.axes.plot(kwargs['x'], kwargs['y'][1], color=kwargs['colors'][1], label=kwargs['labels'][1],linestyle='dashed', **{ 'marker': 'o'})
                        # подпись точек графика
                        for i in range(len(kwargs['x'])):
                            canv.axes.annotate(str(round(kwargs['y'][0][i], 2)), xy=(kwargs['x'][i], kwargs['y'][0][i]))
                            canv.axes.annotate(str(round(kwargs['y'][1][i], 2)), xy=(kwargs['x'][i], kwargs['y'][1][i]))
                    elif kwargs['title']== 'Доля проблемных активов в портфеле':
                        canv.axes.plot(kwargs['x'], kwargs['y'][0], color=kwargs['colors'][0], label=kwargs['labels'][0],**{ 'marker': 'o'})
                        canv.axes.plot(kwargs['x'], kwargs['y'][1], color=kwargs['colors'][1], label=kwargs['labels'][1],**{ 'marker': 'o'})
                        # подпись точек графика
                        for i in range(len(kwargs['x'])):
                            canv.axes.annotate(str(round(kwargs['y'][0][i], 2)), xy=(kwargs['x'][i], kwargs['y'][0][i]))
                            canv.axes.annotate(str(round(kwargs['y'][1][i], 2)), xy=(kwargs['x'][i], kwargs['y'][1][i]))
                else:
                    canv.axes.plot(kwargs['x'], kwargs['y'][0], color=kwargs['colors'][0], label=kwargs['labels'][0])
                    canv.axes.plot(kwargs['x'], kwargs['y'][1], color=kwargs['colors'][1], label=kwargs['labels'][1])
                    canv.axes.plot(kwargs['x'], kwargs['y'][2], color=kwargs['colors'][2], label=kwargs['labels'][2])
                    # подпись последней точки графика
                    canv.axes.annotate(str(round(kwargs['y'][0][-1], 2)), xy=(kwargs['x'][-1], kwargs['y'][0][-1]))
                    canv.axes.annotate(str(round(kwargs['y'][1][-1], 2)), xy=(kwargs['x'][-1], kwargs['y'][1][-1]))
                    canv.axes.annotate(str(round(kwargs['y'][2][-1], 2)), xy=(kwargs['x'][-1], kwargs['y'][2][-1]))

                # убираем рамку
                canv.axes.set_frame_on(False)
                canv.axes.tick_params(left=False, bottom=False)  # убираем точки на осях
                canv.axes.grid(axis='y')  # линии по оси у ,labelpad=1
                canv.axes.set_ylabel(kwargs['y_label'], fontsize=6.0,rotation=90,)
                canv.axes.tick_params(labelsize=7.0)
                canv.axes.legend(bbox_to_anchor=(0.5, 0),borderaxespad =-0.4,loc='lower center', frameon=False, bbox_transform=fig.transFigure,ncol=3, fontsize=7.0)
                canv.axes.set_title(kwargs['title'], fontsize=7.0)
                toolbar = NavigationToolbar(canv, self)
                layout = kwargs['layout']
                tool_graph_layout=QtWidgets.QVBoxLayout()
                tool_graph_layout.addWidget(toolbar)
                tool_graph_layout.addWidget(canv)

                layout.addLayout(tool_graph_layout,self.placement_y_lines, self.placement_x_lines)

                #меняем координаты следующего графика
                self.placement_x_lines += 1#столбцы: расположение по строке
                if self.placement_x_lines>=4:
                    self.placement_y_lines += 1#номер строки
                    self.placement_x_lines=0

            return layout

        def bars_widget(self,layout):
            """
            :param layout: разметка виджета с гистограммами
            :return: виджет с графиками гистограмм
            """
            widget_bars = QtWidgets.QWidget()
            widget_bars.resize(1021, 1000)
            widget_bars.setLayout(layout)
            return widget_bars

        def lines_widget(self,layout):
            """
            :param layout: разметка виджета с прямыми
            :return: виджет с графиками прямых
            """
            widget_lines = QtWidgets.QWidget()
            widget_lines.resize(1021, 1000)
            widget_lines.setLayout(layout)
            return widget_lines

        def build_graphs(self):
            """
            функция построения набора базовых графиков(гистограммы и прямые)
            """
            try:
                self.dates_state()

                # проверяем, что выбрано 5 или более дат
                if len(self.desire_dates) < 5:
                    raise ArithmeticError('Ошибка ввода пользователя: для построения графиков выберите не менее 5 дат')
                # сортируем выбранные пользователем даты
                self.get_fin_choices()
                graph_dates = self.desire_dates[-5:]#для вычисления результата
                #даты для вывода на график
                x = []
                for i in range(5):
                    x.append(graph_dates[i].replace('_', '.'))
                for i in range(5):
                    year=x[i].split('.')[2]
                    x[i]=x[i][:6]+year[2:]
                matplotlib.rc('font', size=7.0)
                #fin_layout = QtWidgets.QVBoxLayout(self.tab_main)
                fin_layout_lines = QtWidgets.QGridLayout()
                fin_layout_bars = QtWidgets.QGridLayout()
                #индексы расположения виджетов графиков в сетке окна
                self.placement_x_bars = 0
                self.placement_y_bars = 0
                self.placement_x_lines=0
                self.placement_y_lines=0

                #  новый бизнес: фин.лизинг
                y = self.calculate_bars_graph(graph_dates, **{'desire_param': ([('новый бизнес', 'финансовый лизинг'), True],
                         [('темп прироста нового бизнеса скользящий год (год к году)', 'финансовый лизинг'),True]) })
                self.dec_graph_bars(**{'title': 'Новый бизнес(фин. лизинг)', 'x': x, 'y': y, 'colors': ['#0485d1', '#FFCC00', 'red','black'],
                                  'labels': ['Частные ЛК', 'Банковские ЛК', 'Гос. ЛК', 'Темп прироста НБ(г./г.)'],
                                  'y_label': 'Млрд руб.', 'type': 'bars','layout': fin_layout_bars})

                #  новый бизнес: операционная аренда
                y = self.calculate_bars_graph(graph_dates,
                                              **{'desire_param': ([('новый бизнес', 'операционная аренда'), True],
                                                                  [(
                                                                   'темп прироста нового бизнеса скользящий год (год к году)',
                                                                   'операционная аренда'), True])})
                self.dec_graph_bars(**{'title': 'Новый бизнес(опер. аренда)', 'x': x, 'y': y,
                                       'colors': ['#0485d1', '#FFCC00', 'red', 'black'],
                                       'labels': ['Частные ЛК', 'Банковские ЛК', 'Гос. ЛК', 'Темп прироста НБ(г./г.)'],
                                       'y_label': 'Млрд руб.', 'type': 'bars', 'layout': fin_layout_bars})

                # портфель (фин.лизинг)
                y = self.calculate_bars_graph(graph_dates,
                                              **{'desire_param': ([('лизинговый портфель', 'финансовый лизинг'), False],
                                                                  [(
                                                                      'темп прироста лизингового портфеля (год к году)',
                                                                      'финансовый лизинг'), False])})
                self.dec_graph_bars(**{'title': 'Портфель (фин. лизинг)', 'x': x, 'y': y,
                                       'colors': ['#0485d1', '#FFCC00', 'red', 'black'],
                                       'labels': ['Частные ЛК', 'Банковские ЛК', 'Гос. ЛК', 'Темп прироста ЛП(г./г.)'],
                                       'y_label': 'Млрд руб.', 'type': 'bars', 'layout': fin_layout_bars})

                # портфель (опер. аренда)
                y = self.calculate_bars_graph(graph_dates,
                                              **{'desire_param': ([('лизинговый портфель', 'операционная аренда'), False],
                                                                  [(
                                                                      'темп прироста лизингового портфеля (год к году)',
                                                                      'операционная аренда'), False])})
                self.dec_graph_bars(**{'title': 'Портфель (опер. аренда)', 'x': x, 'y': y,
                                       'colors': ['#0485d1', '#FFCC00', 'red', 'black'],
                                       'labels': ['Частные ЛК', 'Банковские ЛК', 'Гос. ЛК', 'Темп прироста ЛП(г./г.)'],
                                       'y_label': 'Млрд руб.', 'type': 'bars', 'layout': fin_layout_bars})

                # Проблемные активы (фин.лизинг)
                y = self.calculate_bars_graph(graph_dates,
                                              **{'desire_param': ([('расторжения','финансовый лизинг'), False],
                                                                  [('реструктуризации', 'финансовый лизинг'), False],
                                                                  [('NPL90+', 'финансовый лизинг'), False],
                                                                  [('доля проблемных активов','финансовый лизинг'), False],),
                                                 'special': True})
                self.dec_graph_bars(**{'title': 'Проблемные активы (фин. лизинг)', 'x': x, 'y': y,
                                       'colors': ['#0485d1', '#FFCC00', 'red', 'black'],
                                       'labels': ['Расторгнутые договоры', 'Обслуживаемая реструктуризация', 'NPL 90+', 'Доля проблемных активов'],
                                       'y_label': 'Млрд руб.', 'type': 'bars', 'layout': fin_layout_bars,'special_lbl': True})

                # Проблемные активы (опер.аренда)
                y = self.calculate_bars_graph(graph_dates,
                                              **{'desire_param': ([('расторжения','операционная аренда'), False],
                                                                  [('реструктуризации', 'операционная аренда'), False],
                                                                  [('NPL90+', 'операционная аренда'), False],
                                                                  [('доля проблемных активов','операционная аренда'), False],),
                                                 'special': True})
                self.dec_graph_bars(**{'title': 'Проблемные активы (опер.аренда)', 'x': x, 'y': y,
                                       'colors': ['#0485d1', '#FFCC00', 'red', 'black'],
                                       'labels': ['Расторгнутые договоры', 'Обслуживаемая реструктуризация', 'NPL 90+', 'Доля проблемных активов'],
                                       'y_label': 'Млрд руб.', 'type': 'bars', 'layout': fin_layout_bars, 'special_lbl': True})

                #структура фондирования
                y=self.calculate_stacked_graph([graph_dates[0],graph_dates[-1]],
                                              **{'desire_param': ([('Кредиты полученные', 'Данные МСФО'), False],
                                                                  [('Займы полученные', 'Данные МСФО'), False],
                                                                  [('Выпущенные долговые ценные бумаги', 'Данные МСФО'), False],),})
                self.dec_stacked_graph(**{'title': 'Структура фондирования', 'x': [x[0],x[-1]], 'y': y,
                                       'colors': ['#0485d1','red', '#FFCC00'],
                                       'labels': ['Кредиты', 'Займы', 'Облигации'],
                                       'y_label': '%', 'type': 'bars', 'layout': fin_layout_bars})
                # ROE
                y=self.calculate_3lines_graph(graph_dates,**{'desire_param': [('ROE', 'По данным МСФО'), False],})
                self.dec_graph_lines(**{'title':'ROE','x':x,'y':y,'colors':['#0485d1','#FFCC00','red'],
                                  'labels':['Частные ЛК','Банковские ЛК','Гос. ЛК'],'y_label':'%', 'type': 'lines',
                                  'layout': fin_layout_lines})
                #NIM
                y = self.calculate_3lines_graph(graph_dates, **{'desire_param': [('NIM', 'По данным МСФО'), False], })
                self.dec_graph_lines(**{'title': 'NIM', 'x': x, 'y': y, 'colors': ['#0485d1', '#FFCC00', 'red'],
                                  'labels': ['Частные ЛК', 'Банковские ЛК', 'Гос. ЛК'], 'y_label': '%', 'type': 'lines',
                                  'layout': fin_layout_lines})
                # CIR
                y = self.calculate_3lines_graph(graph_dates, **{'desire_param': [('CIR', 'По данным МСФО'), False], })
                self.dec_graph_lines(**{'title': 'CIR', 'x': x, 'y': y, 'colors': ['#0485d1', '#FFCC00', 'red'],
                                  'labels': ['Частные ЛК', 'Банковские ЛК', 'Гос. ЛК'], 'y_label': '%', 'type': 'lines',
                                  'layout': fin_layout_lines})
                # стоимость фондирования
                y = self.calculate_3lines_graph(graph_dates, **{'desire_param': [('стоимость фондирования', 'По данным МСФО'), False], })
                self.dec_graph_lines(**{'title': 'стоимость фондирования', 'x': x, 'y': y, 'colors': ['#0485d1', '#FFCC00', 'red'],
                                  'labels': ['Частные ЛК', 'Банковские ЛК', 'Гос. ЛК'], 'y_label': '%', 'type': 'lines',
                                  'layout': fin_layout_lines})

                #финансовый рычаг(leverage эк инд)
                y = self.calculate_3lines_graph(graph_dates,
                                                **{'desire_param': [('Leverage', 'По данным МСФО'), False], })
                self.dec_graph_lines(
                    **{'title': 'финансовый рычаг', 'x': x, 'y': y, 'colors': ['#0485d1', '#FFCC00', 'red'],
                       'labels': ['Частные ЛК', 'Банковские ЛК', 'Гос. ЛК'], 'y_label': '%', 'type': 'lines',
                       'layout': fin_layout_lines})

                #ЧИЛ и выручка (п. 5.4 и 5.31)
                y = self.calculate_3lines_graph(graph_dates,
                                                **{'desire_param': ([('ЧИЛ', 'По данным МСФО'), False],
                                                                    [('Выручка', 'По данным МСФО'), True]),'special':True, })
                self.dec_graph_lines(
                    **{'title': 'ЧИЛ и Выручка', 'x': x, 'y': y, 'colors': ['#0485d1', 'red'],
                       'labels': ['ЧИЛ', 'Выручка(скользящий год)'], 'y_label': 'Млрд руб.', 'type': 'lines',
                       'layout': fin_layout_lines,'special':True,})

                #доля проблемных активов в портфеле
                y = self.calculate_3lines_graph(graph_dates,
                                                **{'desire_param': ([('доля проблемных активов', 'все продукты'), False],
                                                                    [('доля проблемных активов', 'все продукты'), False]),
                                                   'special': True, })
                self.dec_graph_lines(
                    **{'title': 'Доля проблемных активов в портфеле', 'x': x, 'y': y, 'colors': [ 'red','#0485d1'],
                       'labels': ['Доля проблемных активов с ГТЛК', 'Доля проблемных активов без ГТЛК'], 'y_label': '%', 'type': 'lines',
                       'layout': fin_layout_lines, 'special': True, })

                self.setCentralWidget(self.bars_widget(fin_layout_bars))
                self.SW = SecondWindow()
                self.SW.setCentralWidget(self.lines_widget(fin_layout_lines))
                self.SW.show()
                self.show()
            except ArithmeticError as msg_err:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(msg_err.args[0])
                msg.setWindowTitle("Error")
                msg.exec_()

        def call_valid(self):
            """
            функция вызова метода валидирования данных и записи его результатов в файл
            """
            vd = validate_data()
            if not len(vd) == 0:  # если найдены проблемы с таблцей
                file = open('not_valid_data.txt', 'w')
                v_txt = ''
                for k in vd.keys():
                    v_txt = v_txt + '\n' + f'--------{k}---------'
                    if 'pos' in vd[k]:
                        kn = 'pos'
                        for v in vd[k][kn]:
                            sign = '>=0'
                            v_txt = v_txt + '\n' + '(ИСПРАВЛЕНО)Правило знаков:' + f'требуемый знак {sign}'
                            v_txt = v_txt + '\n' + f'дата: {v[0]} ; пункт {v[1]}'
                    if 'otr' in vd[k]:
                        kn = 'otr'
                        for v in vd[k][kn]:
                            sign = '<0'
                            v_txt = v_txt + '\n' + '(ИСПРАВЛЕНО)Правило знаков:' + f'требуемый знак {sign}'
                            v_txt = v_txt + '\n' + f'дата: {v[0]} ; пункт {v[1]}'
                    if 'compare' in vd[k]:
                        kn = 'compare'
                        for v in vd[k][kn]:
                            v_txt = v_txt + '\n' + 'Правило сравнения:' + (f'дата: {v[0]}  ;  '
                                                                           f'пункт: {v[1][0]}  НЕ <  '
                                                                           f'   {v[1][1]}')
                    if 'compare_abs' in vd[k]:
                        kn = 'compare_abs'
                        for v in vd[k][kn]:
                            v_txt = v_txt + '\n' + 'Правило сравнения:' + (f'дата: {v[0]}  ;  '
                                                                           f'пункт: {v[1][0]}  по модулю НЕ <  '
                                                                           f'   {v[1][1]}')
                    if 'eq' in vd[k]:
                        kn = 'eq'
                        for v in vd[k][kn]:
                            v_txt = v_txt + '\n' + 'Правило сравнения:' + (f'дата: {v[0]}  ;  '
                                                                           f'пункт: {v[1][0]}  НЕ =  сумме пунктов(пункту)'
                                                                           f'   {v[1][1]}')
                full_df.to_excel("fix.xlsx")
                file.write(v_txt)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(f'Проведена валидация,найдены ошибки результаты сохранены в файл; исправленная таблица сохранена как fix.xlsx')
                msg.setWindowTitle("Error")
                msg.exec_()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText(f'Проведена валидация,ошибок нет')
                msg.setWindowTitle("Info")
                msg.exec_()

        def f_collect_data(self, file_names):
            try:
                # собираем номера ОГРН из экселя всех данных и проверяем на наличие в сданных анкетах
                old_df = pd.read_excel('TS_2_upload_data_full_final_final.xlsm', header=0)
                ogrn_list = old_df['lk_ogrn'].drop_duplicates().values
                wrong_numbers=[]
                wrong_dates=[]
                wrong_files=[]
                for form in file_names:  # идем по всем сданным новым анкетам
                    try:
                        tmp_df = pd.read_excel(form, sheet_name='Raw4')  # читаем эксель, по дефолту это первая страница файла
                        org_num=tmp_df['ОГРН'].iloc[1]#находим часть с номером ОГРН
                        if org_num not in ogrn_list:
                            wrong_numbers.append((org_num, form))
                    except Exception as e:
                        wrong_files.append(form)
                if len(wrong_files)>0:
                    txt = 'не удалось прочитать файлы excel<br>'
                    for el in wrong_files:
                        txt = txt + f'<b>анкеты по адресу</b> {el}<br>'
                    raise ArithmeticError(txt)
                if len(wrong_numbers)>0:
                    txt='не удалось найти соответствующий ОГРН в финальном файле excel\n'
                    for el in wrong_numbers:
                        txt=txt+f'ОГРН: {el[0]} для анкеты по адресу {el[1]}\n'
                    raise ArithmeticError(txt)
                else:#если все нормально, продолжаем формирование новых данных
                    last_date=old_df.columns.values.tolist()[-1]
                    formated_last_date=time.strptime(last_date, "%d_%m_%Y")
                    expected_date= datetime.fromtimestamp(time.mktime(formated_last_date))+relativedelta(months=3)
                    for form in file_names:
                        tmp_df = pd.read_excel(form, sheet_name='Raw4')
                        d=tmp_df.columns.values.tolist()[3]
                        if not expected_date == d:
                            wrong_dates.append((d, form))
                    if len(wrong_dates) > 0:
                        txt = 'В некоторых анкетах дата не совпадает с необходимой\n'
                        for el in wrong_dates:
                            txt = txt + f'Дата: {el[0]} для анкеты по адресу {el[1]}\n'
                        raise ArithmeticError(txt)
                #формирование (закончена проверка дат и номеров ОГРН)
                if len(wrong_numbers)==0 and len(wrong_dates)==0:
                    #добавляем новый столбик

                    tmp_df = pd.read_excel(file_names[0], sheet_name='Raw4')
                    cn = tmp_df.columns.values.tolist()
                    d_cur = cn[3].strftime("%d_%m_%Y")
                    d_prev = cn[2].strftime("%d_%m_%Y")
                    old_df[d_cur]=np.nan
                    col_num=len(old_df.columns.values.tolist())-1
                    for form in file_names:
                        #берем два столбика значений из эксель
                        tmp_df = pd.read_excel(form, sheet_name='Raw4')

                        cn = tmp_df.columns.values.tolist()
                        ogrn=tmp_df['ОГРН'].iloc[1]
                        new_col_prev=tmp_df[cn[2]].tolist()
                        """новые значения для предыдущего периода"""
                        new_col_cur=tmp_df[cn[3]].tolist()
                        """новые значения для текущего периода"""
                        # на первый столбик применяем формулу сравнения
                        d_prev=cn[2].strftime("%d_%m_%Y")
                        ind=old_df.loc[old_df['lk_ogrn']==ogrn,d_prev].index.tolist()
                        for i in range(len(new_col_prev)):
                            if not old_df.loc[old_df['lk_ogrn']==ogrn,d_prev].iloc[i]==new_col_prev[i] and not new_col_prev==0:
                                #записываем новое значение в дф
                                #old_df.loc[old_df['lk_ogrn']==ogrn, d].iloc[i]=new_col_prev[i]
                                old_df.iloc[(ind[i],col_num-1)]=new_col_prev[i]

                        #записываем стобик текущей даты
                        for i in range(len(new_col_cur)):
                            #old_df.loc[old_df['lk_ogrn'] == ogrn, d]=new_col_cur
                            old_df.iloc[(ind[i], col_num)]=new_col_cur[i]
                    #переделать слова в цифры
                    dates_list.append(d_cur)
                    for d in dates_list:
                        old_df[d] = pd.to_numeric(old_df[d], errors='coerce')
                        old_df[d]=old_df[d].fillna(0)
                    #ФОРМУЛА 1
                    lkn=old_df['lk_name'].drop_duplicates()
                    for company in lkn:
                        for pn in ("4.78", "4.79", "4.80", "4.81", "4.82", "4.83", "5.57", "5.58",
                                   "5.59", "5.60", "5.61", "5.62"):
                            ind = old_df.loc[
                                (old_df['lk_name'] == company) & (old_df['point_number'] == pn), d_prev].index.tolist()
                            #прошлая дата
                            if old_df.iloc[(ind[0], col_num-1)]<0:
                                old_df.iloc[(ind[0], col_num-1)]*=(-1)
                            ind = old_df.loc[
                                (old_df['lk_name'] == company) & (old_df['point_number'] == pn), d_cur].index.tolist()
                            if old_df.iloc[(ind[0], col_num)]<0:
                                old_df.iloc[(ind[0], col_num)]*=(-1)
                    old_df.to_excel("updated_data.xlsm")
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Файл с новыми данными сохранен под именем updated_data.xlsm."
                                "<br>Чтобы использовать его, переименуйте файл как старую версию и перезагрузите программу")
                    msg.setWindowTitle("Info")
                    msg.exec_()
            except ArithmeticError as msg_err:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText(msg_err.args[0])
                msg.setWindowTitle("Error")
                msg.exec_()

        def get_file_data(self):
            dlg = QFileDialog()
            dlg.setFileMode(QFileDialog.ExistingFiles)
            dlg.setNameFilter("All excel files ( *xlsx)")#*.xsl *.xlsm
            #filenames = QStringList()
            if dlg.exec_():
                filenames = dlg.selectedFiles()
                #функция сбора материалов для анкет
                self.f_collect_data(filenames)
except Exception as e:
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(f'Неизвестная ошибка: {e}')
    msg.setWindowTitle("Error")
    msg.exec_()

class SecondWindow(QMainWindow):
    def __init__(self):
        super(SecondWindow, self).__init__()
        lbl = QLabel('', self)

class ExtendedComboBox(QComboBox):
    """
    класс combobox-ов с функцией поиска названия при вводе
    """
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setEditable(True)
        # add a filter model to filter matching items
        self.pFilterModel = QtCore.QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())
        # add a completer, which uses the filter model
        self.completer = QCompleter(self.pFilterModel, self)
        # always show all (filtered) completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)
        # connect signals
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    def on_completer_activated(self, text):
        """
        on selection of an item from the completer, select the corresponding item from combobox
        :param text: введенный для поиска в комбобоксе текст
        :return:
        """
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))


    # on model change, update the models of the filter and completer as well
    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)


    # on model column change, update the model column of the filter and completer as well
    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)