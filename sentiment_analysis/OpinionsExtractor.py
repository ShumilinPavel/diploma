import configparser
import pymorphy2
import nltk
from MongoDb import *


class OpinionsExtractor:
    def __init__(self, application_name, config_file_name):
        self.__parse_config(config_file_name, application_name)
        self.mongo = MongoDb(self.collection_name_prefix)
        self.morph = pymorphy2.MorphAnalyzer()
        self.aspects = set()
        self.id_to_opinions = dict()
        self.review_docs = []

    def __parse_config(self, config_file_name, application_name):
        self.config = configparser.ConfigParser()
        self.config.read(config_file_name)
        self.collection_name_prefix = self.config[application_name]['collection_name_prefix']

    def load_aspects(self):
        aspect_docs = self.mongo.load_aspects()
        for doc in aspect_docs:
            self.aspects.add(doc["aspect"])

    def load_reviews(self):
        self.review_docs = self.mongo.load_reviews()

    # def extract(self):
    #     for i in list(self.df['id']):
    #         review = self.df.loc[i, 'text']
    #         for sentence in nltk.sent_tokenize(review.lower(), language='russian'):
    #             words = nltk.word_tokenize(sentence, language='russian')
    #             for j in range(0, len(words)):
    #                 morphed = self.morph.parse(words[j])[0]
    #                 if morphed.tag.POS == 'NOUN' and morphed.normal_form in self.aspects:
    #                     self.__scan_window_for_sentiment(i, words, j)

    def extract(self):
        window_radius = self.__get_window_radius()
        for doc in self.review_docs:
            id = doc["_id"]
            text = doc["text"]
            for sentence in nltk.sent_tokenize(text.lower(), language='russian'):
                words = nltk.word_tokenize(sentence, language='russian')
                for j in range(0, len(words)):
                    morphed = self.morph.parse(words[j])[0]
                    if morphed.tag.POS == 'NOUN' and morphed.normal_form in self.aspects:
                        self.__scan_window_for_sentiment(id, words, j, window_radius)

    def __scan_window_for_sentiment(self, id, sentence_words, aspect_position, window_radius):
        left_i = max(0, aspect_position - window_radius)
        right_i = min(aspect_position + window_radius, len(sentence_words) - 1)
        min_distance = 1000
        sentiment = 'NOT FOUND'
        aspect_morphed = self.morph.parse(sentence_words[aspect_position])[0]
        for i in range(left_i, right_i + 1):
            if i == aspect_position:
                continue
            for morphed in self.morph.parse(sentence_words[i]):
                if (morphed.tag.POS == 'ADJF' or morphed.tag.POS == 'ADJS') and morphed.tag.case == aspect_morphed.tag.case and abs(i - aspect_position) < min_distance:
                    min_distance = abs(i - aspect_position)
                    sentiment = morphed.normal_form
                    break
        if id in self.id_to_opinions.keys():
            self.id_to_opinions[id].append({'aspect': aspect_morphed.normal_form, 'sentiment': sentiment})
        else:
            self.id_to_opinions[id] = [{'aspect': aspect_morphed.normal_form, 'sentiment': sentiment}]

    def __get_window_radius(self):
        doc = self.mongo.load_window_radius()
        return int(doc['window'])

    def write_opinions(self):
        self.mongo.write_opinions(self.id_to_opinions)

    # def save_opinions_to_csv(self, file_name):
    #     df_opinions = pd.DataFrame(self.opinions)
    #     df_opinions.to_csv(file_name)

    # def extract_opinion_advanced(self):
    #     morph = pymorphy2.MorphAnalyzer()
    #     for i in self.df.index:
    #         review = self.df.loc[i, 'text']
    #         for sentence in nltk.sent_tokenize(review, language='russian'):
    #             bigrams = list(nltk.bigrams(nltk.word_tokenize(sentence.lower(), language='russian')))
    #             for j in range(len(bigrams)):
    #                 first = bigrams[j][0]
    #                 second = bigrams[j][1]
    #                 first_morphed = morph.parse(first)[0]
    #                 second_morphed = morph.parse(second)[0]
    #                 if first_morphed.tag.case == second_morphed.tag.case:
    #                     potential_aspect = ' '.join([first_morphed.normal_form, second_morphed.normal_form])
    #                     if potential_aspect in self.aspects:
    #                         self.__scan_window_for_sentiment(i, 2*j, 2*j + 1, self.window_size) # self.window_size не существует
    #                     elif first_morphed.normal_form in self.aspects:
    #                         self.__scan_window_for_sentiment(i, 2*j, 2*j, self.window_size)
    #                 if len(bigrams) > 0:
    #                    # last
    #                     pass

    # def __scan_window_for_sentiment_advanced(self, id, aspect_left_position, aspect_right_position, window_size):
    #     pass


if __name__ == '__main__':
    # application_name = 'YandexMail'
    application_name = 'Duolingo'
    config_file_name = '../settings.ini'
    opinions_extractor = OpinionsExtractor(application_name, config_file_name)
    opinions_extractor.load_reviews()
    opinions_extractor.load_aspects()
    opinions_extractor.extract()
    opinions_extractor.write_opinions()
