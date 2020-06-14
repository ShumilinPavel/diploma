from review_scraping.GooglePlayScraper import GooglePlayScraper
from aspect_extraction.TransactionsManager import TransactionsManager
from aspect_extraction.AspectsExtractor import AspectsExtractor
from sentiment_analysis.OpinionsExtractor import OpinionsExtractor
from SentimentDictionaryCreator import SentimentDictionaryCreator
from sentiment_analysis.SentimentAnalyzer import SentimentAnalyzer


if __name__ == '__main__':
    application_name = 'test'
    config_file_name = '../settings.ini'

    scraper = GooglePlayScraper(application_name, config_file_name)
    scraper.scrap()

    transactions_manager = TransactionsManager(application_name, config_file_name)
    transactions_manager.load_reviews()
    transactions_manager.create_transactions()
    transactions_manager.write_transactions()

    aspects_extractor = AspectsExtractor(application_name, config_file_name)
    aspects_extractor.load_transactions()
    aspects_extractor.extract()
    aspects_extractor.write_aspects()

    opinions_extractor = OpinionsExtractor(application_name, config_file_name)
    opinions_extractor.load_reviews()
    opinions_extractor.load_aspects()
    opinions_extractor.extract()
    opinions_extractor.write_opinions()

    is_create_sentiment_dictionary = False
    if is_create_sentiment_dictionary:
        prepath = '../resources/WordNet-AffectRuRomVer2/'
        sentiment_dictionary_creator = SentimentDictionaryCreator(
            [prepath + 'joy.txt', prepath + 'surprise.txt'],
            [prepath + 'anger.txt', prepath + 'disgust.txt', prepath + 'fear.txt', prepath + 'sadness.txt'],
            '../resources/' + 'rusentilex_2017.txt'
        )
        sentiment_dictionary_creator.create()
        sentiment_dictionary_creator.write_sentiment_dictionary()

    sentiment_analyzer = SentimentAnalyzer(application_name, config_file_name)
    sentiment_analyzer.load_reviews()
    sentiment_analyzer.load_sentiment_dictionary_docs()
    sentiment_analyzer.analyze()
    sentiment_analyzer.write()
