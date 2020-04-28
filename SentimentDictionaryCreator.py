import pandas as pd


class SentimentDictionaryCreator:
    def __init__(self, ru_wordnet_affect_positive_files, ru_wordnet_affect_negative_files, rusentilex_file):
        self.ru_wordnet_affect_positive_files = ru_wordnet_affect_positive_files
        self.ru_wordnet_affect_negative_files = ru_wordnet_affect_negative_files
        self.rusentilex_file = rusentilex_file
        self.adjective_to_polarity = dict()

    def create(self):
        self.__process_ru_wordnet_affect()
        self.__process_rusentilex()

    def __process_ru_wordnet_affect(self):
        for file_name in self.ru_wordnet_affect_positive_files:
            self.__process_file_with_mark(file_name, 'positive')
        for file_name in self.ru_wordnet_affect_negative_files:
            self.__process_file_with_mark(file_name, 'negative')

    def __process_file_with_mark(self, file_name, mark):
        with open(file_name, 'r', encoding='utf-8-sig') as file:
            for line in file:
                if '\t' in line:
                    rus_words = line.split('\t')[3]
                    for word in rus_words.split():
                        self.adjective_to_polarity[word.replace('_', ' ')] = mark

    def __process_rusentilex(self):
        with open(self.rusentilex_file, 'r', encoding='utf-8-sig') as file:
            for i in range(18):
                file.readline()
            for line in file:
                words = [w.strip() for w in line.split(',')]
                pos = words[1]
                lemma = words[2]
                polarity = words[3]
                source = words[4]
                if pos == 'Adj' and lemma not in self.adjective_to_polarity.keys() and source == 'opinion':
                    self.adjective_to_polarity[lemma] = polarity

    def save_to_csv(self, file_name):
        df = pd.DataFrame({'word': list(self.adjective_to_polarity.keys()), 'polarity': list(self.adjective_to_polarity.values())})
        df.to_csv(file_name)


if __name__ == '__main__':
    prepath = '../resourses/WordNetAffectRuRomVer2\WordNet-AffectRuRomVer2/'
    sentiment_dictionary_creator = SentimentDictionaryCreator(
        [prepath+'joy.txt', prepath+'surprise.txt'],
        [prepath+'anger.txt', prepath+'disgust.txt', prepath+'fear.txt', prepath+'sadness.txt'],
        '../resourses/'+'rusentilex_2017.txt'
    )
    sentiment_dictionary_creator.create()
    sentiment_dictionary_creator.save_to_csv('sentiment_dictinary.csv')
