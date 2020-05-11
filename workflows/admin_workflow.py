from GooglePlayScraper import GooglePlayScraper
from TransactionsManager import TransactionsManager
from AspectsExtractor import AspectsExtractor
from OpinionsExtractor import OpinionsExtractor
from SentimentDictionaryCreator import SentimentDictionaryCreator
from SentimentAnalyzer import SentimentAnalyzer


if __name__ == '__main__':
    application_name = 'MailRu'

    scraper = GooglePlayScraper(application_name)
    scraper.scrap()

    transactions_manager = TransactionsManager(application_name)
    transactions_manager.load_reviews()
    transactions_manager.create_transactions()
    transactions_manager.write_transactions()

    aspects_extractor = AspectsExtractor(application_name)
    aspects_extractor.load_transactions()
    aspects_extractor.extract()
    aspects_extractor.write_aspects()

    opinions_extractor = OpinionsExtractor(application_name)
    opinions_extractor.load_reviews()
    opinions_extractor.load_aspects()
    opinions_extractor.extract()
    opinions_extractor.write_opinions()

    is_create_sentiment_dictionary = False
    if is_create_sentiment_dictionary:
        prepath = '../resourses/WordNetAffectRuRomVer2\WordNet-AffectRuRomVer2/'
        sentiment_dictionary_creator = SentimentDictionaryCreator(
            [prepath + 'joy.txt', prepath + 'surprise.txt'],
            [prepath + 'anger.txt', prepath + 'disgust.txt', prepath + 'fear.txt', prepath + 'sadness.txt'],
            '../resourses/' + 'rusentilex_2017.txt'
        )
        sentiment_dictionary_creator.create()
        sentiment_dictionary_creator.write_sentiment_dictionary()

    sentiment_analyzer = SentimentAnalyzer(application_name)
    sentiment_analyzer.load_reviews()
    sentiment_analyzer.load_sentiment_dictionary_docs()
    sentiment_analyzer.analyze()
    sentiment_analyzer.write()
