from bitshares.instance import shared_bitshares_instance
from .amount import Amount
from .asset import Asset
from .utils import formatTimeString


class Price(dict):
    """ This class deals with all sorts of prices of any pair of assets to
        simplify dealing with the tuple::

            (quote_amount, quote_asset, base_amount, base_asset)

        The price (floating) is derived as ``base_amount/quote_amount`` and
        carries the unit ``base/quote``

        :param list args: Allows to deal with different representations of a price
        :param bitshares.asset.Asset base: Base asset
        :param bitshares.asset.Asset quote: Quote asset
        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance
        :returns: All data required to represent a price
        :rtype: dict

        Way to obtain a proper instance:

            * ``args`` is a str with a price and two assets (i.e. ``0.315 USD/BTS``)
            * ``args`` can be a floating number and ``base`` and ``quote`` being instances of :class:`bitshares.asset.Asset`
            * ``args`` can be a floating number and ``base`` and ``quote`` being instances of ``str``
            * ``args`` can be dict with keys ``price``, ``base``, and ``quote``
            * ``args`` can be dict with keys ``base`` and ``quote``
            * ``args`` can be dict with key ``receives`` (filled orders)
            * ``args`` being a list of ``[quote, base]`` both being instances of :class:`bitshares.amount.Amount`
            * ``args`` being a list of ``[quote, base]`` both being instances of ``str`` (``amount symbol``)
            * ``base`` and ``quote`` being instances of :class:`bitshares.asset.Amount`

        Instances of this class can be used in regular mathematical expressions
        (``+-*/%``) such as:

        .. code-block:: python

            >>> from bitshares.price import Price
            >>> Price("0.3314 USD/BTS") * 2
            0.662600000 USD/BTS 

    """
    def __init__(
        self,
        *args,
        base=None,
        quote=None,
        base_asset=None,  # to identify sell/buy
        bitshares_instance=None
    ):

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        # len(args) == 0
        if (len(args) == 1 and isinstance(args[0], dict) and (
            "price" in args[0] and
            "base" in args[0] and
            "quote" in args[0])
        ):
            self["base"] = args[0]["base"]
            self["quote"] = args[0]["quote"]

        elif (len(args) == 1 and isinstance(args[0], str) and not base and not quote):
            import re
            price, assets = args[0].split(" ")
            base_symbol, quote_symbol = re.split("[/-:]", assets)
            base = Asset(base_symbol, bitshares_instance=self.bitshares)
            quote = Asset(quote_symbol, bitshares_instance=self.bitshares)
            self["quote"] = Amount(amount=1, asset=quote, bitshares_instance=self.bitshares)
            self["base"] = Amount(amount=float(price), asset=base, bitshares_instance=self.bitshares)

        elif (len(args) == 1 and isinstance(args[0], dict) and
            "base" in args[0] and
            "quote" in obj
        ):
            # Regular 'price' objects according to bitshares-core
            base_id = args[0]["base"]["asset_id"]
            if args[0]["base"]["asset_id"] == base_id:
                self["base"] = Amount(args[0]["base"], bitshares_instance=self.bitshares)
                self["quote"] = Amount(args[0]["quote"], bitshares_instance=self.bitshares)
            else:
                self["quote"] = Amount(args[0]["base"], bitshares_instance=self.bitshares)
                self["base"] = Amount(args[0]["quote"], bitshares_instance=self.bitshares)

        elif len(args) == 1 and isinstance(args[0], dict) and "receives" in obj:
            # Filled order
            assert base_asset, "Need a 'base_asset' asset"
            base_asset = Asset(base_asset)
            if args[0]["receives"]["asset_id"] == base_asset["id"]:
                # If the seller received "base" in a quote_base market, than
                # it has been a sell order of quote
                self["base"] = Amount(args[0]["receives"], bitshares_instance=self.bitshares)
                self["quote"] = Amount(args[0]["pays"], bitshares_instance=self.bitshares)
                self["type"] = "sell"
            else:
                # buy order
                self["base"] = Amount(args[0]["pays"], bitshares_instance=self.bitshares)
                self["quote"] = Amount(args[0]["receives"], bitshares_instance=self.bitshares)
                self["type"] = "buy"

        elif len(args) == 1 and (isinstance(base, Asset) and isinstance(quote, Asset)):
            self["quote"] = Amount(amount=1, asset=quote, bitshares_instance=self.bitshares)
            self["base"] = Amount(amount=float(args[0]), asset=base, bitshares_instance=self.bitshares)

        elif (len(args) == 1 and isinstance(base, str) and isinstance(quote, str)):
            self["quote"] = Amount(amount=1, asset=quote, bitshares_instance=self.bitshares)
            self["base"] = Amount(amount=float(args[0]), asset=base, bitshares_instance=self.bitshares)

        # len(args) > 1
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            self["quote"], self["base"] = args[0], args[1]
            self["base"] = Amount(base, bitshares_instance=self.bitshares)
            self["quote"] = Amount(quote, bitshares_instance=self.bitshares)

        elif len(args) == 2 and isinstance(args[0], Amount) and isinstance(args[1], Amount):
            self["quote"], self["base"] = args[0], args[1]

        # len(args) == 0
        elif (isinstance(base, Amount) and isinstance(quote, Amount)):
            self["quote"] = quote
            self["base"] = base

        else:
            raise Exception

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if "quote" in self and "base" in self:
            dict.__setitem__(self, "price", self._safedivide(
                self["base"]["amount"],
                self["quote"]["amount"]))

    def copy(self):
        return Price(
            base=self["base"].copy(),
            quote=self["quote"].copy())

    def _safedivide(self, a, b):
        if b != 0.0:
            return a / b
        else:
            return float('Inf')

    def invert(self):
        """ Invert the price (e.g. go from ``USD/BTS`` into ``BTS/USD``)
        """
        tmp = self["quote"]
        self["quote"] = self["base"]
        self["base"] = tmp
        return self

    def __repr__(self):
        return "{price:.{precision}f} {base}/{quote} ".format(
            price=self["price"],
            base=self["base"]["symbol"],
            quote=self["quote"]["symbol"],
            precision=(
                self["base"]["asset"]["precision"] +
                self["quote"]["asset"]["precision"]
            )
        )

    def __float__(self):
        return self["price"]

    def __mul__(self, other):
        a = self.copy()
        if isinstance(other, Price):
            raise ValueError("Multiplication of two prices!?")
        else:
            a["base"] *= other
        return a

    def __imul__(self, other):
        if isinstance(other, Price):
            raise ValueError("Multiplication of two prices!?")
        else:
            self["base"] *= other
        return self

    def __div__(self, other):
        a = self.copy()
        if isinstance(other, Price):
            raise ValueError("Division of two prices!?")
        else:
            a["base"] /= other
        return a

    def __idiv__(self, other):
        if isinstance(other, Price):
            raise ValueError("Division of two prices!?")
        else:
            self["base"] /= other
        return self

    def __floordiv__(self, other):
        a = self.copy()
        if isinstance(other, Price):
            raise ValueError("Division of two prices!?")
        else:
            a["base"] //= other

    def __ifloordiv__(self, other):
        if isinstance(other, Price):
            raise ValueError("Division of two prices!?")
        else:
            self["base"] //= other
        return self

    def __lt__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["base"]["symbol"]
            return self["price"] < other["price"]
        else:
            return self["price"] < float(other or 0)

    def __le__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["base"]["symbol"]
            return self["price"] <= other["price"]
        else:
            return self["price"] <= float(other or 0)

    def __eq__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["base"]["symbol"]
            return self["price"] == other["price"]
        else:
            return self["price"] == float(other or 0)

    def __ne__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["base"]["symbol"]
            return self["price"] != other["price"]
        else:
            return self["price"] != float(other or 0)

    def __ge__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["base"]["symbol"]
            return self["price"] >= other["price"]
        else:
            return self["price"] >= float(other or 0)

    def __gt__(self, other):
        if isinstance(other, Price):
            assert other["base"]["symbol"] == self["base"]["symbol"]
            assert other["quote"]["symbol"] == self["base"]["symbol"]
            return self["price"] > other["price"]
        else:
            return self["price"] > float(other or 0)

    __truediv__ = __div__
    __truemul__ = __mul__
    __str__ = __repr__

    @property
    def market(self):
        """ Open the corresponding market

            :returns: Instance of :class:`bitshares.market.Market` for the
                      corresponding pair of assets.
        """
        from .market import Market
        return Market(
            base=self["base"],
            quote=self["quote"],
            bitshares_instance=self.bitshares
        )


class Order(Price):
    """ This class inherits :class:`bitshares.price.Price` but has the ``base``
        and ``quote`` Amounts not only be used to represent the price (as a
        ratio of base and quote) but instead has those amounts represent the
        amounts of an actual order!
    """

    def __init__(self, *args, bitshares_instance=None, **kwargs):

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if (
            isinstance(args[0], dict) and
            "sell_price" in args[0]
        ):
            super(Order, self).__init__(args[0]["sell_price"])
        elif (
            isinstance(args[0], dict) and
            "min_to_receive" in args[0] and
            "amount_to_sell" in args[0]
        ):
            super(Order, self).__init__(
                Amount(args[0]["min_to_receive"], bitshares_instance=self.bitshares),
                Amount(args[0]["amount_to_sell"], bitshares_instance=self.bitshares),
            )
        elif isinstance(args[0], Amount) and isinstance(args[1], Amount):
            super(Order, self).__init__(*args, **kwargs)
        else:
            raise ValueError("Unkown format to load Order")

    def __repr__(self):
        t = ""
        if "time" in self and self["time"]:
            t += "(%s) " % self["time"]
        if "type" in self and self["type"]:
            t += "%s " % str(self["type"])
        if "quote" in self and self["quote"]:
            t += "%s " % str(self["quote"])
        if "base" in self and self["base"]:
            t += "%s " % str(self["base"])
        return t + "@ " + Price.__repr__(self)

    __str__ = __repr__


class FilledOrder(Price):
    """ This class inherits :class:`bitshares.price.Price` but has the ``base``
        and ``quote`` Amounts not only be used to represent the price (as a
        ratio of base and quote) but instead has those amounts represent the
        amounts of an actually filled order!

        .. note:: Instances of this class come with an additional ``time`` key
                  that shows when the order has been filled!
    """

    def __init__(self, order, bitshares_instance=None, **kwargs):

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if isinstance(order, dict) and "price" in order:
            super(FilledOrder, self).__init__(
                order.get("price"),
                base=kwargs.get("base"),
                quote=kwargs.get("quote"),
            )
            self["time"] = formatTimeString(order["date"])

        elif isinstance(order, dict):
            # filled orders from account history
            if "op" in order:
                order = order["op"]
            base_asset = kwargs.get("base_asset", order["receives"]["asset_id"])
            super(FilledOrder, self).__init__(
                order,
                base_asset=base_asset,
            )
            if "time" in order:
                self["time"] = formatTimeString(order["time"])

        else:
            raise

    def __repr__(self):
        t = ""
        if "time" in self and self["time"]:
            t += "(%s) " % self["time"]
        if "type" in self and self["type"]:
            t += "%s " % str(self["type"])
        if "quote" in self and self["quote"]:
            t += "%s " % str(self["quote"])
        if "base" in self and self["base"]:
            t += "%s " % str(self["base"])
        return t + "@ " + Price.__repr__(self)

    __str__ = __repr__
