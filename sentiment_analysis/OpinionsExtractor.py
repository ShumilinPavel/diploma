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
        self.config.read(config_file_name, encoding='utf-8')
        self.collection_name_prefix = self.config[application_name]['collection_name_prefix']
        self.application_label = self.config[application_name]['application_label']

    def load_aspects(self):
        aspect_docs = self.mongo.load_aspects()
        for doc in aspect_docs:
            self.aspects.add(doc["aspect"])

    def load_reviews(self):
        self.review_docs = self.mongo.load_reviews()

    def extract(self):
        window_radius = self.__get_window_radius()
        stopwords = set(nltk.corpus.stopwords.words('russian'))
        stopwords.remove('не')
        tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
        self.id_to_opinions = dict()

        for doc in self.review_docs:
            id = doc["_id"]
            text = doc["text"]
            for sentence in nltk.sent_tokenize(text.lower(), language='russian'):
                words = tokenizer.tokenize(sentence)  # words = nltk.word_tokenize(sentence, language='russian')
                filtered_words = []
                for w in words:
                    if w not in stopwords:
                        filtered_words.append(w)
                # self.__process_sentence(id, filtered_words)
                for j in range(0, len(filtered_words)):
                    morphed = self.morph.parse(filtered_words[j])[0]
                    if morphed.tag.POS == 'NOUN' and morphed.normal_form in self.aspects:
                        self.__scan_window_for_sentiment(id, filtered_words, j, window_radius)

    def __get_window_radius(self):
        doc = self.mongo.load_window_radius(self.application_label)
        return int(doc['window'])

    def __process_sentence(self, id, words):
        morphed_adjective_pos_inverse_flag_tuples = []
        morphed_aspect_pos_pairs = []

        for i in range(len(words)):
            word = words[i]
            for morphed in self.morph.parse(word)[:2]:
                if morphed.tag.POS == 'ADJF': # or morphed.tag.POS == 'ADJS':
                    is_inversed = self.__is_inversed_polarity(words, i)
                    morphed_adjective_pos_inverse_flag_tuples.append((morphed, i, is_inversed))
                    break
                elif morphed.tag.POS == 'NOUN' and morphed.normal_form in self.aspects:
                    morphed_aspect_pos_pairs.append((morphed, i))
                    break

        sentiment_words_and_inverse_flag = []

        for (morphed, _, is_inversed) in morphed_adjective_pos_inverse_flag_tuples:
            if is_inversed:
                sentiment_words_and_inverse_flag.append({'word': morphed.normal_form, 'is_inversed': is_inversed})
            else:
                sentiment_words_and_inverse_flag.append({'word': morphed.normal_form})

        adjectives_normal_forms_length = len(sentiment_words_and_inverse_flag)
        window_radius = self.__get_window_radius()

        for (morphed_aspect, aspect_pos) in morphed_aspect_pos_pairs:
            left_pos = max(0, aspect_pos - window_radius)
            right_pos = min(aspect_pos + window_radius, len(words) - 1)
            min_dist = 9999
            effective_sentiment = ''
            for (morphed_adjective, adjective_pos, _) in morphed_adjective_pos_inverse_flag_tuples:
                if adjective_pos < left_pos:
                    continue
                elif adjective_pos > right_pos:
                    break
                else:
                    dist = abs(aspect_pos - adjective_pos)
                    if self.__are_adjective_and_aspect_match(morphed_adjective, morphed_aspect, dist, min_dist):
                        min_dist = dist
                        effective_sentiment = morphed_adjective.normal_form
            doc = {'aspect': morphed_aspect.normal_form}
            if effective_sentiment != '':
                doc['effective_sentiment'] = effective_sentiment
            if adjectives_normal_forms_length != 0:
                doc['sentiment_words'] = sentiment_words_and_inverse_flag
            if id in self.id_to_opinions.keys():
                self.id_to_opinions[id].append(doc)
            else:
                self.id_to_opinions[id] = [doc]

    def __is_inversed_polarity(self, words, adj_pos):
        if adj_pos == 0:
            return False
        return words[adj_pos - 1] == 'не'

    def __are_adjective_and_aspect_match(self, morphed_adjective, morphed_aspect, dist, min_dist):
        return (morphed_adjective.tag.POS == 'ADJF' and morphed_adjective.tag.case == morphed_aspect.tag.case or morphed_adjective.tag.POS == 'ADJS') and dist < min_dist

    def __scan_window_for_sentiment(self, id, sentence_words, aspect_position, window_radius):
        left_i = max(0, aspect_position - window_radius)
        right_i = min(aspect_position + window_radius, len(sentence_words) - 1)
        min_distance = 1000
        sentiment = ''
        aspect_morphed = self.morph.parse(sentence_words[aspect_position])[0]

        for i in range(left_i, right_i + 1):
            if i == aspect_position:
                continue
            for morphed in self.morph.parse(sentence_words[i])[:2]:
                if self.__are_words_consistent(morphed, aspect_morphed, i, aspect_position, min_distance):
                    min_distance = abs(i - aspect_position)
                    sentiment = morphed.normal_form
                    break
        doc = {'aspect': aspect_morphed.normal_form}
        if sentiment != '':
            doc['sentiment'] = sentiment
        if id in self.id_to_opinions.keys():
            self.id_to_opinions[id].append(doc)
        else:
            self.id_to_opinions[id] = [doc]

    def __are_words_consistent_1(self, morphed, aspect_morphed, word_position, aspect_position, min_distance):
        return (morphed.tag.POS == 'ADJF' and morphed.tag.case == aspect_morphed.tag.case or morphed.tag.POS == 'ADJS') and abs(word_position - aspect_position) < min_distance\
               # and morphed.tag.number == aspect_morphed.tag.number \
               # and morphed.tag.gender == aspect_morphed.tag.gender \
               # and abs(word_position - aspect_position) < min_distance

    def __are_words_consistent(self, morphed, aspect_morphed, word_position, aspect_position, min_distance):
        if (word_position - aspect_position) >= min_distance:
            return False
        pos = morphed.tag.POS
        score = 0
        if pos == 'ADJF' or pos == 'ADJS' or pos == 'PRTF':
            if morphed.tag.case == aspect_morphed.tag.case:
                score += 1
            if morphed.tag.number == aspect_morphed.tag.number:
                score += 1
            if morphed.tag.gender == aspect_morphed.tag.gender:
                score += 1
            return score >= 2
        return False

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
    application_name = 'test'
    config_file_name = '../settings.ini'
    opinions_extractor = OpinionsExtractor(application_name, config_file_name)
    opinions_extractor.load_reviews()
    opinions_extractor.load_aspects()
    opinions_extractor.extract()
    opinions_extractor.write_opinions()
