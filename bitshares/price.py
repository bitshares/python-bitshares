import bitshares as bts
from .amount import Amount
from .asset import Asset
from .utils import formatTimeString


class Price(dict):
    def __init__(self, *args, base=None, quote=None):

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
                        self["base"] = Amount(obj["base"])
                        self["quote"] = Amount(obj["quote"])
                    else:
                        self["quote"] = Amount(obj["base"])
                        self["base"] = Amount(obj["quote"])

                # Filled order
                elif "op" in obj:
                    assert base, "Need a 'base' asset"
                    self["base"] = Asset(base)
                    if obj["op"]["receives"]["asset_id"] == base["id"]:
                        # If the seller received "base" in a quote_base market, than
                        # it has been a sell order of quote
                        self["base"] = Amount(obj["op"]["receives"])
                        self["quote"] = Amount(obj["op"]["pays"])
                    else:
                        # buy order
                        self["base"] = Amount(obj["op"]["pays"])
                        self["quote"] = Amount(obj["op"]["receives"])

                else:
                    raise ValueError("Invalid json format for Price()")

            elif (isinstance(base, Asset) and isinstance(quote, Asset)):
                    qp = quote["precision"]
                    bp = base["precision"]
                    self["quote"] = Amount({
                        "amount": 10 ** qp,
                        "asset": quote
                    })
                    self["base"] = Amount({
                        "amount": float(obj) * 10 ** bp,
                        "asset": base
                    })

            elif (isinstance(base, str) and isinstance(quote, str)):
                    self["base"] = Asset(base)
                    self["quote"] = Asset(quote)
            else:
                raise ValueError("Invalid way of calling Price()")

        elif len(args) == 2:
            if isinstance(args[0], str) and isinstance(args[1], str):
                self["quote"], self["base"] = args[0], args[1]
                self["base"] = Amount(base)
                self["quote"] = Amount(quote)

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
        t = ""
        if "time" in self and self["time"]:
            t += "(%s) " % self["time"]
        if "type" in self and self["type"]:
            t += "%s " % str(self["type"])

        if isinstance(self, Order) or isinstance(self, FilledOrder):
            if "quote" in self and self["quote"]:
                t += "%s " % str(self["quote"])
            if "base" in self and self["base"]:
                t += "%s " % str(self["base"])

        return t + "{price:.{precision}f} {base}/{quote} ".format(
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
            quote=self["quote"]
        )


class Order(Price):

    def __init__(self, *args, **kwargs):
        if (
            isinstance(args[0], dict) and
            "sell_price" in args[0]
        ):
            super(Order, self).__init__(args[0]["sell_price"])
            for k, v in args[0].items():
                self[k] = v
            self["price"] = Price(args[0]["sell_price"])
            self["quote"] = Amount(args[0]["sell_price"]["quote"])
            self["base"] = Amount(args[0]["sell_price"]["base"])

        elif (
            isinstance(args[0], dict) and
            "min_to_receive" in args[0] and
            "amount_to_sell" in args[0]
        ):
            super(Order, self).__init__(
                Amount(args[0]["min_to_receive"]),
                Amount(args[0]["amount_to_sell"]),
            )
            for k, v in args[0].items():
                self[k] = v
            self["price"] = Price(
                Amount(args[0]["min_to_receive"]),
                Amount(args[0]["amount_to_sell"])
            )
            self["quote"] = Amount(args[0]["min_to_receive"])
            self["base"] = Amount(args[0]["amount_to_sell"])

        elif isinstance(args[0], Amount) and isinstance(args[1], Amount):
            self["price"] = Price(*args, **kwargs)
            self["quote"] = args[0]
            self["base"] = args[1]
        else:
            raise ValueError("Unkown format to load Order")


class FilledOrder(Price):

    def __init__(self, order, **kwargs):
        if isinstance(order, dict) and "price" in order:
            super(FilledOrder, self).__init__(
                order.get("price"),
                base=Asset(kwargs.get("base")),
                quote=Asset(kwargs.get("quote")),
            )
            self["quote"] = Amount(
                order.get("amount"),
                kwargs.get("quote")
            )
            self["base"] = Amount(
                order.get("value"),
                kwargs.get("base")
            )
            self["time"] = formatTimeString(order["date"])
            self["price"] = Price(
                order.get("price"),
                base=Asset(kwargs.get("base")),
                quote=Asset(kwargs.get("quote")),
            )
        elif isinstance(order, dict) and "op" in order:
            quote = kwargs.get("quote")
            base = kwargs.get("base")
            super(FilledOrder, self).__init__(
                order,
                base=Asset(base),
                quote=Asset(quote),
            )
            for k, v in order.items():
                self[k] = v
            if base["id"] == order["op"]["receives"]["asset_id"]:
                self["quote"] = Amount(order["op"]["receives"])
                self["base"] = Amount(order["op"]["pays"])
                self["type"] = "buy"
            else:
                self["quote"] = Amount(order["op"]["pays"])
                self["base"] = Amount(order["op"]["receives"])
                self["type"] = "sell"

            self["time"] = formatTimeString(self["time"])
            self["price"] = Price(
                order,
                base=Asset(base),
                quote=Asset(quote),
            )
        elif (
            isinstance(order, dict) and
            "receives" in order and
            "pays" in order
        ):
            self["quote"] = Amount(order["pays"])
            self["base"] = Amount(order["receives"])
            self["time"] = None
            self["price"] = Price(
                self["base"],
                self["quote"]
            )
        else:
            raise
