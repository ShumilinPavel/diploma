from PyQt5.QtWidgets import QMainWindow
import gui.layouts.settings as settings
from MongoDb import MongoDb
import threading


class SettingsWindow(QMainWindow, settings.Ui_SettingsMainWindow):
    def __init__(self, main_window, mongo: MongoDb):
        super().__init__()
        self.setupUi(self)
        self.mongo = mongo
        self.main_window = main_window
        self.cur_app_label = self.main_window.applications_combo_box.currentText()
        self.__fill_line_edits()
        self.__setup_signals()

    def __fill_line_edits(self):
        self.__fill_minsup()
        self.__fill_window()

    def __fill_minsup(self):
        doc = self.mongo.load_minimum_support(self.cur_app_label)
        minsup = doc['minsup']
        self.minsup_line_edit.setText(str(minsup))

    def __fill_window(self):
        doc = self.mongo.load_window_radius(self.cur_app_label)
        window_radius = doc['window']
        self.window_line_edit.setText(str(window_radius))

    def __setup_signals(self):
        self.cancel_btn.clicked.connect(self.__on_cancel_click)
        self.submit_btn.clicked.connect(self.__on_submit_click)

    def __on_cancel_click(self):
        self.close()

    def __on_submit_click(self):
        minsup = self.minsup_line_edit.text()
        window_radius = self.window_line_edit.text()
        self.mongo.update_settings(self.cur_app_label, minsup, window_radius)
        t1 = threading.Thread(target=self.main_window.process_with_new_settings)
        t1.start()
        self.close()
        t1.join()
