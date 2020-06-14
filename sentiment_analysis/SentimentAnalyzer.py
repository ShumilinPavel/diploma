import configparser
from MongoDb import *


class AspectsStatistics:
    def __init__(self):
        self.aspect_to_polarity_to_count = dict()

    def consider(self, aspect, polarity):
        if aspect in self.aspect_to_polarity_to_count.keys():
            self.aspect_to_polarity_to_count[aspect][polarity] += 1
        else:
            self.aspect_to_polarity_to_count[aspect] = dict()
            self.aspect_to_polarity_to_count[aspect]['positive'] = 0
            self.aspect_to_polarity_to_count[aspect]['negative'] = 0
            self.aspect_to_polarity_to_count[aspect]['neutral'] = 0
            self.aspect_to_polarity_to_count[aspect]['unknown'] = 0
            self.aspect_to_polarity_to_count[aspect][polarity] += 1

    def get_documents(self):
        documents = []
        for aspect in self.aspect_to_polarity_to_count.keys():
            documents.append({
                'aspect': aspect,
                'pos_rev_count': self.aspect_to_polarity_to_count[aspect]['positive'],
                'neg_rev_count': self.aspect_to_polarity_to_count[aspect]['negative'],
                'neut_rev_count': self.aspect_to_polarity_to_count[aspect]['neutral'],
                'unknown_rev_count': self.aspect_to_polarity_to_count[aspect]['unknown'],
            })
        return documents


class SentimentAnalyzer:
    def __init__(self, application_name, config_file_name):
        self.__parse_config(config_file_name, application_name)
        self.mongo = MongoDb(self.collection_name_prefix)
        self.review_docs = []
        self.sentiment_dictionary = dict()
        self.modified_review_docs = []
        self.aspects_statistics = AspectsStatistics()

    def __parse_config(self, config_file_name, application_name):
        self.config = configparser.ConfigParser()
        self.config.read(config_file_name, encoding='utf-8')
        self.collection_name_prefix = self.config[application_name]['collection_name_prefix']

    def load_reviews(self):
        self.review_docs = self.mongo.load_reviews()

    def load_sentiment_dictionary_docs(self):
        sentiment_dictionary_docs = self.mongo.load_sentiment_dictionary()
        for doc in sentiment_dictionary_docs:
            self.sentiment_dictionary[doc['word']] = doc['polarity']

    def analyze(self):
        known_sentiments = set(self.sentiment_dictionary.keys())
        self.aspects_statistics = AspectsStatistics()

        for review_doc in self.review_docs:
            id = review_doc["_id"]
            already_counted_opinion = set()
            if 'opinions' not in review_doc.keys():
                continue
            for opinion_obj in review_doc['opinions']:
                if 'sentiment' not in opinion_obj.keys():
                    continue
                aspect = opinion_obj['aspect']
                sentiment = opinion_obj['sentiment']
                if sentiment in known_sentiments:
                    polarity = self.sentiment_dictionary[sentiment]
                    opinion_obj['polarity'] = polarity
                    if aspect + sentiment not in already_counted_opinion:
                        self.aspects_statistics.consider(aspect, polarity)
                        already_counted_opinion.add(aspect + sentiment)
                else:
                    # opinion_obj['polarity'] = ''
                    if aspect + sentiment not in already_counted_opinion:
                        self.aspects_statistics.consider(aspect, "unknown")
                        already_counted_opinion.add(aspect + sentiment)
            self.modified_review_docs.append(review_doc)

    def write(self):
        self.mongo.write_polarities(self.modified_review_docs)
        self.mongo.write_aspects_statistics(self.aspects_statistics.get_documents())

    # def save_to_csv(self, file_name):
    #     self.df.to_csv(file_name)


if __name__ == '__main__':
    application_name = 'test'
    config_file_name = '../settings.ini'
    sentiment_analyzer = SentimentAnalyzer(application_name, config_file_name)
    sentiment_analyzer.load_reviews()
    sentiment_analyzer.load_sentiment_dictionary_docs()
    sentiment_analyzer.analyze()
    sentiment_analyzer.write()
