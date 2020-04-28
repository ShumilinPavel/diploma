import os
import csv


class CsvWriter:
    def __init__(self, output_file):
        self.file = output_file

    # data = [(name, score, date, likes, has_photo, text), ...]
    def write(self, data):
        if not os.path.exists(self.file):
            self.__write_header()
        self.__write_data(data)

    def __write_header(self):
        with open(self.file, "w", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'name', 'score', 'date', 'likes', 'has_photo', 'text'])

    def __write_data(self, data):
        with open(self.file, "a", newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            id = 0
            for name, score, date, likes, has_photo, text in data:
                writer.writerow([id, name, score, date, likes, has_photo, text])
                id += 1
