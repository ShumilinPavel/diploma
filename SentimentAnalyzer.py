import pandas as pd


class SentimentAnalyzer:
    def __init__(self, opinions_file, sentiment_dict_file):
        self.opinions_df = pd.read_csv(opinions_file)
        self.sentiments_df = pd.read_csv(sentiment_dict_file)
        self.df = pd.DataFrame()

    def analyze(self):
        self.df = self.opinions_df.merge(self.sentiments_df, how='left', left_on='sentiment', right_on='word')[:][['id_review', 'aspect', 'sentiment', 'polarity']]
        self.df.drop_duplicates(inplace=True)

    def save_to_csv(self, file_name):
        self.df.to_csv(file_name)


if __name__ == '__main__':
    sentiment_analyzer = SentimentAnalyzer('yandex_mail_opinions.csv', 'sentiment_dictinary.csv')
    sentiment_analyzer.analyze()
    sentiment_analyzer.save_to_csv('yandex_mail_opinions_polarity.csv')
