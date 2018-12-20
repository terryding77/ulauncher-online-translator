# -*- coding:utf-8 -*-
import logging
import os
import urllib
from pprint import pformat

from .translator import Translator, Item
from google.cloud import translate


class GoogleTranslator(Translator):
    CREDENTIALS = 'google_credentials'
    PROXY = 'https_proxy'

    def __init__(self):
        self.client = None
        self.google_credentials = ""
        self.https_proxy = ""

    def start(self, *values, **args):
        changed = False
        google_credentials = args.get(GoogleTranslator.CREDENTIALS, '')
        https_proxy = args.get(GoogleTranslator.PROXY, '')

        if google_credentials != self.google_credentials:
            self.google_credentials = google_credentials
            changed = True
        if https_proxy != self.https_proxy:
            self.https_proxy = https_proxy
            changed = True
        if not changed:
            return

        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.google_credentials
        # '/home/username/Downloads/translate-XXX.json'
        os.environ['https_proxy'] = self.https_proxy
        os.environ['http_proxy'] = self.https_proxy
        try:
            self.client = translate.Client()
            logging.debug(pformat(self.client.get_languages()))
        except Exception as e:
            logging.error("google翻译初始化失败，{}".format(e))

    def search_word(self, word):
        if self.client is None:
            return []
        target_lang, source_lang = self.detect_language(word)
        if isinstance(word, unicode):
            word = word.encode('utf8')
        try:
            res = self.client.translate(word,
                                        target_language=target_lang,
                                        source_language=source_lang,
                                        )
        except Exception as e:
            logging.error("google翻译失败，{}".format(e))
            res = []
        logging.debug(res)
        if isinstance(res, dict):
            res = [Item(source_lang, target_lang, word, res.get('translatedText', ''))]
        return res

    def get_url(self, word):
        lang_dict = {
            'zh': 'zh-CN',

        }
        target_lang, source_lang = self.detect_language(word)
        base_url = 'https://translate.google.cn'
        return '{}/#{}/{}/{}'.format(base_url, lang_dict.get(source_lang, source_lang),
                                     lang_dict.get(target_lang, target_lang),
                                     urllib.quote(word))
