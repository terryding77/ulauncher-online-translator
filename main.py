# -*- coding:utf-8 -*-
import logging
import os
import urllib
from pprint import pformat

from google.cloud import translate
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent, PreferencesEvent, PreferencesUpdateEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem


class TranslatorExtension(Extension):

    def __init__(self):
        super(TranslatorExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

        self.keyword = None

        self.client = None
        self.google_credentials = ""
        self.https_proxy = ""

    def show_menu(self):
        query = os.popen('xclip -out -selection clipboard').read()
        if isinstance(query, unicode):
            query = query.encode('utf-8')

        logging.info(query)

        items = []

        for item in search_word(self.client, query):
            logging.debug(item)
            logging.debug(item['translatedText'])
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name=item['translatedText'],
                                             description='单词"{}" in clipboard'.format(query),
                                             on_enter=CopyToClipboardAction(item['translatedText'])))

        items.append(ExtensionResultItem(icon='images/icon.png',
                                         name='search in web browser',
                                         description='from google translate',
                                         on_enter=OpenUrlAction(get_URL(query))))
        return RenderResultListAction(items)

    def set_env(self):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.google_credentials
        # '/home/username/Downloads/translate-XXX.json'
        os.environ['https_proxy'] = self.https_proxy
        # 'socks5://127.0.0.1:1080'
        self.client = translate.Client()
        logging.debug(pformat(self.client.get_languages()))


def is_chinese(word):
    """判断一个unicode是否是汉字"""
    if isinstance(word, str):
        word = word.decode('utf-8')
    for uchar in word:
        if u'\u4e00' <= uchar <= u'\u9fa5':
            return True
    return False


def detect_language(word):
    target_lang = 'zh'  # Chinese by default
    source_lang = 'en'  # English by default
    if is_chinese(word):
        target_lang, source_lang = 'en', 'zh'
    return target_lang, source_lang


def search_word(translator, word):
    if translator is None:
        return []
    target_lang, source_lang = detect_language(word)
    if isinstance(word, unicode):
        word = word.encode('utf8')
    res = translator.translate(word,
                               target_language=target_lang,
                               source_language=source_lang,
                               )
    logging.debug(res)
    if isinstance(res, dict):
        res = [res]
    return res


def get_URL(word):
    lang_dict = {
        'zh': 'zh-CN',

    }
    target_lang, source_lang = detect_language(word)
    base_url = 'https://translate.google.cn'
    return '{}/#{}/{}/{}'.format(base_url, lang_dict.get(source_lang, source_lang),
                                 lang_dict.get(target_lang, target_lang),
                                 urllib.quote(word))


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument()
        if isinstance(query, unicode):
            query = query.encode('utf-8')

        if query is None:
            return extension.show_menu()
        logging.debug("单词为{}".format(query))
        items = []
        for item in search_word(extension.client, query):
            logging.debug(item)
            logging.debug(item['translatedText'])
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name=item['translatedText'],
                                             description='from google translate',
                                             on_enter=CopyToClipboardAction(item['translatedText'])))
        items.append(ExtensionResultItem(icon='images/icon.png',
                                         name='search in web browser',
                                         description='from google translate',
                                         on_enter=OpenUrlAction(get_URL(query))))

        return RenderResultListAction(items)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.google_credentials = event.preferences['google_credentials']
        logging.debug(extension.google_credentials)
        extension.https_proxy = event.preferences['https_proxy']
        logging.debug(extension.https_proxy)
        extension.set_env()


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        if event.id == 'google_credentials':
            extension.google_credentials = event.new_value
            logging.debug(extension.google_credentials)
        elif event.id == 'https_proxy':
            extension.https_proxy = event.new_value
            logging.debug(extension.https_proxy)
        extension.set_env()


if __name__ == '__main__':
    TranslatorExtension().run()
