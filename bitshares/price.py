from bitshares.instance import shared_bitshares_instance
from .amount import Amount
from .asset import Asset
from .utils import formatTimeString


class Price(dict):
    def __init__(
        self,
        *args,
        base=None,   # base amount
        quote=None,  # quote amount
        base_asset=None,  # to identify sell/buy
        bitshares_instance=None
    ):

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if len(args) == 1:
            obj = args[0]

            if isinstance(obj, dict):
                # Copy price object
                if ("price" in obj and
                        "base" in obj and
                        "quote" in obj):
                    self["base"] = obj["base"]
                    self["quote"] = obj["quote"]

                # Regular 'price' objects according to bitshares-core
                elif "base" in obj and "quote" in obj:
                    base_id = obj["base"]["asset_id"]
                    if obj["base"]["asset_id"] == base_id:
                        self["base"] = Amount(obj["base"], bitshares_instance=self.bitshares)
                        self["quote"] = Amount(obj["quote"], bitshares_instance=self.bitshares)
                    else:
                        self["quote"] = Amount(obj["base"], bitshares_instance=self.bitshares)
                        self["base"] = Amount(obj["quote"], bitshares_instance=self.bitshares)

                # Filled order
                elif "receives" in obj:
                    assert base_asset, "Need a 'base_asset' asset"
                    base_asset = Asset(base_asset)
                    if obj["receives"]["asset_id"] == base_asset["id"]:
                        # If the seller received "base" in a quote_base market, than
                        # it has been a sell order of quote
                        self["base"] = Amount(obj["receives"], bitshares_instance=self.bitshares)
                        self["quote"] = Amount(obj["pays"], bitshares_instance=self.bitshares)
                        self["type"] = "sell"
                    else:
                        # buy order
                        self["base"] = Amount(obj["pays"], bitshares_instance=self.bitshares)
                        self["quote"] = Amount(obj["receives"], bitshares_instance=self.bitshares)
                        self["type"] = "buy"

                else:
                    raise ValueError("Invalid json format for Price()")

            elif (isinstance(base, Asset) and isinstance(quote, Asset)):
                    qp = quote["precision"]
                    bp = base["precision"]
                    self["quote"] = Amount({
                        "amount": 10 ** qp,
                        "asset": quote
                    }, bitshares_instance=self.bitshares)
                    self["base"] = Amount({
                        "amount": float(obj) * 10 ** bp,
                        "asset": base
                    }, bitshares_instance=self.bitshares)

            elif (isinstance(base, str) and isinstance(quote, str)):
                    quote = Asset(quote, bitshares_instance=self.bitshares)
                    base = Asset(base, bitshares_instance=self.bitshares)
                    self["quote"] = Amount({
                        "amount": 10 ** quote["precision"],
                        "asset": quote
                    }, bitshares_instance=self.bitshares)
                    self["base"] = Amount({
                        "amount": float(obj) * 10 ** base["precision"],
                        "asset": base
                    }, bitshares_instance=self.bitshares)

            elif (isinstance(base, Amount) and isinstance(quote, Amount)):
                    self["quote"] = quote
                    self["base"] = base

            else:
                raise ValueError("Invalid way of calling Price()")

        elif len(args) == 2:
            if isinstance(args[0], str) and isinstance(args[1], str):
                self["quote"], self["base"] = args[0], args[1]
                self["base"] = Amount(base, bitshares_instance=self.bitshares)
                self["quote"] = Amount(quote, bitshares_instance=self.bitshares)

            if isinstance(args[0], Amount) and isinstance(args[1], Amount):
                self["quote"], self["base"] = args[0], args[1]

            else:
                raise ValueError("Invalid way of calling Price()")

        elif base and quote:
            self["base"] = base
            self["quote"] = quote

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
        tmp = self["quote"]
        self["quote"] = self["base"]
        self["base"] = tmp
        self["price"] = self._safedivide(
            self["base"]["amount"],
            self["quote"]["amount"]
        )
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

    def normalize(self):
        return float(int(self["price"] * (
            10 ** (self["base"]["precision"] - self["quote"]["precision"])) /
            10 ** (self["base"]["precision"] - self["quote"]["precision"])
        ))

    def __mul__(self, other):
        a = self.copy()
        if isinstance(other, Price):
            raise ValueError("Multiplication of two prices!?")
        else:
            a["quote"]["amount"] *= other
            a["price"] *= other
#            a["price"] = self._safedivide(
#                a["base"]["amount"],
#                a["quote"]["amount"]
#            )
        return a

    def __imul__(self, other):
        if isinstance(other, Price):
            raise ValueError("Multiplication of two prices!?")
        else:
            self["quote"]["amount"] *= other
            self["price"] = self._safedivide(
                self["base"]["amount"],
                self["quote"]["amount"]
            )
        return self

    def __div__(self, other):
        a = self.copy()
        if isinstance(other, Price):
            raise ValueError("Division of two prices!?")
        else:
            a["quote"]["amount"] /= other
            a["price"] = self._safedivide(
                a["base"]["amount"],
                a["quote"]["amount"]
            )

    def __idiv__(self, other):
        if isinstance(other, Price):
            raise ValueError("Division of two prices!?")
        else:
            self["quote"]["amount"] /= other
            self["price"] = self._safedivide(
                self["base"]["amount"],
                self["quote"]["amount"]
            )
        return self

    def __floordiv__(self, other):
        a = self.copy()
        if isinstance(other, Price):
            raise ValueError("Division of two prices!?")
        else:
            a["quote"]["amount"] //= other
            a["price"] = self._safedivide(
                a["base"]["amount"],
                a["quote"]["amount"]
            )

    def __ifloordiv__(self, other):
        if isinstance(other, Price):
            raise ValueError("Division of two prices!?")
        else:
            self["quote"]["amount"] //= other
            self["price"] = self._safedivide(
                self["base"]["amount"],
                self["quote"]["amount"]
            )
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
    __str__ = __repr__

    @property
    def market(self):
        from .market import Market
        return Market(
            base=self["base"],
            quote=self["quote"],
            bitshares_instance=self.bitshares
        )


class Order(Price):

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


# TODO: fix this in combination with `openorders`
# FilledOrder should just be a wrapper to Price and not have Price as value of
# a key!
class FilledOrder(Price):

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
