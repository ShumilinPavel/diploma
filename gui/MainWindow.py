import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
import gui.layouts.manual_ui as manual_ui

import configparser
from MongoDb import MongoDb
from aspect_extraction.AspectsExtractor import AspectsExtractor
from sentiment_analysis.OpinionsExtractor import OpinionsExtractor
from sentiment_analysis.SentimentAnalyzer import SentimentAnalyzer

from gui.SettingsWindow import SettingsWindow


class MainWindow(QMainWindow, manual_ui.Ui_main_window):
    def __init__(self, application_name, config_file_name):
        super().__init__()
        self.setupUi(self)

        self.__setup_signals()

        self.__parse_config(config_file_name, application_name)
        self.mongo = MongoDb(self.collection_name_prefix)

        self.aspects_extractor = AspectsExtractor(application_name, config_file_name)
        self.opinions_extractor = OpinionsExtractor(application_name, config_file_name)
        self.sentiment_analyzer = SentimentAnalyzer(application_name, config_file_name)

        self.__reset_to_start()

    def __parse_config(self, config_file_name, application_name):
        self.config = configparser.ConfigParser()
        self.config.read(config_file_name)
        self.collection_name_prefix = self.config[application_name]['collection_name_prefix']

    def __reset_to_start(self):
        self.fill_aspects()
        self.fill_table(self.aspects_combo_box.currentText(), self.button_group.checkedButton().polarity)

    def __setup_signals(self):
        self.aspects_combo_box.currentTextChanged.connect(self.on_combobox_func)
        self.button_group.buttonClicked.connect(self._on_radio_button_clicked)
        self.settings_btn.clicked.connect(self.__on_settings_button_click)

    def on_combobox_func(self, selected_aspect):
        selected_polarity = self.button_group.checkedButton().polarity
        self.fill_table(selected_aspect, selected_polarity)

    def _on_radio_button_clicked(self, checked_button):
        selected_polarity = checked_button.polarity
        selected_aspect = self.aspects_combo_box.currentText()
        self.fill_table(selected_aspect, selected_polarity)

    def __on_settings_button_click(self):
        self.settings_window = SettingsWindow(self, self.mongo)
        self.settings_window.show()

    def __clear_table(self):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

    def fill_table(self, aspect, polatiry):
        self.table_widget.setSortingEnabled(False)
        self.__clear_table()
        docs = self.mongo.load_summary_data(aspect.lower(), polatiry)
        for doc in docs:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            col_id = 0
            for field in [doc['name'], str(doc['score']), doc['date'], str(doc['likes']), doc['text']]:
                self.table_widget.setItem(row_position, col_id, QTableWidgetItem(field))
                col_id += 1
        self.table_widget.setSortingEnabled(True)

    def fill_aspects(self):
        self.aspects_combo_box.clear()
        docs = self.mongo.load_aspects()
        for doc in docs:
            aspect = doc['aspect']
            self.aspects_combo_box.addItem(aspect)

    def process_with_new_settings(self):
        self.__clear_table()
        self.status_label.setText('Поиск частых аспектов')
        self.progress_bar.setValue(0)
        self.status_label.show()
        self.progress_bar.show()

        self.aspects_extractor.load_transactions()
        self.aspects_extractor.extract()
        self.aspects_extractor.write_aspects()

        self.status_label.setText('Поиск мнений')
        self.progress_bar.setValue(35)

        self.opinions_extractor.load_reviews()
        self.opinions_extractor.load_aspects()
        self.opinions_extractor.extract()
        self.opinions_extractor.write_opinions()

        self.status_label.setText('Анализ полярности')
        self.progress_bar.setValue(70)

        self.sentiment_analyzer.load_reviews()
        self.sentiment_analyzer.load_sentiment_dictionary_docs()
        self.sentiment_analyzer.analyze()
        self.sentiment_analyzer.write()

        self.status_label.hide()
        self.progress_bar.hide()

        self.__reset_to_start()


def main():
    application_name = 'Duolingo'
    config_file_name = '../settings.ini'
    app = QApplication(sys.argv)
    window = MainWindow(application_name, config_file_name)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
