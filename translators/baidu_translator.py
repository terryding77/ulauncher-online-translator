# -*- coding:utf-8 -*-
import hashlib
import httplib
import json
import logging
import random
import urllib

from .translator import Translator, Item


class BaiduTranslator(Translator):
    APPID = 'baidu_appid'
    SECRET_KEY = 'baidu_secret_key'

    def __init__(self):
        self.appid = ""
        self.secretKey = ""
        self.base_translator_uri = '/api/trans/vip/translate'
        self.host = 'api.fanyi.baidu.com'

    def start(self, *values, **args):
        self.appid = args.get(BaiduTranslator.APPID, '')
        self.secretKey = args.get(BaiduTranslator.SECRET_KEY, '')

    def construct_api(self, word):
        target_lang, source_lang = self.detect_language(word)
        salt = random.randint(32768, 65536)

        sign = self.appid + word + str(salt) + self.secretKey
        m1 = hashlib.md5()
        m1.update(sign)
        sign = m1.hexdigest()

        api_url = '{}?appid={}&q={}&from={}&to={}&salt={}&sign={}'.format(
            self.base_translator_uri, self.appid, urllib.quote(word), source_lang, target_lang, salt, sign)
        logging.debug("api.fanyi.baidu.com{}".format(api_url))
        return api_url

    def search_word(self, word):
        items = []

        target_lang, source_lang = self.detect_language(word)
        if isinstance(word, unicode):
            word = word.encode('utf8')
        client = None
        try:
            client = httplib.HTTPConnection(self.host)
            client.request('GET', self.construct_api(word))

            # response是HTTPResponse对象
            response = client.getresponse()
            content = json.loads(response.read())
            logging.debug(content)
            for one_result in content.get('trans_result', []):
                src = one_result.get('src', '')
                dst = one_result.get('dst', '')
                if isinstance(src, unicode):
                    src = src.encode('utf8')
                if isinstance(dst, unicode):
                    dst = dst.encode('utf8')
                logging.debug("{}->{} {}->{}".format(source_lang, target_lang, src, dst))
                items.append(Item(source_lang, target_lang, src, dst))
        except Exception, e:
            print e
        finally:
            if client:
                client.close()
        return items

    def get_url(self, word):
        lang_dict = {}
        target_lang, source_lang = self.detect_language(word)
        base_url = 'https://fanyi.baidu.com'
        return '{}/#{}/{}/{}'.format(base_url, lang_dict.get(source_lang, source_lang),
                                     lang_dict.get(target_lang, target_lang),
                                     urllib.quote(word))
