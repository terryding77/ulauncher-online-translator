# -*- coding:utf-8 -*-
import hashlib
import http.client
import json
import logging
import random
import urllib.request

from .translator import Translator, Item


class BaiduTranslator(Translator):
    APPID = 'baidu_appid'
    SECRET_KEY = 'baidu_secret_key'

    def __init__(self):
        self.appid: str = ""
        self.secretKey: str = ""
        self.base_translator_uri: str = '/api/trans/vip/translate'
        self.host: str = 'api.fanyi.baidu.com'

    def start(self, *values, **args):
        self.appid = args.get(BaiduTranslator.APPID, '')
        self.secretKey = args.get(BaiduTranslator.SECRET_KEY, '')

    def construct_api(self, word: str) -> str:
        target_lang, source_lang = self.detect_language(word)
        salt = random.randint(32768, 65536)

        sign = f'{self.appid}{word}{salt}{self.secretKey}'
        m1 = hashlib.md5()
        m1.update(sign.encode('utf-8'))
        sign = m1.hexdigest()

        api_url = '{}?appid={}&q={}&from={}&to={}&salt={}&sign={}'.format(
            self.base_translator_uri, self.appid, urllib.request.quote(word),
            source_lang, target_lang, salt, sign)
        logging.debug(f"api.fanyi.baidu.com{api_url}")
        return api_url

    def search_word(self, word: str):
        items = []

        target_lang, source_lang = self.detect_language(word)
        client = None
        try:
            client = http.client.HTTPConnection(self.host)
            client.request('GET', self.construct_api(word))

            # response是HTTPResponse对象
            response = client.getresponse()
            content = json.loads(response.read())
            logging.debug(content)
            for one_result in content.get('trans_result', []):
                src = one_result.get('src', '')
                dst = one_result.get('dst', '')
                logging.debug(f'{source_lang}->{target_lang} {src}->{dst}')
                items.append(Item(source_lang, target_lang, src, dst))
        except Exception as e:
            print(e)
        finally:
            if client:
                client.close()
        return items

    def get_url(self, word):
        lang_dict = {}
        target_lang, source_lang = self.detect_language(word)
        base_url = 'https://fanyi.baidu.com'
        return f'{base_url}/#{lang_dict.get(source_lang, source_lang)}' \
            f'{lang_dict.get(target_lang, target_lang),}/{urllib.request.quote(word)}'
