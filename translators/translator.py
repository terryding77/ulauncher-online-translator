# -*- coding:utf-8 -*-
from abc import abstractmethod
from typing import Tuple, List


class Item:
    def __init__(self, source_lang: str, target_lang: str, src: str, dest: str):
        self.source_lang: str = source_lang
        self.target_lang: str = target_lang
        self.src: str = src
        self.dest: str = dest


class Translator:
    @staticmethod
    def is_chinese(word: str) -> bool:
        """判断一个unicode是否是汉字"""
        for uchar in word:
            if u'\u4e00' <= uchar <= u'\u9fa5':
                return True
        return False

    @staticmethod
    def detect_language(word: str) -> Tuple[str, str]:
        target_lang = 'zh'  # Chinese by default
        source_lang = 'en'  # English by default
        if Translator.is_chinese(word):
            target_lang, source_lang = 'en', 'zh'
        return target_lang, source_lang

    @abstractmethod
    def start(self, *values, **args):
        pass

    @abstractmethod
    def get_url(self, word: str) -> str:
        pass

    @abstractmethod
    def search_word(self, word: str) -> List[Item]:
        pass
