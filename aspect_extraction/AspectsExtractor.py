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
        self.config.read(config_file_name, encoding='utf-8')
        self.collection_name_prefix = self.config[application_name]['collection_name_prefix']
        self.application_label = self.config[application_name]['application_label']

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

        if self.__settings_for_app_exist():
            minsup = self.__get_minsup_fraction()
        else:
            minsup = 0.1
            self.mongo.save_new_settings(self.application_label, self.collection_name_prefix, 10, 2)
        df_aspects = apriori(sparse_df, min_support=minsup, use_colnames=True, max_len=1)

        self.aspect_docs = []
        for i in df_aspects.index:
            aspect = ' '.join(list(df_aspects.loc[i, 'itemsets']))
            self.aspect_docs.append({'aspect': aspect, 'support': df_aspects.loc[i, 'support']})

    def __settings_for_app_exist(self):
        return self.mongo.find_settings(self.application_label) != 0

    def __get_minsup_fraction(self):
        doc = self.mongo.load_minimum_support(self.application_label)
        return float(doc['minsup']) / 100

    def write_aspects(self):
        self.mongo.write_aspects(self.aspect_docs)

    # def extract_advanced(self):
    #     transactions_for_te = []
    #     for doc in self.transaction_docs:
    #         transaction = doc["transaction"]
    #         transactions_for_te.append(transaction.split(';'))
    #
    #     te = TransactionEncoder()
    #     oht_ary = te.fit(transactions_for_te).transform(transactions_for_te, sparse=True)
    #     sparse_df = pd.DataFrame.sparse.from_spmatrix(oht_ary, columns=te.columns_)
    #
    #     minsup = self.__get_minsup_fraction()
    #     df_aspects = apriori(sparse_df, min_support=minsup, use_colnames=True, max_len=1)
    #
    #
    #     # for aspect_set in list(df_aspects['itemsets']):
    #     #     aspect = ' '.join(list(aspect_set))
    #     #     self.aspect_docs.append({'aspect': aspect})
    #
    #     for i in df_aspects.index:
    #         aspect = ' '.join(list(df_aspects.loc[i, 'itemsets']))
    #         self.aspect_docs.append({'aspect': aspect, 'support': df_aspects.loc[i, 'support']})


if __name__ == '__main__':
    application_name = 'test'
    config_file_name = '../settings.ini'
    aspects_extractor = AspectsExtractor(application_name, config_file_name)
    aspects_extractor.load_transactions()
    aspects_extractor.extract()
    aspects_extractor.write_aspects()
