# -*- coding:utf-8 -*-

import logging
import os
from collections import defaultdict

from translators import Translator
from translators import translators as trans_types

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
        self.preferences = dict()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(PreferencesEvent, PreferencesEventListener())
        self.subscribe(PreferencesUpdateEvent, PreferencesUpdateEventListener())

        self.keyword = None

        self.translators = defaultdict(Translator)

        self.google_credentials = ""
        self.https_proxy = ""

    def show_menu(self):
        query = os.popen('xclip -out -selection clipboard').read()
        if isinstance(query, unicode):
            query = query.encode('utf-8')

        logging.info('剪切板中内容为 {}'.format(query))
        items = self.get_search_result(query)

        return RenderResultListAction(items)

    def get_search_result(self, word):
        items = []
        for trans_type, translator in self.translators.items():
            for item in translator.search_word(word):
                logging.debug(item)
                items.append(ExtensionResultItem(icon='images/icon.png',
                                                 name=item.dest,
                                                 description='使用{}翻译{}语单词"{}"到{}语'.format(
                                                     trans_type,
                                                     item.source_lang,
                                                     item.src,
                                                     item.target_lang
                                                 ),
                                                 on_enter=CopyToClipboardAction(item.dest)))

            translator_url = translator.get_url(word)
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name='在浏览器中使用{}翻译'.format(trans_type),
                                             description='from {} translate'.format(trans_type),
                                             on_enter=OpenUrlAction(translator_url)))
        return items

    def update_translators(self):
        trans_names = self.preferences.get('translators', '').lower().split(';')
        for name in trans_names:
            if name in trans_types:
                logging.debug("尝试初始化{}翻译器".format(name))
                if name not in self.translators:
                    self.translators[name] = trans_types[name]()

                self.translators[name].start(**self.preferences)
                logging.debug("初始化{}翻译器结束".format(name))


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        query = event.get_argument()
        if isinstance(query, unicode):
            query = query.encode('utf-8')

        if query is None:
            return extension.show_menu()
        logging.debug('查询单词为"{}"'.format(query))
        items = extension.get_search_result(query)

        return RenderResultListAction(items)


class PreferencesEventListener(EventListener):
    def on_event(self, event, extension):
        extension.preferences.update(event.preferences)
        logging.debug(extension.preferences)
        extension.update_translators()


class PreferencesUpdateEventListener(EventListener):
    def on_event(self, event, extension):
        extension.preferences[event.id] = event.new_value
        logging.debug(extension.preferences)
        extension.update_translators()


if __name__ == '__main__':
    TranslatorExtension().run()
