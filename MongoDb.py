from pymongo import MongoClient


class MongoDb:
    def __init__(self, collection_name_prefix):
        self.client = MongoClient()
        self.db = self.client["google_play_reviews_analyzer"]
        self.reviews_collection = self.db[collection_name_prefix + "_reviews"]
        self.aspects_collection = self.db[collection_name_prefix + "_aspects"]
        self.sentiment_dictionary_collection = self.db["sentiment_dictionary"]
        self.settings_collection = self.db['settings']

    def change_collection(self, collection_name_prefix):
        self.reviews_collection = self.db[collection_name_prefix + "_reviews"]
        self.aspects_collection = self.db[collection_name_prefix + "_aspects"]

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
        if len(aspect_docs) == 0:
            return
        self.aspects_collection.remove({})
        self.aspects_collection.insert_many(aspect_docs)

    def load_aspects(self):
        return self.aspects_collection.find({})

    def write_opinions(self, id_to_opinions):
        for id, opinions in id_to_opinions.items():
            self.reviews_collection.update_one({"_id": id}, {"$set": {"opinions": opinions}})

    def write_sentiment_dictionary(self, sentiment_docs):
        self.sentiment_dictionary_collection.remove({})
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

    def load_summary_data_with_unknown_polarity(self, aspect, polarity):
        return self.reviews_collection.find({"$or": [
            {"opinions": {"$elemMatch": {"aspect": aspect, "polarity": polarity}}},
            # {"opinions": {"$elemMatch": {"aspect": aspect, "sentiment": {"$exists": True}, "polarity": {"$exists": False}}}}
            {"opinions": {"$elemMatch": {"aspect": aspect, "polarity": {"$exists": False}}}}
        ]}, {"name": 1, "score": 1, "date": 1, "likes": 1, "text": 1})

    def load_minimum_support(self, application_label):
        return self.settings_collection.find_one({"app_label": application_label}, {"minsup": 1})

    def load_window_radius(self, application_label):
        return self.settings_collection.find_one({"app_label": application_label}, {"window": 1})

    def update_settings(self, app_label, minsup, window_radius):
        self.settings_collection.update_one({"app_label": app_label}, {"$set": {"minsup": minsup, "window": window_radius}})

    def save_new_settings(self, app_label, collection_name_prefix, minsup, window_radius):
        self.settings_collection.insert_one({"app_label": app_label, "collection_name_prefix": collection_name_prefix,
                                             "minsup": minsup, "window": window_radius})

    def load_application_labels(self):
        return self.settings_collection.find({}, {"app_label": 1})

    def load_collection_prefix(self, app_label):
        return self.settings_collection.find_one({"app_label": app_label}, {"collection_name_prefix": 1})

    def find_settings(self, app_label):
        return self.settings_collection.count_documents({"app_label": app_label})

    def write_aspects_statistics(self, aspects_statistics_docs):
        for doc in aspects_statistics_docs:
            aspect = doc['aspect']
            pos_rev_count = doc['pos_rev_count']
            neg_rev_count = doc['neg_rev_count']
            neut_rev_count = doc['neut_rev_count']
            unknown_rev_count = doc['unknown_rev_count']
            self.aspects_collection.update_one(
                {"aspect": aspect},
                {"$set": {
                    "pos_rev_count": pos_rev_count,
                    "neg_rev_count": neg_rev_count,
                    "neut_rev_count": neut_rev_count,
                    'unknown_rev_count': unknown_rev_count
                }
                }
            )
