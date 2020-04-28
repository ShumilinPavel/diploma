import pandas as pd
import configparser
import pymorphy2
import nltk


class OpinionExtractor:
    def __init__(self, reviews_file, aspects):
        self.df = pd.read_csv(reviews_file)
        self.raw_reviews = list(self.df.loc[:, 'text'])
        self.aspects = aspects # set
        self.opinions = list()
        self.window_size = 3
        self.morph = pymorphy2.MorphAnalyzer()

    def extract_opinion(self):
        for i in list(self.df['id']):
            review = self.df.loc[i, 'text']
            for sentence in nltk.sent_tokenize(review.lower(), language='russian'):
                words = nltk.word_tokenize(sentence, language='russian')
                for j in range(0, len(words)):
                    morphed = self.morph.parse(words[j])[0]
                    if morphed.tag.POS == 'NOUN' and morphed.normal_form in self.aspects:
                        self.__scan_window_for_sentiment(i, words, j)

    def __scan_window_for_sentiment(self, id, sentence_words, aspect_position):
        left_i = max(0, aspect_position - self.window_size)
        right_i = min(aspect_position + self.window_size, len(sentence_words) - 1)
        min_distance = 1000
        sentiment = 'NOT FOUND'
        aspect_morphed = self.morph.parse(sentence_words[aspect_position])[0]
        for i in range(left_i, right_i + 1):
            for morphed in self.morph.parse(sentence_words[i]):
                if (morphed.tag.POS == 'ADJF' or morphed.tag.POS == 'ADJS') and morphed.tag.case == aspect_morphed.tag.case and abs(i - aspect_position) < min_distance:
                    min_distance = abs(i - aspect_position)
                    sentiment = morphed.normal_form
                    break
        self.opinions.append({'id_review': id, 'aspect': aspect_morphed.normal_form, 'sentiment': sentiment})

    def save_opinions_to_csv(self, file_name):
        df_opinions = pd.DataFrame(self.opinions)
        df_opinions.to_csv(file_name)

    def extract_opinion_advanced(self):
        morph = pymorphy2.MorphAnalyzer()
        for i in self.df.index:
            review = self.df.loc[i, 'text']
            for sentence in nltk.sent_tokenize(review, language='russian'):
                bigrams = list(nltk.bigrams(nltk.word_tokenize(sentence.lower(), language='russian')))
                for j in range(len(bigrams)):
                    first = bigrams[j][0]
                    second = bigrams[j][1]
                    first_morphed = morph.parse(first)[0]
                    second_morphed = morph.parse(second)[0]
                    if first_morphed.tag.case == second_morphed.tag.case:
                        potential_aspect = ' '.join([first_morphed.normal_form, second_morphed.normal_form])
                        if potential_aspect in self.aspects:
                            self.__scan_window_for_sentiment(i, 2*j, 2*j + 1, self.window_size)
                        elif first_morphed.normal_form in self.aspects:
                            self.__scan_window_for_sentiment(i, 2*j, 2*j, self.window_size)
                    if len(bigrams) > 0:
                       # last
                        pass

    def __scan_window_for_sentiment_advanced(self, id, aspect_left_position, aspect_right_position, window_size):
        pass


if __name__ == '__main__':
    application_name = 'YandexMail'
    config = configparser.ConfigParser()
    config.read('settings.ini')
    application_file_prefix = config[application_name]['application_file_prefix']

    df = pd.read_csv('yandex_mail_features.csv')
    aspects = list(df.loc[:, 'Split Value 1'])

    opinion_extractor = OpinionExtractor('{0}.csv'.format(application_file_prefix), aspects)
    opinion_extractor.extract_opinion()
    opinion_extractor.save_opinions_to_csv('{0}_opinions.csv'.format(application_file_prefix))
