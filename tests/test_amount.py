import unittest
from bitshares import BitShares
from bitshares.amount import Amount
from bitshares.asset import Asset
from bitshares.instance import set_shared_bitshares_instance, SharedInstance


url = "wss://node.testnet.bitshares.eu"


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = BitShares(url, nobroadcast=True)
        set_shared_bitshares_instance(self.bts)
        self.asset = Asset("1.3.0")
        self.symbol = self.asset["symbol"]
        self.precision = self.asset["precision"]
        self.asset2 = Asset("1.3.1")

    def dotest(self, ret, amount, symbol):
        self.assertEqual(float(ret), float(amount))
        self.assertEqual(ret["symbol"], symbol)
        self.assertIsInstance(ret["asset"], dict)
        self.assertIsInstance(ret["amount"], float)

    def test_url(self):
        self.assertEqual(self.bts.rpc.url, url)

    def test_init(self):
        # String init
        amount = Amount("1 {}".format(self.symbol))
        self.dotest(amount, 1, self.symbol)

        # Amount init
        amount = Amount(amount)
        self.dotest(amount, 1, self.symbol)

        # blockchain dict init
        amount = Amount({
            "amount": 1 * 10 ** self.precision,
            "asset_id": self.asset["id"]
        })
        self.dotest(amount, 1, self.symbol)

        # API dict init
        amount = Amount({
            "amount": 1.3 * 10 ** self.precision,
            "asset": self.asset["id"]
        })
        self.dotest(amount, 1.3, self.symbol)

        # Asset as symbol
        amount = Amount(1.3, Asset("1.3.0"))
        self.dotest(amount, 1.3, self.symbol)

        # Asset as symbol
        amount = Amount(1.3, self.symbol)
        self.dotest(amount, 1.3, self.symbol)

        # keyword inits
        amount = Amount(amount=1.3, asset=Asset("1.3.0"))
        self.dotest(amount, 1.3, self.symbol)

        # keyword inits
        amount = Amount(amount=1.3, asset=dict(Asset("1.3.0")))
        self.dotest(amount, 1.3, self.symbol)

        # keyword inits
        amount = Amount(amount=1.3, asset=self.symbol)
        self.dotest(amount, 1.3, self.symbol)

    def test_copy(self):
        amount = Amount("1", self.symbol)
        self.dotest(amount.copy(), 1, self.symbol)

    def test_properties(self):
        amount = Amount("1", self.symbol)
        self.assertEqual(amount.amount, 1.0)
        self.assertEqual(amount.symbol, self.symbol)
        self.assertIsInstance(amount.asset, Asset)
        self.assertEqual(amount.asset["symbol"], self.symbol)

    def test_tuple(self):
        amount = Amount("1", self.symbol)
        self.assertEqual(
            amount.tuple(),
            (1.0, self.symbol))

    def test_json(self):
        amount = Amount("1", self.symbol)
        self.assertEqual(
            amount.json(),
            {
                "asset_id": self.asset["id"],
                "amount": 1 * 10 ** self.precision
            })

    def test_string(self):
        self.assertEqual(
            str(Amount("1", self.symbol)),
            "1.00000 {}".format(self.symbol))

    def test_int(self):
        self.assertEqual(
            int(Amount("1", self.symbol)),
            100000)

    def test_float(self):
        self.assertEqual(
            float(Amount("1", self.symbol)),
            1.00000)

    def test_plus(self):
        a1 = Amount(1, self.symbol)
        a2 = Amount(2, self.symbol)
        self.dotest(a1 + a2, 3, self.symbol)
        with self.assertRaises(Exception):
            a1 + Amount(1, asset=self.asset2)
        # inline
        a2 = Amount(2, self.symbol)
        a2 += a1
        self.dotest(a2, 3, self.symbol)
        a2 += 5
        self.dotest(a2, 8, self.symbol)
        with self.assertRaises(Exception):
            a1 += Amount(1, asset=self.asset2)

    def test_minus(self):
        a1 = Amount(1, self.symbol)
        a2 = Amount(2, self.symbol)
        self.dotest(a1 - a2, -1, self.symbol)
        self.dotest(a1 - 5, -4, self.symbol)
        with self.assertRaises(Exception):
            a1 - Amount(1, asset=self.asset2)
        # inline
        a2 = Amount(2, self.symbol)
        a2 -= a1
        self.dotest(a2, 1, self.symbol)
        a2 -= 1
        self.dotest(a2, 0, self.symbol)
        self.dotest(a2 - 2, -2, self.symbol)
        with self.assertRaises(Exception):
            a1 -= Amount(1, asset=self.asset2)

    def test_mul(self):
        a1 = Amount(5, self.symbol)
        a2 = Amount(2, self.symbol)
        self.dotest(a1 * a2, 10, self.symbol)
        self.dotest(a1 * 3, 15, self.symbol)
        with self.assertRaises(Exception):
            a1 * Amount(1, asset=self.asset2)
        # inline
        a2 = Amount(2, self.symbol)
        a2 *= 5
        self.dotest(a2, 10, self.symbol)
        with self.assertRaises(Exception):
            a1 *= Amount(2, asset=self.asset2)

    def test_div(self):
        a1 = Amount(15, self.symbol)
        self.dotest(a1 / 3, 5, self.symbol)
        self.dotest(a1 // 2, 7, self.symbol)
        with self.assertRaises(Exception):
            a1 / Amount(1, asset=self.asset2)
        # inline
        a2 = a1.copy()
        a2 /= 3
        self.dotest(a2, 5, self.symbol)
        a2 = a1.copy()
        a2 //= 2
        self.dotest(a2, 7, self.symbol)
        with self.assertRaises(Exception):
            a1 *= Amount(2, asset=self.asset2)

    def test_mod(self):
        a1 = Amount(15, self.symbol)
        self.dotest(a1 % 3, 0, self.symbol)
        self.dotest(a1 % 2, 1, self.symbol)
        with self.assertRaises(Exception):
            a1 % Amount(1, asset=self.asset2)
        # inline
        a2 = a1.copy()
        a2 %= 3
        self.dotest(a2, 0, self.symbol)
        with self.assertRaises(Exception):
            a1 %= Amount(2, asset=self.asset2)

    def test_pow(self):
        a1 = Amount(15, self.symbol)
        self.dotest(a1 ** 3, 15 ** 3, self.symbol)
        self.dotest(a1 ** 2, 15 ** 2, self.symbol)
        with self.assertRaises(Exception):
            a1 ** Amount(1, asset=self.asset2)
        # inline
        a2 = a1.copy()
        a2 **= 3
        self.dotest(a2, 15 ** 3, self.symbol)
        with self.assertRaises(Exception):
            a1 **= Amount(2, asset=self.asset2)

    def test_ltge(self):
        a1 = Amount(1, self.symbol)
        a2 = Amount(2, self.symbol)
        self.assertTrue(a1 < a2)
        self.assertTrue(a2 > a1)
        self.assertTrue(a2 > 1)
        self.assertTrue(a1 < 5)

    def test_leeq(self):
        a1 = Amount(1, self.symbol)
        a2 = Amount(1, self.symbol)
        self.assertTrue(a1 <= a2)
        self.assertTrue(a1 >= a2)
        self.assertTrue(a1 <= 1)
        self.assertTrue(a1 >= 1)

    def test_ne(self):
        a1 = Amount(1, self.symbol)
        a2 = Amount(2, self.symbol)
        self.assertTrue(a1 != a2)
        self.assertTrue(a1 != 5)
        a1 = Amount(1, self.symbol)
        a2 = Amount(1, self.symbol)
        self.assertTrue(a1 == a2)
        self.assertTrue(a1 == 1)
