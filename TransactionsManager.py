import configparser
import pandas as pd
import re
import nltk
import pymorphy2
# Теги для pymorph2: https://pymorphy2.readthedocs.io/en/latest/user/grammemes.html


class TransactionsManager:
    def __init__(self, reviews_file):
        self.df = pd.read_csv(reviews_file)
        self.raw_reviews = list(self.df.loc[:, 'text'])
        self.transactions = []

    def create_transactions(self):
        morph = pymorphy2.MorphAnalyzer()
        self.transactions = []
        for review in self.raw_reviews:
            transaction = []
            clear_review = re.sub('[^А-Яа-яё0-9]+', ' ', review).lower()
            for word in clear_review.split():
                morphed = morph.parse(word)[0]
                if morphed.tag.POS == 'NOUN':
                    transaction.append(morphed.normal_form)
            self.transactions.append(' '.join(transaction))

    def create_transactions_advanced(self):
        morph = pymorphy2.MorphAnalyzer()
        self.transactions = []
        for review in self.raw_reviews:
            transaction = []
            for sentence in nltk.sent_tokenize(review, language='russian'):
                bigrams = list(nltk.bigrams(nltk.word_tokenize(sentence.lower(), language='russian')))
                for first, second in bigrams:
                    first_morphed = morph.parse(first)[0]
                    second_morphed = morph.parse(second)[0]
                    morphed = [first_morphed, second_morphed]
                    if TransactionsManager.__is_noun_phrase(morphed):
                        transaction.append(' '.join(m.normal_form for m in morphed))
                    if first_morphed.tag.POS == 'NOUN':
                        transaction.append(first_morphed.normal_form)
                if len(bigrams) > 0:
                    last_morphed = morph.parse(bigrams[len(bigrams) - 1][1])[0]
                    if last_morphed.normal_form == 'NOUN':
                        transaction.append(last_morphed.normal_form)
            self.transactions.append(';'.join(set(transaction)))

            #     words = re.sub('[^А-Яа-яё0-9]+', ' ', sentence).lower().split()
            #     for i in range(0, len(words) - 1):
            #         morphed_0 = morph.parse(words[i])[0]
            #         morphed_1 = morph.parse(words[i + 1])[0]
            #         morphed = [morphed_0, morphed_1]
            #         if morphed_0.tag.POS == 'NOUN' and morphed_1.tag.POS == 'ADJF' or morphed_0.tag.POS == 'ADJF' and morphed_1.tag.POS == 'NOUN':
            #             transaction.append(' '.join([m.normal_form for m in morphed]))
            #         if morphed_0.tag.POS == 'NOUN':
            #             transaction.append(morphed[0].normal_form)
            #         if i + 1 == len(words) - 1 and morphed_1.tag.POS == 'NOUN':
            #             transaction.append(morphed[1].normal_form)
            #     if len(words) == 1:
            #         morphed = morph.parse(words[0])[0]
            #         if morphed.tag.POS == 'NOUN':
            #             transaction.append(morphed.normal_form)
            # self.transactions.append(';'.join(transaction))

    @staticmethod
    def __is_noun_phrase(words):
        return words[0].tag.case == words[1].tag.case and \
               (words[0].tag.POS == 'NOUN' and words[1].tag.POS == 'ADJF' or
               words[0].tag.POS == 'ADJF' and words[1].tag.POS == 'NOUN')

    def create_transactions_regexp(self):
        self.transactions = []
        # patterns = """
        #     S+V:{<S><V>}
        #     V+S:{<V><S>}
        #     A+S:{<A=.*><A=.*>*<S>}
        #     S+A:{<S><A=.*>*}
        # """
        patterns = """
            A+S:{<A=.*><A=.*>*<S>}
            S+A:{<S><A=.*><A=.*>*}
        """
        chunker = nltk.RegexpParser(patterns)

        for review in self.raw_reviews:
            tokens_tag = nltk.pos_tag(nltk.word_tokenize(review.lower(), language='russian'), lang='rus')
            chunked = chunker.parse(tokens_tag)

            transaction = []
            for node in chunked:
                if isinstance(node, nltk.tree.Tree):
                    if node.label() == 'A+S' or node.label() == 'S+A':
                        print(node)
                        noun_phrase = []
                        for subnode in node:
                            noun_phrase.append(subnode[0])
                        transaction.append(' '.join(noun_phrase))
                elif node[1] == 'S':
                    transaction.append(node[0])
            self.transactions.append(';'.join(transaction))

    def save_transactions_to_csv(self, file_name):
        df_tr = pd.DataFrame({'itemset': self.transactions})
        df_tr.to_csv(file_name)


if __name__ == '__main__':
    application_name = 'YandexMail'
    config = configparser.ConfigParser()
    config.read('settings.ini')
    application_file_prefix = config[application_name]['application_file_prefix']
    transactions_manager = TransactionsManager('{0}.csv'.format(application_file_prefix))
    transactions_manager.create_transactions()
    # transactions_manager.create_transactions_regexp()
    # transactions_manager.create_transactions_advanced()
    transactions_manager.save_transactions_to_csv('{0}_transactions.csv'.format(application_file_prefix))
