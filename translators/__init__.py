from .translator import Translator
from .baidu_translator import BaiduTranslator
from .google_translator import GoogleTranslator

translators = {
    'baidu': BaiduTranslator,
    'google': GoogleTranslator,
}
__all__ = [
    'Translator',
    'translators',
]
