from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

import time
import configparser

from Logger import *
from Postgres import *


class GooglePlayScraper:
    def __init__(self, application_name):
        self.config = configparser.ConfigParser()
        self.config.read('settings.ini')

        self.url_to_scrap = self.config[application_name]['url_to_scrap']
        self.database_table = self.config[application_name]['database_table']
        self.sleep_in_seconds = int(self.config['Scraper']['sleep_in_seconds'])
        self.page_to_parse_index = 0

        self.__create_driver()
        self.__create_database_connection()
        self.__create_logger(application_name)

        self.postgres.connect()

    def __create_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=chrome_options)

    def __create_database_connection(self):
        name = self.config['Database']['name']
        user = self.config['Database']['user']
        password = self.config['Database']['password']
        host = self.config['Database']['host']
        port = self.config['Database']['port']
        self.postgres = Postgres(name, user, password, host, port)

    def __create_logger(self, application_name):
        log_file = self.config[application_name]['log_file']
        self.logger = Logger(log_file)

    def skip_first_pages(self, pages_count):
        for i in range(pages_count):
            self.logger.log("Пропуск страницы номер {0}\n".format(self.page_to_parse_index))
            self.page_to_parse_index += 1

            self.__delete_reviews()
            self.__trigger_next_page()

            if self.__check_button_existence():
                self.__click_button()

            time.sleep(self.sleep_in_seconds)

    def __delete_reviews(self):
        self.driver.execute_script(
            'var root = document.querySelector("[jsname=fk8dgd]"); \
            while (root.firstChild) { \
                root.removeChild(root.firstChild); \
            }'
        )

    def __trigger_next_page(self):
        self.driver.execute_script('window.scrollBy(0, -20)')
        self.driver.execute_script(
            'window.scrollTo({top: document.body.scrollHeight, behavior: "smooth"})')

    def __check_button_existence(self):
        try:
            self.driver.find_element_by_xpath("//span[contains(./text(), 'Показать ещё')]/../..")
        except NoSuchElementException:
            return False
        return True

    def __click_button(self):
        btn = self.driver.find_element_by_xpath("//span[contains(./text(), 'Показать ещё')]/../..")
        self.driver.execute_script("arguments[0].click();", btn)

    def scrap(self):
        self.driver.get(self.url_to_scrap)
        page_to_scrap_count = int(self.config['Scraper']['page_to_scrap_count'])
        for i in range(page_to_scrap_count):
            self.logger.log("[INFO] текущая страница {0}\n".format(self.page_to_parse_index))
            self.page_to_parse_index += 1

            reviews = self.__get_reviews_containers()

            self.logger.log("[INFO] получено отзывов со страницы {0}\n".format(len(reviews)))
            print(len(reviews))

            reviews_data = self.__get_reviews_data(reviews)
            self.postgres.write(reviews_data, self.database_table)
            self.__delete_reviews()

            self.__trigger_next_page()

            if self.__check_button_existence():
                self.__click_button()

            time.sleep(self.sleep_in_seconds)
        self.driver.quit()

    def __get_reviews_containers(self):
        try:
            reviews = self.driver.find_elements_by_xpath("//div[contains(@jsname, 'fk8dgd')]/div")
            return reviews
        except Exception as e:
            self.logger.log("[ERROR] ошибка при получении отзывов со страницы: {0}\n".format(str(e)))

    def __get_reviews_data(self, reviews):
        reviews_data = []
        for review in reviews:
            name = review.find_element_by_xpath(".//span[contains(@class, 'X43Kjb')]").text
            score = review.find_element_by_xpath(".//div[contains(@role, 'img')]").get_attribute(
                "aria-label").split()[2]
            likes = review.find_element_by_xpath(".//div[contains(@class, 'jUL89d y92BAb')]").text
            date = self.__get_date(review)
            has_photo = '/photo.jpg' not in review.find_element_by_xpath(
                ".//img[contains(@class, 'T75of ZqMJr')]").get_attribute("src")

            text = review.find_element_by_xpath(".//span[contains(@jsname, 'fbQN7e')]").get_attribute('textContent')
            if text == '':
                text = review.find_element_by_xpath(".//span[contains(@jsname, 'bN97Pc')]").text
            reviews_data.append((name, score, date, likes, has_photo, text))
        return reviews_data

    def __get_date(self, review):
        date_splitted_str = review.find_element_by_xpath(".//span[contains(@class, 'p2TkOb')]").text.split()
        day = date_splitted_str[0]
        year = date_splitted_str[2]
        month_str = date_splitted_str[1]
        month_str_to_num = {'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
                            'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
                            'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'}
        month = month_str_to_num[month_str]
        return year + '-' + month + '-' + day


if __name__ == '__main__':
    application_name = 'YandexMail'
    scraper = GooglePlayScraper(application_name)
    scraper.scrap()
