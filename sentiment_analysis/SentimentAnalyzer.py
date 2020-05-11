import configparser
from MongoDb import *


class SentimentAnalyzer:
    def __init__(self, application_name, config_file_name):
        self.__parse_config(config_file_name, application_name)
        self.mongo = MongoDb(self.collection_name_prefix)
        self.review_docs = []
        self.sentiment_dictionary= dict()
        self.modified_review_docs = []

    def __parse_config(self, config_file_name, application_name):
        self.config = configparser.ConfigParser()
        self.config.read(config_file_name)
        self.collection_name_prefix = self.config[application_name]['collection_name_prefix']

    def load_reviews(self):
        self.review_docs = self.mongo.load_reviews()

    def load_sentiment_dictionary_docs(self):
        sentiment_dictionary_docs = self.mongo.load_sentiment_dictionary()
        for doc in sentiment_dictionary_docs:
            self.sentiment_dictionary[doc['word']] = doc['polarity']

    def analyze(self):
        # self.df = self.opinions_df.merge(self.sentiments_df, how='left', left_on='sentiment', right_on='word')[:][['id_review', 'aspect', 'sentiment', 'polarity']]
        # self.df.drop_duplicates(inplace=True)
        # self.mongo.reviews_collection.aggregate([
        #     {"$unwind": "$opinions"},
        #     {
        #         "$lookup": {
        #             "from": self.mongo.sentiment_dictionary_collection_name,
        #             "localField": "opinions.sentiment",
        #             "foreignField": "word",
        #             "as": "opinions_new"
        #         }
        #     }
        # ])
        known_sentiments = set(self.sentiment_dictionary.keys())
        for review_doc in self.review_docs:
            id = review_doc["_id"]
            if 'opinions' not in review_doc.keys():
                continue
            for opinion_obj in review_doc['opinions']:
                sentiment = opinion_obj['sentiment']
                if sentiment == 'NOT FOUND':
                    continue
                if sentiment in known_sentiments:
                    polarity = self.sentiment_dictionary[sentiment]
                    opinion_obj['polarity'] = polarity
                else:
                    opinion_obj['polarity'] = ''
                    # TODO: надо ли это делать? Буду ли считать нейтральным?
            self.modified_review_docs.append(review_doc)

    def write(self):
        self.mongo.write_polarities(self.modified_review_docs)

    # def save_to_csv(self, file_name):
    #     self.df.to_csv(file_name)


if __name__ == '__main__':
    # application_name = 'YandexMail'
    application_name = 'Duolingo'
    config_file_name = '../settings.ini'
    sentiment_analyzer = SentimentAnalyzer(application_name, config_file_name)
    sentiment_analyzer.load_reviews()
    sentiment_analyzer.load_sentiment_dictionary_docs()
    sentiment_analyzer.analyze()
    sentiment_analyzer.write()
