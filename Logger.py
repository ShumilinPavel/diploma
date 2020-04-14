import datetime


class Logger:
    def __init__(self, file_name):
        self.file_name = file_name

    def log(self, text):
        with open(self.file_name, 'a', encoding='utf-8') as file:
            file.write("{0} : {1}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), text))
