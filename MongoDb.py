from pymongo import MongoClient


class MongoDb:
    def __init__(self, collection_name_prefix):
        self.client = MongoClient()
        self.database_name = "google_play_reviews_analyzer"
        self.db = self.client[self.database_name]
        self.reviews_collection_name = collection_name_prefix + "_reviews"
        self.reviews_collection = self.db[self.reviews_collection_name]
        self.aspects_collection_name = collection_name_prefix + "_aspects"
        self.aspects_collection = self.db[self.aspects_collection_name]
        self.sentiment_dictionary_collection_name = "sentiment_dictionary"
        self.sentiment_dictionary_collection = self.db[self.sentiment_dictionary_collection_name]
        self.settings_collection_name = 'settings'
        self.settings_collection = self.db[self.settings_collection_name]

    def write_reviews(self, review_docs):
        self.reviews_collection.insert_many(review_docs)

    def load_reviews(self):
        return self.reviews_collection.find({}, {"_id": 1, "text": 1, "opinions": 1})

    def write_transactions(self, transaction_docs):
        for doc in transaction_docs:
            id = doc["_id"]
            transaction = doc["transaction"]
            self.reviews_collection.update_one({"_id": id}, {"$set": {"transaction": transaction}})

    def load_transactions(self):
        return self.reviews_collection.find({}, {"_id": 1, "transaction": 1})

    def write_aspects(self, aspect_docs):
        self.aspects_collection.remove()
        self.aspects_collection.insert_many(aspect_docs)

    def load_aspects(self):
        return self.aspects_collection.find({}, {"_id": 1, "aspect": 1})

    def write_opinions(self, id_to_opinions):
        for id, opinions in id_to_opinions.items():
            self.reviews_collection.update_one({"_id": id}, {"$set": {"opinions": opinions}})

    def write_sentiment_dictionary(self, sentiment_docs):
        self.sentiment_dictionary_collection.insert_many(sentiment_docs)

    def load_sentiment_dictionary(self):
        return self.sentiment_dictionary_collection.find({})

    def write_polarities(self, reviews_docs):
        for doc in reviews_docs:
            id = doc["_id"]
            opinions = doc["opinions"]
            self.reviews_collection.update_one({"_id": id}, {"$set": {"opinions": opinions}})

    def load_summary_data(self, aspect, polarity):
        return self.reviews_collection.find({"opinions": {"$elemMatch": {"aspect": aspect, "polarity": polarity}}},
                                            {"name": 1, "score": 1, "date": 1, "likes": 1, "text": 1})

    def load_minimum_support(self):
        return self.settings_collection.find_one({}, {"minsup": 1})
        # TODO: совпадение по приложению

    def load_window_radius(self):
        return self.settings_collection.find_one({}, {"window": 1})
        # TODO: совпадение по приложению

    def save_settings(self, minsup, window_radius):
        # self.settings_collection.update_one({}, {"$set": {"minsup": minsup, "window": window_radius}})
        self.settings_collection.replace_one({}, {"minsup": minsup, "window": window_radius})

m = MongoDb('asdf')
