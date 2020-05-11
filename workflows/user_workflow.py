import sys
from pyqt import *
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    application_name = 'YandexMail'

    app = QApplication(sys.argv)
    window = Gui(application_name)
    window.show()
    app.exec_()
