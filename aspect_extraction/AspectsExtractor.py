from mlxtend.frequent_patterns.apriori import apriori
from mlxtend.preprocessing import TransactionEncoder
import pandas as pd
from MongoDb import *
import configparser


class AspectsExtractor:
    def __init__(self, application_name, config_file_name):
        self.__parse_config(config_file_name, application_name)
        self.mongo = MongoDb(self.collection_name_prefix)
        self.transaction_docs = []
        self.aspect_docs = []

    def __parse_config(self, config_file_name, application_name):
        self.config = configparser.ConfigParser()
        self.config.read(config_file_name)
        self.collection_name_prefix = self.config[application_name]['collection_name_prefix']

    def load_transactions(self):
        self.transaction_docs = self.mongo.load_transactions()

    def extract(self):
        transactions_for_te = []
        for doc in self.transaction_docs:
            transaction = doc["transaction"]
            transactions_for_te.append(transaction.split())

        te = TransactionEncoder()
        oht_ary = te.fit(transactions_for_te).transform(transactions_for_te, sparse=True)
        sparse_df = pd.DataFrame.sparse.from_spmatrix(oht_ary, columns=te.columns_)

        minsup = self.__get_minsup_fraction()
        df_aspects = apriori(sparse_df, min_support=minsup, use_colnames=True, max_len=1)

        # TODO: получение аспектов, если длина больше 1
        for aspect_set in list(df_aspects['itemsets']):
            aspect = ' '.join(list(aspect_set))
            self.aspect_docs.append({'aspect': aspect})

    def write_aspects(self):
        self.mongo.write_aspects(self.aspect_docs)

    def __get_minsup_fraction(self):
        doc = self.mongo.load_minimum_support()
        return int(doc['minsup']) / 100


if __name__ == '__main__':
    # application_name = 'YandexMail'
    application_name = 'Duolingo'
    config_file_name = '../settings.ini'
    aspects_extractor = AspectsExtractor(application_name, config_file_name)
    aspects_extractor.load_transactions()
    aspects_extractor.extract()
    aspects_extractor.write_aspects()
