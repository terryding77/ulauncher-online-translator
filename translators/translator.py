# -*- coding:utf-8 -*-
from abc import abstractmethod


class Translator(object):
    @staticmethod
    def is_chinese(word):
        """判断一个unicode是否是汉字"""
        if isinstance(word, str):
            word = word.decode('utf-8')
        for uchar in word:
            if u'\u4e00' <= uchar <= u'\u9fa5':
                return True
        return False

    @staticmethod
    def detect_language(word):
        target_lang = 'zh'  # Chinese by default
        source_lang = 'en'  # English by default
        if Translator.is_chinese(word):
            target_lang, source_lang = 'en', 'zh'
        return target_lang, source_lang

    @abstractmethod
    def start(self, *values, **args):
        pass

    @abstractmethod
    def get_url(self, word):
        pass

    @abstractmethod
    def search_word(self, word):
        pass


class Item(object):
    def __init__(self, source_lang, target_lang, src, dest):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.src = src
        self.dest = dest
