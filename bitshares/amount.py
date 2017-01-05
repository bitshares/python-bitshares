from . import bitshares as bts
from .asset import Asset


class Amount(object):
    def __init__(self, *args, bitshares_instance=None):
        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance

        if len(args) == 1 and isinstance(args[0], Amount):
            amount = args[0].amount
            asset = args[0].symbol
        elif (len(args) == 1 and
                isinstance(args[0], dict) and 
                "amount" in args[0] and
                "asset_id" in args[0]):
            asset = Asset(args[0]["asset_id"])
            amount = int(args[0]["amount"]) / 10 ** asset["precision"]
        elif len(args) == 2:
            amount = args[0]
            asset = args[1]
        else:
            raise

        self.amount = float(amount)

        if isinstance(asset, dict):
            self.symbol = asset["symbol"]
            self._asset = asset
        else:
            self.symbol = asset
            self._asset = None

    @property
    def asset(self):
        if not self._asset:
            self._asset = Asset(self.symbol, bitshares_instance=self.bitshares)
        return self._asset

    def __str__(self):
        return "{:.{prec}f} {}".format(
            self.amount,
            self.symbol,
            prec=self.asset["precision"]
        )

    def __float__(self):
        return self.amount

    def __int__(self):
        return int(self.amount * 10 ** self.asset["precision"])

    def __add__(self, other):
        a = Amount(str(self))
        if isinstance(other, Amount):
            assert other.asset == self.asset
            a.amount += other.amount
        else:
            a.amount += float(other)
        return a

    def __sub__(self, other):
        a = Amount(str(self))
        if isinstance(other, Amount):
            assert other.asset == self.asset
            a.amount -= other.amount
        else:
            a.amount -= float(other)
        return a

    def __mul__(self, other):
        a = Amount(str(self))
        a.amount *= other
        return a

    def __floordiv__(self, other):
        a = Amount(str(self))
        a.amount //= other
        return a

    def __div__(self, other):
        a = Amount(str(self))
        a.amount /= other
        return a

    def __mod__(self, other):
        a = Amount(str(self))
        a.amount %= other
        return a

    def __pow__(self, other):
        a = Amount(str(self))
        a.amount **= other
        return a

    def __iadd__(self, other):
        if isinstance(other, Amount):
            assert other.asset == self.asset
            self.amount += other.amount
        else:
            self.amount += other
        return self

    def __isub__(self, other):
        if isinstance(other, Amount):
            assert other.asset == self.asset
            self.amount -= other.amount
        else:
            self.amount -= other
        return self

    def __imul__(self, other):
        self.amount *= other
        return self

    def __idiv__(self, other):
        if isinstance(other, Amount):
            assert other.asset == self.asset
            return self.amount / other.amount
        else:
            self.amount /= other
            return self

    def __ifloordiv__(self, other):
        self.amount //= other
        return self

    def __imod__(self, other):
        self.amount %= other
        return self

    def __ipow__(self, other):
        self.amount **= other
        return self

    def __lt__(self, other):
        if isinstance(other, Amount):
            assert other.asset == self.asset
            return self.amount < other.amount
        else:
            return self.amount < float(other or 0)

    def __le__(self, other):
        if isinstance(other, Amount):
            assert other.asset == self.asset
            return self.amount <= other.amount
        else:
            return self.amount <= float(other or 0)

    def __eq__(self, other):
        if isinstance(other, Amount):
            assert other.asset == self.asset
            return self.amount == other.amount
        else:
            return self.amount == float(other or 0)

    def __ne__(self, other):
        if isinstance(other, Amount):
            assert other.asset == self.asset
            return self.amount != other.amount
        else:
            return self.amount != float(other or 0)

    def __ge__(self, other):
        if isinstance(other, Amount):
            assert other.asset == self.asset
            return self.amount >= other.amount
        else:
            return self.amount >= float(other or 0)

    def __gt__(self, other):
        if isinstance(other, Amount):
            assert other.asset == self.asset
            return self.amount > other.amount
        else:
            return self.amount > float(other or 0)

    __repr__ = __str__
