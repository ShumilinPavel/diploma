import sys
from gui.MainWindow import MainWindow
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    application_name = 'YandexMail_500'
    config_file_name = '../settings.ini'

    app = QApplication(sys.argv)
    window = MainWindow(application_name, config_file_name)
    window.show()
    app.exec_()
