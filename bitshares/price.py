from fractions import Fraction
from bitshares.instance import shared_bitshares_instance
from .exceptions import InvalidAssetException
from .account import Account
from .amount import Amount
from .asset import Asset
from .utils import formatTimeString
from .witness import Witness
from .utils import parse_time


class Price(dict):
    """ This class deals with all sorts of prices of any pair of assets to
        simplify dealing with the tuple::

            (quote, base)

        each being an instance of :class:`bitshares.amount.Amount`. The
        amount themselves define the price.

        .. note::

            The price (floating) is derived as ``base/quote``

        :param list args: Allows to deal with different representations of a price
        :param bitshares.asset.Asset base: Base asset
        :param bitshares.asset.Asset quote: Quote asset
        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance
        :returns: All data required to represent a price
        :rtype: dict

        Way to obtain a proper instance:

            * ``args`` is a str with a price and two assets
            * ``args`` can be a floating number and ``base`` and ``quote`` being instances of :class:`bitshares.asset.Asset`
            * ``args`` can be a floating number and ``base`` and ``quote`` being instances of ``str``
            * ``args`` can be dict with keys ``price``, ``base``, and ``quote`` (*graphene balances*)
            * ``args`` can be dict with keys ``base`` and ``quote``
            * ``args`` can be dict with key ``receives`` (filled orders)
            * ``args`` being a list of ``[quote, base]`` both being instances of :class:`bitshares.amount.Amount`
            * ``args`` being a list of ``[quote, base]`` both being instances of ``str`` (``amount symbol``)
            * ``base`` and ``quote`` being instances of :class:`bitshares.asset.Amount`

        This allows instanciations like:

        * ``Price("0.315 USD/BTS")``
        * ``Price(0.315, base="USD", quote="BTS")``
        * ``Price(0.315, base=Asset("USD"), quote=Asset("BTS"))``
        * ``Price({"base": {"amount": 1, "asset_id": "1.3.0"}, "quote": {"amount": 10, "asset_id": "1.3.106"}})``
        * ``Price({"receives": {"amount": 1, "asset_id": "1.3.0"}, "pays": {"amount": 10, "asset_id": "1.3.106"}}, base_asset=Asset("1.3.0"))``
        * ``Price(quote="10 GOLD", base="1 USD")``
        * ``Price("10 GOLD", "1 USD")``
        * ``Price(Amount("10 GOLD"), Amount("1 USD"))``
        * ``Price(1.0, "USD/GOLD")``

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

        if (len(args) == 1 and isinstance(args[0], str) and not base and not quote):
            import re
            price, assets = args[0].split(" ")
            base_symbol, quote_symbol = re.split("[/-:]", assets)
            base = Asset(base_symbol, bitshares_instance=self.bitshares)
            quote = Asset(quote_symbol, bitshares_instance=self.bitshares)
            frac = Fraction(float(price)).limit_denominator(10 ** base["precision"])
            self["quote"] = Amount(amount=frac.denominator, asset=quote, bitshares_instance=self.bitshares)
            self["base"] = Amount(amount=frac.numerator, asset=base, bitshares_instance=self.bitshares)

        elif (len(args) == 1 and isinstance(args[0], dict) and
                "base" in args[0] and
                "quote" in args[0]):
            assert "price" not in args[0], "You cannot provide a 'price' this way"
            # Regular 'price' objects according to bitshares-core
            base_id = args[0]["base"]["asset_id"]
            if args[0]["base"]["asset_id"] == base_id:
                self["base"] = Amount(args[0]["base"], bitshares_instance=self.bitshares)
                self["quote"] = Amount(args[0]["quote"], bitshares_instance=self.bitshares)
            else:
                self["quote"] = Amount(args[0]["base"], bitshares_instance=self.bitshares)
                self["base"] = Amount(args[0]["quote"], bitshares_instance=self.bitshares)

        elif len(args) == 1 and isinstance(args[0], dict) and "receives" in args[0]:
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
            price = args[0]
            frac = Fraction(float(price)).limit_denominator(10 ** base["precision"])
            self["quote"] = Amount(amount=frac.denominator, asset=quote, bitshares_instance=self.bitshares)
            self["base"] = Amount(amount=frac.numerator, asset=base, bitshares_instance=self.bitshares)

        elif (len(args) == 1 and isinstance(base, str) and isinstance(quote, str)):
            price = args[0]
            base = Asset(base)
            quote = Asset(quote)
            frac = Fraction(float(price)).limit_denominator(10 ** base["precision"])
            self["quote"] = Amount(amount=frac.denominator, asset=quote, bitshares_instance=self.bitshares)
            self["base"] = Amount(amount=frac.numerator, asset=base, bitshares_instance=self.bitshares)

        elif (len(args) == 0 and isinstance(base, str) and isinstance(quote, str)):
            self["quote"] = Amount(quote, bitshares_instance=self.bitshares)
            self["base"] = Amount(base, bitshares_instance=self.bitshares)

        # len(args) > 1
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], str):
            self["base"] = Amount(args[1], bitshares_instance=self.bitshares)
            self["quote"] = Amount(args[0], bitshares_instance=self.bitshares)

        elif len(args) == 2 and isinstance(args[0], Amount) and isinstance(args[1], Amount):
            self["quote"], self["base"] = args[0], args[1]

        # len(args) == 0
        elif (isinstance(base, Amount) and isinstance(quote, Amount)):
            self["quote"] = quote
            self["base"] = base

        elif (len(args) == 2 and
                (isinstance(args[0], float) or isinstance(args[0], int)) and
                isinstance(args[1], str)):
            import re
            price = args[0]
            base_symbol, quote_symbol = re.split("[/-:]", args[1])
            base = Asset(base_symbol, bitshares_instance=self.bitshares)
            quote = Asset(quote_symbol, bitshares_instance=self.bitshares)
            frac = Fraction(float(price)).limit_denominator(10 ** base["precision"])
            self["quote"] = Amount(amount=frac.denominator, asset=quote, bitshares_instance=self.bitshares)
            self["base"] = Amount(amount=frac.numerator, asset=base, bitshares_instance=self.bitshares)

        else:
            raise ValueError("Couldn't parse 'Price'.")

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        if ("quote" in self and
                "base" in self and
                self["base"] and self["quote"]):  # don't derive price for deleted Orders
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

    def symbols(self):
        return self["base"]["symbol"], self["quote"]["symbol"]

    def as_base(self, base):
        """ Returns the price instance so that the base asset is ``base``.

            Note: This makes a copy of the object!
        """
        if base == self["base"]["symbol"]:
            return self.copy()
        elif base == self["quote"]["symbol"]:
            return self.copy().invert()
        else:
            raise InvalidAssetException

    def as_quote(self, quote):
        """ Returns the price instance so that the quote asset is ``quote``.

            Note: This makes a copy of the object!
        """
        if quote == self["quote"]["symbol"]:
            return self.copy()
        elif quote == self["base"]["symbol"]:
            return self.copy().invert()
        else:
            raise InvalidAssetException

    def invert(self):
        """ Invert the price (e.g. go from ``USD/BTS`` into ``BTS/USD``)
        """
        tmp = self["quote"]
        self["quote"] = self["base"]
        self["base"] = tmp
        return self

    def json(self):
        return {
            "base": self["base"].json(),
            "quote": self["quote"].json()
        }

    def __repr__(self):
        return "{price:.{precision}f} {base}/{quote}".format(
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
            # Rotate/invert other
            if self["quote"]["symbol"] in other.symbols():
                other = other.as_quote(self["quote"]["symbol"])
            elif self["base"]["symbol"] in other.symbols():
                other = other.as_quote(self["base"]["symbol"])
            else:
                raise InvalidAssetException
            a["base"] = Amount(float(self["base"] * other["base"]), other["base"]["symbol"])
            a["quote"] = Amount(float(self["quote"] * other["quote"]), self["quote"]["symbol"])
        elif isinstance(other, Amount):
            assert other["asset"]["id"] == self["quote"]["asset"]["id"]
            a = other.copy() * self["price"]
            a["asset"] = self["base"]["asset"].copy()
            a["symbol"] = self["base"]["asset"]["symbol"]
        else:
            a["base"] *= other
        return a

    def __imul__(self, other):
        if isinstance(other, Price):
            tmp = self * other
            self["base"] = tmp["base"]
            self["quote"] = tmp["quote"]
        else:
            self["base"] *= other
        return self

    def __div__(self, other):
        a = self.copy()
        if isinstance(other, Price):
            # Rotate/invert other
            if sorted(self.symbols()) == sorted(other.symbols()):
                return float(self.as_base(self["base"]["symbol"])) / float(other.as_base(self["base"]["symbol"]))
            elif self["quote"]["symbol"] in other.symbols():
                other = other.as_base(self["quote"]["symbol"])
            elif self["base"]["symbol"] in other.symbols():
                other = other.as_base(self["base"]["symbol"])
            else:
                raise InvalidAssetException
            a["base"] = Amount(float(self["quote"] / other["quote"]), other["quote"]["symbol"])
            a["quote"] = Amount(float(self["base"] / other["base"]), self["quote"]["symbol"])
        elif isinstance(other, Amount):
            assert other["asset"]["id"] == self["quote"]["asset"]["id"]
            a = other.copy() / self["price"]
            a["asset"] = self["base"]["asset"].copy()
            a["symbol"] = self["base"]["asset"]["symbol"]
        else:
            a["base"] /= other
        return a

    def __idiv__(self, other):
        if isinstance(other, Price):
            tmp = self / other
            self["base"] = tmp["base"]
            self["quote"] = tmp["quote"]
        else:
            self["base"] /= other
        return self

    def __floordiv__(self, other):
        raise NotImplementedError("This is not possible as the price is a ratio")

    def __ifloordiv__(self, other):
        raise NotImplementedError("This is not possible as the price is a ratio")

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
            base=self["base"]["asset"],
            quote=self["quote"]["asset"],
            bitshares_instance=self.bitshares
        )


class Order(Price):
    """ This class inherits :class:`bitshares.price.Price` but has the ``base``
        and ``quote`` Amounts not only be used to represent the price (as a
        ratio of base and quote) but instead has those amounts represent the
        amounts of an actual order!

        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance

        .. note::

                If an order is marked as deleted, it will carry the
                'deleted' key which is set to ``True`` and all other
                data be ``None``.
    """

    def __init__(self, *args, bitshares_instance=None, **kwargs):

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if (
            len(args) == 1 and
            isinstance(args[0], str)
        ):
            order = self.bitshares.rpc.get_objects([args[0]])[0]
            if order:
                super(Order, self).__init__(order["sell_price"])
                self["seller"] = order["seller"]
                self["id"] = order.get("id")
                self["deleted"] = False
            else:
                self["id"] = args[0]
                self["deleted"] = True
                self["quote"] = None
                self["base"] = None
                self["price"] = None
                self["seller"] = None
        elif (
            isinstance(args[0], dict) and
            "sell_price" in args[0]
        ):
            super(Order, self).__init__(args[0]["sell_price"])
            self["id"] = args[0].get("id")
        elif (
            isinstance(args[0], dict) and
            "min_to_receive" in args[0] and
            "amount_to_sell" in args[0]
        ):
            super(Order, self).__init__(
                Amount(args[0]["min_to_receive"], bitshares_instance=self.bitshares),
                Amount(args[0]["amount_to_sell"], bitshares_instance=self.bitshares),
            )
            self["id"] = args[0].get("id")
        elif isinstance(args[0], Amount) and isinstance(args[1], Amount):
            super(Order, self).__init__(*args, **kwargs)
        else:
            raise ValueError("Unkown format to load Order")

    def __repr__(self):
        if "deleted" in self and self["deleted"]:
            return "deleted order %s" % self["id"]
        else:
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

        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance

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
            if "account_id" in order:
                self["account_id"] = order["account_id"]

        else:
            raise ValueError("Couldn't parse 'Price'.")

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


class UpdateCallOrder(Price):
    """ This class inherits :class:`bitshares.price.Price` but has the ``base``
        and ``quote`` Amounts not only be used to represent the **call
        price** (as a ratio of base and quote).

        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance
    """
    def __init__(self, call, bitshares_instance=None, **kwargs):

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if isinstance(call, dict) and "call_price" in call:
            super(UpdateCallOrder, self).__init__(
                call.get("call_price"),
                base=call["call_price"].get("base"),
                quote=call["call_price"].get("quote"),
            )

        else:
            raise ValueError("Couldn't parse 'Call'.")

    def __repr__(self):
        t = "Margin Call: "
        if "quote" in self and self["quote"]:
            t += "%s " % str(self["quote"])
        if "base" in self and self["base"]:
            t += "%s " % str(self["base"])
        return t + "@ " + Price.__repr__(self)

    __str__ = __repr__


class PriceFeed(dict):
    """ This class is used to represent a price feed consisting of

        * a witness,
        * a symbol,
        * a core exchange rate,
        * the maintenance collateral ratio,
        * the max short squeeze ratio,
        * a settlement price, and
        * a date

        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance

    """
    def __init__(self, feed, bitshares_instance=None):
        self.bitshares = bitshares_instance or shared_bitshares_instance()
        if len(feed) == 2:
            super(PriceFeed, self).__init__({
                "producer": Account(feed[0], lazy=True),
                "date": parse_time(feed[1][0]),
                "maintenance_collateral_ratio": feed[1][1]["maintenance_collateral_ratio"],
                "maximum_short_squeeze_ratio": feed[1][1]["maximum_short_squeeze_ratio"],
                "settlement_price": Price(feed[1][1]["settlement_price"]),
                "core_exchange_rate": Price(feed[1][1]["core_exchange_rate"])
            })
        else:
            super(PriceFeed, self).__init__({
                "maintenance_collateral_ratio": feed["maintenance_collateral_ratio"],
                "maximum_short_squeeze_ratio": feed["maximum_short_squeeze_ratio"],
                "settlement_price": Price(feed["settlement_price"]),
                "core_exchange_rate": Price(feed["core_exchange_rate"])
            })
