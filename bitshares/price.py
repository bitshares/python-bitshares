from . import bitshares as bts
from .amount import Amount
from .asset import Asset


class Price(dict):
    def __init__(self, *args, base=None, quote=None):

        if len(args) == 1:
            obj = args[0]

            if isinstance(obj, dict):
                # Copy price object
                if ("price" in obj and
                        "base" in obj and
                        "quote" in obj):
                    base = obj["base"]
                    quote = obj["quote"]
                    price = obj["price"]

                # Regular 'price' objects according to bitshares-core
                elif "base" in obj and "quote" in obj:
                    if base:
                        base_id = Asset(base)
                    else:
                        base_id = obj["base"]["asset_id"]
                    if obj["base"]["asset_id"] == base_id:
                        base = Amount(obj["base"])
                        quote = Amount(obj["quote"])
                    else:
                        quote = Amount(obj["base"])
                        base = Amount(obj["quote"])
                    price = self._safedivide(base["amount"], quote["amount"])

                # Filled order
                elif "op" in obj:
                    assert base, "Need a 'base' asset"
                    base = Asset(base)
                    if obj["op"]["receives"]["asset_id"] == base["id"]:
                        # If the seller received "base" in a quote_base market, than
                        # it has been a sell order of quote
                        base = Amount(obj["op"]["receives"])
                        quote = Amount(obj["op"]["pays"])
                    else:
                        # buy order
                        base = Amount(obj["op"]["pays"])
                        quote = Amount(obj["op"]["receives"])
                    price = self._safedivide(base["amount"], quote["amount"])

                else:
                    raise ValueError("Invalid json format for Price()")

            elif (isinstance(base, Asset) and isinstance(quote, Asset)):
                    qp = quote["precision"]
                    bp = base["precision"]
                    quote = Amount({
                        "amount": 10 ** qp,
                        "asset": quote
                    })
                    base = Amount({
                        "amount": float(obj) * 10 ** bp,
                        "asset": base
                    })
                    price = self._safedivide(base["amount"], quote["amount"])

            elif (isinstance(base, str) and isinstance(quote, str)):
                    price = float(obj)
                    base = Asset(base)
                    quote = Asset(quote)

            else:
                raise ValueError("Invalid way of calling Price()")

        elif len(args) == 2:
            if isinstance(args[0], str) and isinstance(args[1], str):
                quote, base = args[0], args[1]
                base = Amount(base)
                quote = Amount(quote)
                price = self._safedivide(base["amount"], quote["amount"])

            if isinstance(args[0], Amount) and isinstance(args[1], Amount):
                quote, base = args[0], args[1]
                price = self._safedivide(base["amount"], quote["amount"])
        else:
            raise Exception

        super(Price, self).__init__({
            "base": base,
            "quote": quote,
            "price": price
        })

    def _safedivide(self, a, b):
        if b != 0.0:
            return a / b
        else:
            return float('Inf')

    def __repr__(self):
        return "%f %s/%s" % (
            self["price"],
            self["base"].symbol,
            self["quote"].symbol
        )

    def __float__(self):
        return self["price"]

    def normalize(self):
        return float(int(self["price"] * (
            10 ** (self["base"]["precision"] - self["quote"]["precision"])) /
            10 ** (self["base"]["precision"] - self["quote"]["precision"])
        ))

    def __div__(self, other):
        if isinstance(other, Price):
            return self["price"] / other["price"]
        else:
            return self["price"] / other

    def __floordiv__(self, other):
        if isinstance(other, Price):
            return self["price"] // other["price"]
        else:
            return self["price"] // other

    def __idiv__(self, other):
        if isinstance(other, Price):
            assert other["asset"] == self["asset"]
            return self["price"] / other["price"]
        else:
            self["price"] /= other
            return self

    def __ifloordiv__(self, other):
        if isinstance(other, Price):
            self["price"] //= other["price"]
        else:
            self["price"] //= other
        return self

    __truediv__ = __div__
    __str__ = __repr__


class Order(Price):

    def __init__(self, *args, **kwargs):
        if isinstance(args[0], dict) and "sell_price" in args[0]:
            super(Order, self).__init__(args[0]["sell_price"])
            for k, v in args[0].items():
                self[k] = v
        else:
            super(Order, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "%f %s/%s (%s|%s)" % (
            self["price"],
            self["base"].symbol,
            self["quote"].symbol,
            str(self["base"]),
            str(self["quote"])
        )

    __str__ = __repr__


class FilledOrder(Price):

    def __init__(self, order, **kwargs):
        super(FilledOrder, self).__init__(
            order.get("price"),
            base=Asset(kwargs.get("base")),
            quote=Asset(kwargs.get("quote")),
        )
        self["quote_amount"] = Amount(
            order.get("amount"),
            kwargs.get("quote")
        )
        self["base_amount"] = Amount(
            order.get("value"),
            kwargs.get("base")
        )

    def __repr__(self):
        return "%f %s/%s (%s|%s)" % (
            self["price"],
            self["base"].symbol,
            self["quote"].symbol,
            str(self["quote_amount"]),
            str(self["base_amount"]),
        )

    __str__ = __repr__
