# -*- coding: utf-8 -*-
import os
import time

from threader import Threader
from TwitterAPI import TwitterAPI

from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException


class BandecoBot:
    """
    Creates a bot object that scraps the bandeco menu and uploads to twitter as a thread.
        :param meal_time: Meal time for menus, available options are 'almoco' and 'janta'
        :param weekday: Weekday name, options are 'segunda', 'terca', 'quarta', 'quinta' and 'sexta'
    """

    def __init__(self, meal_time, weekday, date):
        self.meal_time = meal_time
        self.weekday = weekday
        self.date = date
        self.codes = {
            'Central': 6,
            'Prefeitura': 7,
            'Física': 8,
            'Química': 9,
        }
        self.api = TwitterAPI(**self._get_twitter_credentials())

        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = False
        self.browser = Firefox(executable_path=GeckoDriverManager().install())

    @staticmethod
    def _get_twitter_credentials():
        credentials = dict(consumer_key=os.environ['API_KEY'],
                           consumer_secret=os.environ['API_SECRET_KEY'],
                           access_token_key=os.environ['ACCESS_TOKEN'],
                           access_token_secret=os.environ['ACCESS_TOKEN_SECRET'])
        return credentials

    def _get_bandeco_menu(self, name):
        code = self.codes[name]
        url = f'https://uspdigital.usp.br/rucard/Jsp/cardapioSAS.jsp?codrtn={code}'

        id_ = self.meal_time.replace('ç', 'c').lower() + \
              self.weekday.replace('á', 'a').replace('ç', 'c').lower().title()

        self.id_ = id_

        self.browser.get(url)
        delay = 5
        try:
            WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.ID, id_)))
            time.sleep(.5)  # Elements may took some time to load
            return self.browser.find_elements_by_id(id_)[0].text
        except TimeoutException:
            return ''

    def _get_payload(self):
        menus = ["Cardápios USP Butantã - "
                 f"{self.meal_time.title()} "
                 f"{self.weekday.title()} "
                 f"({str(self.date.day).zfill(2)}/{str(self.date.month).zfill(2)}/{self.date.year}):"]

        for name in self.codes.keys():
            menu = self._get_bandeco_menu(name)
            if menu != '':
                menu = name + ':\n\n' + self._get_bandeco_menu(name)
                menus.append(menu)

        self.browser.close()
        return menus

    def post_twitter_thread(self):
        payload = self._get_payload()

        if len(payload) > 1:
            th = Threader(payload, self.api, wait=2, end_string=False)
            th.send_tweets()

        return payload
