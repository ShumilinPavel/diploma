import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import gui.layouts.main_ui as main_ui
import configparser
from MongoDb import MongoDb
from aspect_extraction.AspectsExtractor import AspectsExtractor
from sentiment_analysis.OpinionsExtractor import OpinionsExtractor
from sentiment_analysis.SentimentAnalyzer import SentimentAnalyzer
from gui.SettingsWindow import SettingsWindow


class MainWindow(QMainWindow, main_ui.Ui_main_window):
    def __init__(self, application_name, config_file_name):
        super().__init__()
        self.setupUi(self)

        self.__parse_config(config_file_name, application_name)
        self.mongo = MongoDb(self.collection_name_prefix)

        self.aspects_extractor = AspectsExtractor(application_name, config_file_name)
        self.opinions_extractor = OpinionsExtractor(application_name, config_file_name)
        self.sentiment_analyzer = SentimentAnalyzer(application_name, config_file_name)

        self.aspect_to_color = dict()

        self.__fill_applications_combo_box()
        current_app_label = self.applications_combo_box.currentText()
        self.__reset_to_start_for_app(current_app_label)

        self.__setup_signals()

    def __parse_config(self, config_file_name, application_name):
        self.config = configparser.ConfigParser()
        self.config.read(config_file_name, encoding='utf-8')
        self.collection_name_prefix = self.config[application_name]['collection_name_prefix']

    def __fill_applications_combo_box(self):
        app_labels_docs = self.mongo.load_application_labels()
        for doc in app_labels_docs:
            app_label = doc['app_label']
            self.applications_combo_box.addItem(app_label)

    def __reset_to_start_for_app(self, app_label):
        collection_name_prefix = self.mongo.load_collection_prefix(app_label)['collection_name_prefix']
        self.mongo.change_collection(collection_name_prefix)
        self.fill_aspects()
        self.fill_table(self.aspects_combo_box.currentText(), self.button_group.checkedButton().polarity)

    def fill_aspects(self):
        self.aspects_combo_box.clear()
        self.aspect_to_color.clear()
        docs = self.mongo.load_aspects()
        model = self.aspects_combo_box.model()

        for doc in docs:
            aspect = doc['aspect']
            if 'pos_rev_count' in doc.keys():
                pos_count = doc['pos_rev_count']
                recognised_count = pos_count + doc['neg_rev_count']
                entry = QStandardItem('{0} ({1})'.format(aspect, recognised_count))
                if recognised_count != 0:
                    fraction = pos_count / recognised_count
                    if fraction > 0.5:
                        self.aspect_to_color[aspect] = 'green'
                        entry.setForeground(QColor('green'))
                    elif fraction < 0.5:
                        self.aspect_to_color[aspect] = 'red'
                        entry.setForeground(QColor('red'))
                    else:
                        self.aspect_to_color[aspect] = 'brown'
                        entry.setForeground(QColor('brown'))
                else:
                    entry = QStandardItem('{0} (0)'.format(aspect))
                    self.aspect_to_color[aspect] = 'black'
                    entry.setForeground(QColor('black'))
            else:
                entry = QStandardItem('{0} (0)'.format(aspect))
                self.aspect_to_color[aspect] = 'black'
                entry.setForeground(QColor('black'))
            model.appendRow(entry)

    def fill_table(self, aspect, polarity):
        self.table_widget.setSortingEnabled(False)
        self.__clear_table()
        aspect = aspect.split(' (')[0]
        if polarity != 'neutral':
            docs = self.mongo.load_summary_data(aspect.lower(), polarity)
        else:
            docs = self.mongo.load_summary_data_with_unknown_polarity(aspect.lower(), polarity)
        for doc in docs:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)
            col_id = 0
            for field in [doc['name'], str(doc['score']), doc['date'], str(doc['likes']), doc['text']]:
                self.table_widget.setItem(row_position, col_id, QTableWidgetItem(field))
                col_id += 1
        self.table_widget.setSortingEnabled(True)

    def __clear_table(self):
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)

    def __setup_signals(self):
        self.applications_combo_box.currentTextChanged.connect(self.__on_application_change)
        self.aspects_combo_box.currentTextChanged.connect(self.__on_aspect_change)
        self.button_group.buttonClicked.connect(self.__on_radio_button_click)
        self.settings_btn.clicked.connect(self.__on_settings_button_click)

    def __on_application_change(self, selected_app_label):
        self.__reset_to_start_for_app(selected_app_label)

    def __on_aspect_change(self, selected_aspect):
        selected_polarity = self.button_group.checkedButton().polarity
        cleared_aspect = selected_aspect.split(' (')[0]
        if cleared_aspect in self.aspect_to_color.keys():
            color = self.aspect_to_color[cleared_aspect]
            self.aspects_combo_box.setStyleSheet("QComboBox:editable{{ color: {} }}".format(color))
        self.fill_table(selected_aspect, selected_polarity)

    def __on_radio_button_click(self, checked_button):
        selected_polarity = checked_button.polarity
        selected_aspect = self.aspects_combo_box.currentText()
        self.fill_table(selected_aspect, selected_polarity)

    def __on_settings_button_click(self):
        self.settings_window = SettingsWindow(self, self.mongo)
        self.settings_window.show()

    def process_with_new_settings(self):
        self.__clear_table()
        self.status_label.setText('Поиск частых аспектов')
        self.progress_bar.setValue(0)
        self.status_label.show()
        self.progress_bar.show()

        app_label = self.applications_combo_box.currentText()
        collection_name_prefix = self.mongo.load_collection_prefix(app_label)['collection_name_prefix']
        self.aspects_extractor.mongo.change_collection(collection_name_prefix)
        self.aspects_extractor.application_label = app_label
        self.aspects_extractor.load_transactions()
        self.aspects_extractor.extract()
        self.aspects_extractor.write_aspects()

        self.status_label.setText('Поиск мнений')
        self.progress_bar.setValue(35)

        self.opinions_extractor.mongo.change_collection(collection_name_prefix)
        self.opinions_extractor.application_label = app_label
        self.opinions_extractor.load_reviews()
        self.opinions_extractor.load_aspects()
        self.opinions_extractor.extract()
        self.opinions_extractor.write_opinions()

        self.status_label.setText('Анализ полярности')
        self.progress_bar.setValue(70)

        self.sentiment_analyzer.mongo.change_collection(collection_name_prefix)
        self.sentiment_analyzer.application_label = app_label
        self.sentiment_analyzer.load_reviews()
        self.sentiment_analyzer.load_sentiment_dictionary_docs()
        self.sentiment_analyzer.analyze()
        self.sentiment_analyzer.write()

        self.status_label.hide()
        self.progress_bar.hide()

        self.__reset_to_start_for_app(app_label)


if __name__ == '__main__':
    application_name = 'test'
    config_file_name = '../settings.ini'
    app = QApplication(sys.argv)
    window = MainWindow(application_name, config_file_name)
    window.show()
    app.exec_()
