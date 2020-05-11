from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_main_window(object):
    def setupUi(self, main_window):
        main_window.resize(1018, 623)

        self.central_widget = QtWidgets.QWidget(main_window)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.central_widget)
        self.header_hl = QtWidgets.QHBoxLayout()
        self.header_hl.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.aspect_label = QtWidgets.QLabel(self.central_widget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.aspect_label.sizePolicy().hasHeightForWidth())

        self.aspect_label.setSizePolicy(sizePolicy)
        self.aspect_label.setMaximumSize(QtCore.QSize(100, 16777215))

        font = QtGui.QFont()
        font.setPointSize(16)

        self.aspect_label.setFont(font)

        self.header_hl.addWidget(self.aspect_label)

        self.aspects_combo_box = QtWidgets.QComboBox(self.central_widget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.aspects_combo_box.sizePolicy().hasHeightForWidth())

        self.aspects_combo_box.setSizePolicy(sizePolicy)
        self.aspects_combo_box.setMinimumSize(QtCore.QSize(0, 0))

        font = QtGui.QFont()
        font.setPointSize(10)

        self.aspects_combo_box.setFont(font)
        # self.aspects_combo_box.addItem("")
        # self.aspects_combo_box.addItem("")
        # self.aspects_combo_box.addItem("")

        self.header_hl.addWidget(self.aspects_combo_box)

        spacerItem = QtWidgets.QSpacerItem(50, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.header_hl.addItem(spacerItem)

        self.settings_btn = QtWidgets.QPushButton(self.central_widget)

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)

        sizePolicy.setHeightForWidth(self.settings_btn.sizePolicy().hasHeightForWidth())
        self.settings_btn.setSizePolicy(sizePolicy)

        self.header_hl.addWidget(self.settings_btn)
        self.verticalLayout.addLayout(self.header_hl)

        self.status_hl = QtWidgets.QHBoxLayout()
        self.status_hl.setObjectName("status_hl")
        self.status_label = QtWidgets.QLabel()
        self.status_hl.addWidget(self.status_label)
        self.progress_bar = QtWidgets.QProgressBar()
        self.status_hl.addWidget(self.progress_bar)
        self.verticalLayout.addLayout(self.status_hl)

        self.polarity_hl = QtWidgets.QHBoxLayout()

        self.positive_rb = QtWidgets.QRadioButton(self.central_widget)

        font = QtGui.QFont()
        font.setPointSize(12)

        self.positive_rb.polarity = 'positive'
        self.positive_rb.setFont(font)
        self.positive_rb.setChecked(True)
        self.positive_rb.setObjectName("positive_rb")
        self.polarity_hl.addWidget(self.positive_rb, 0, QtCore.Qt.AlignHCenter)

        self.negative_rb = QtWidgets.QRadioButton(self.central_widget)

        font = QtGui.QFont()
        font.setPointSize(12)

        self.negative_rb.polarity = 'negative'
        self.negative_rb.setFont(font)
        self.negative_rb.setObjectName("negative_rb")
        self.polarity_hl.addWidget(self.negative_rb, 0, QtCore.Qt.AlignHCenter)

        self.neutral_rb = QtWidgets.QRadioButton(self.central_widget)

        font = QtGui.QFont()
        font.setPointSize(12)

        self.neutral_rb.polarity = 'neutral'
        self.neutral_rb.setFont(font)
        self.neutral_rb.setObjectName("neutral_rb")
        self.polarity_hl.addWidget(self.neutral_rb, 0, QtCore.Qt.AlignHCenter)

        #
        self.button_group = QtWidgets.QButtonGroup()
        self.button_group.addButton(self.positive_rb)
        self.button_group.addButton(self.negative_rb)
        self.button_group.addButton(self.neutral_rb)

        #

        self.verticalLayout.addLayout(self.polarity_hl)

        self.table_widget = QtWidgets.QTableWidget(self.central_widget)
        self.table_widget.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.table_widget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_widget.setShowGrid(True)
        self.table_widget.setGridStyle(QtCore.Qt.SolidLine)
        self.table_widget.setWordWrap(True)
        self.table_widget.setRowCount(2)
        self.table_widget.setColumnCount(5)
        self.table_widget.setObjectName("table_widget")

        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setVerticalHeaderItem(0, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setVerticalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_widget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(0, 0, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(0, 1, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(0, 2, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(0, 3, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(0, 4, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(1, 0, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(1, 1, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(1, 2, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(1, 3, item)
        # item = QtWidgets.QTableWidgetItem()
        # self.table_widget.setItem(1, 4, item)

        self.table_widget.horizontalHeader().setVisible(True)
        # self.table_widget.horizontalHeader().setCascadingSectionResizes(True)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        # self.table_widget.verticalHeader().setCascadingSectionResizes(True)
        self.table_widget.verticalHeader().setDefaultSectionSize(30)

        self.table_widget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

        self.verticalLayout.addWidget(self.table_widget)
        main_window.setCentralWidget(self.central_widget)

        self.retranslateUi(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def retranslateUi(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "MainWindow"))
        self.aspect_label.setText(_translate("main_window", "Аспект"))
        # self.aspects_combo_box.setItemText(0, _translate("main_window", "Дизайн"))
        # self.aspects_combo_box.setItemText(1, _translate("main_window", "Почта"))
        # self.aspects_combo_box.setItemText(2, _translate("main_window", "Приложение"))
        self.settings_btn.setText(_translate("main_window", "Настройки"))
        self.positive_rb.setText(_translate("main_window", "Positive"))
        self.negative_rb.setText(_translate("main_window", "Negative"))
        self.neutral_rb.setText(_translate("main_window", "Neutral"))
        self.table_widget.setSortingEnabled(True)

        self.status_label.setText(_translate("main_window", "Статус"))
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.status_label.hide()


        # item = self.table_widget.verticalHeaderItem(0)
        # item.setText(_translate("main_window", "1"))
        # item = self.table_widget.verticalHeaderItem(1)
        # item.setText(_translate("main_window", "2"))
        item = self.table_widget.horizontalHeaderItem(0)
        item.setText(_translate("main_window", "Автор"))
        item = self.table_widget.horizontalHeaderItem(1)
        item.setText(_translate("main_window", "Оценка"))
        item = self.table_widget.horizontalHeaderItem(2)
        item.setText(_translate("main_window", "Дата"))
        item = self.table_widget.horizontalHeaderItem(3)
        item.setText(_translate("main_window", "Одобрение"))
        item = self.table_widget.horizontalHeaderItem(4)
        item.setText(_translate("main_window", "Текст"))
        __sortingEnabled = self.table_widget.isSortingEnabled()
        self.table_widget.setSortingEnabled(False)
        # item = self.table_widget.item(0, 0)
        # item.setText(_translate("main_window", "Евгений Николаич"))
        # item = self.table_widget.item(0, 1)
        # item.setText(_translate("main_window", "4"))
        # item = self.table_widget.item(0, 2)
        # item.setText(_translate("main_window", "2020-03-19"))
        # item = self.table_widget.item(0, 3)
        # item.setText(_translate("main_window", "14"))
        # item = self.table_widget.item(0, 4)
        # item.setText(_translate("main_window", "Хорошее приложение, изменяют отзыв с 3 на 4 звёздочки на данном этапе после устранения недостатков. НО! Было бы круто, если бы приложение умело само сжимать файлы перед отправкой, а именно фото как у конкурента...Ну типа режим сжатия: маленький, средний и большой с указанием объема. Ну очень нужная функция!"))
        # item = self.table_widget.item(1, 0)
        # item.setText(_translate("main_window", "Pauluccio Russo"))
        # item = self.table_widget.item(1, 1)
        # item.setText(_translate("main_window", "4"))
        # item = self.table_widget.item(1, 2)
        # item.setText(_translate("main_window", "2020-03-16"))
        # item = self.table_widget.item(1, 3)
        # item.setText(_translate("main_window", "21"))
        # item = self.table_widget.item(1, 4)
        # item.setText(_translate("main_window", "Нет настройки: загружать письмо полностью/или только заголовок. Нет настройки периодичности проверки новых писем. Нет выбора протокола (pop3, imap). Нет числового обозначения количества новых писем. Управление жестами не всегда удобно (например в транспорте) и не интуитивно (imho кнопки лучше). Тема письма почему-то над адресатом. Кнопка в виде лампочки (когда читаешь письмо), меняющая фон светлый/тёмный, тоже по моему лишняя. Внутри письма аватарка адресата отображается, а снаружи нет."))
        self.table_widget.setSortingEnabled(__sortingEnabled)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = Ui_main_window()
    ui.setupUi(main_window)
    main_window.show()
    sys.exit(app.exec_())
