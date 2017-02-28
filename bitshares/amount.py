from bitshares.instance import shared_bitshares_instance
from .asset import Asset


class Amount(dict):
    def __init__(self, *args, amount=None, asset=None, bitshares_instance=None):
        self["asset"] = {}

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if len(args) == 1 and isinstance(args[0], Amount):
            # Copy Asset object
            self["amount"] = args[0]["amount"]
            self["symbol"] = args[0]["symbol"]
            self["asset"] = args[0]["asset"]

        elif len(args) == 1 and isinstance(args[0], str):
            self["amount"], self["symbol"] = args[0].split(" ")
            self["asset"] = Asset(self["symbol"])

        elif (len(args) == 1 and
                isinstance(args[0], dict) and
                "amount" in args[0] and
                "asset_id" in args[0]):
            self["asset"] = Asset(args[0]["asset_id"])
            self["symbol"] = self["asset"]["symbol"]
            self["amount"] = int(args[0]["amount"]) / 10 ** self["asset"]["precision"]

        elif (len(args) == 1 and
                isinstance(args[0], dict) and
                "amount" in args[0] and
                "asset" in args[0]):
            self["asset"] = Asset(args[0]["asset"])
            self["symbol"] = self["asset"]["symbol"]
            self["amount"] = int(args[0]["amount"]) / 10 ** self["asset"]["precision"]

        elif len(args) == 2 and isinstance(args[1], Asset):
            self["amount"] = args[0]
            self["symbol"] = args[1]["symbol"]
            self["asset"] = args[1]

        elif len(args) == 2 and isinstance(args[1], str):
            self["amount"] = args[0]
            self["asset"] = Asset(args[1])
            self["symbol"] = self["asset"]["symbol"]

        elif amount and asset:
            self["amount"] = amount
            self["asset"] = asset
            self["symbol"] = self["asset"]["symbol"]

        else:
            raise

        # make sure amount is a float
        self["amount"] = float(self["amount"])

    def copy(self):
        return Amount(
            amount=self["amount"],
            asset=self["asset"].copy())

    @property
    def amount(self):
        return self["amount"]

    @property
    def symbol(self):
        return self["symbol"]

    @property
    def asset(self):
        if not self["asset"]:
            self["asset"] = Asset(self["symbol"], bitshares_instance=self.bitshares)
        return self["asset"]

    def __str__(self):
        return "{:,.{prec}f} {}".format(
            self["amount"],
            self["symbol"],
            prec=self["asset"]["precision"]
        )

    def __float__(self):
        return self["amount"]

    def __int__(self):
        return int(self["amount"] * 10 ** self["asset"]["precision"])

    def __add__(self, other):
        a = Amount(self)
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            a["amount"] += other["amount"]
        else:
            a["amount"] += float(other)
        return a

    def __sub__(self, other):
        a = Amount(self)
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            a["amount"] -= other["amount"]
        else:
            a["amount"] -= float(other)
        return a

    def __mul__(self, other):
        a = Amount(self)
        if isinstance(other, Amount):
            a["amount"] *= other["amount"]
        else:
            a["amount"] *= other
        return a

    def __floordiv__(self, other):
        a = Amount(self)
        if isinstance(other, Amount):
            from .price import Price
            return Price(self, other)
        else:
            a["amount"] //= other
        return a

    def __div__(self, other):
        a = Amount(self)
        if isinstance(other, Amount):
            from .price import Price
            return Price(self, other)
        else:
            a["amount"] /= other
        return a

    def __mod__(self, other):
        a = Amount(self)
        if isinstance(other, Amount):
            a["amount"] %= other["amount"]
        else:
            a["amount"] %= other
        return a

    def __pow__(self, other):
        a = Amount(self)
        if isinstance(other, Amount):
            a["amount"] **= other["amount"]
        else:
            a["amount"] **= other
        return a

    def __iadd__(self, other):
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            self["amount"] += other["amount"]
        else:
            self["amount"] += other
        return self

    def __isub__(self, other):
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            self["amount"] -= other["amount"]
        else:
            self["amount"] -= other
        return self

    def __imul__(self, other):
        if isinstance(other, Amount):
            self["amount"] *= other["amount"]
        else:
            self["amount"] *= other
        return self

    def __idiv__(self, other):
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            return self["amount"] / other["amount"]
        else:
            self["amount"] /= other
            return self

    def __ifloordiv__(self, other):
        if isinstance(other, Amount):
            self["amount"] //= other["amount"]
        else:
            self["amount"] //= other
        return self

    def __imod__(self, other):
        if isinstance(other, Amount):
            self["amount"] %= other["amount"]
        else:
            self["amount"] %= other
        return self

    def __ipow__(self, other):
        self["amount"] **= other
        return self

    def __lt__(self, other):
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            return self["amount"] < other["amount"]
        else:
            return self["amount"] < float(other or 0)

    def __le__(self, other):
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            return self["amount"] <= other["amount"]
        else:
            return self["amount"] <= float(other or 0)

    def __eq__(self, other):
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            return self["amount"] == other["amount"]
        else:
            return self["amount"] == float(other or 0)

    def __ne__(self, other):
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            return self["amount"] != other["amount"]
        else:
            return self["amount"] != float(other or 0)

    def __ge__(self, other):
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            return self["amount"] >= other["amount"]
        else:
            return self["amount"] >= float(other or 0)

    def __gt__(self, other):
        if isinstance(other, Amount):
            assert other["asset"] == self["asset"]
            return self["amount"] > other["amount"]
        else:
            return self["amount"] > float(other or 0)

    __repr__ = __str__
    __truediv__ = __div__
    __truemul__ = __mul__
