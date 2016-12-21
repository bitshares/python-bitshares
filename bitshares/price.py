from . import bitshares as bts
from .amount import Amount


class Price(dict):
    def __init__(self, quote, base):
        self.base = Amount(base)
        self.quote = Amount(quote)
        self.price = quote / base
