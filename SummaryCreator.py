import pandas as pd


class SummaryCreator:
    def __init__(self, reviews_file, opinions_polarity_file):
        self.reviews_df = pd.read_csv(reviews_file)
        self.opinions_polarity = pd.read_csv(opinions_polarity_file)
        self.summary = pd.DataFrame()

    def create(self):
        self.summary = self.reviews_df.merge(self.opinions_polarity, how='left', left_on='id', right_on='id_review')
        self.summary.drop(['Unnamed: 0_x', 'Unnamed: 0_y', 'id_review'], axis=1, inplace=True)
        # self.summary.set_index(['aspect', 'polarity', 'name'], inplace=True)
        # self.summary.sort_index(inplace=True)

    def save_to_file(self, file_name):
        self.summary.to_csv(file_name)


if __name__ == '__main__':
    summary_creator = SummaryCreator('yandex_mail.csv', 'yandex_mail_opinions_polarity.csv')
    summary_creator.create()
    summary_creator.save_to_file('yandex_mail_summary.csv')

