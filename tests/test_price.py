from bitshares.amount import Amount
from bitshares.price import Price
from bitshares.asset import Asset
import unittest


class Testcases(unittest.TestCase):

    def test_init(self):
        # self.assertEqual(1, 1)

        Price("0.315 USD/BTS")
        Price(0.315, base="USD", quote="BTS")
        Price(0.315, base=Asset("USD"), quote=Asset("BTS"))
        Price({
            "base": {"amount": 1, "asset_id": "1.3.0"},
            "quote": {"amount": 10, "asset_id": "1.3.106"}})
        Price({
                "receives": {"amount": 1, "asset_id": "1.3.0"},
                "pays": {"amount": 10, "asset_id": "1.3.106"},
            }, base_asset=Asset("1.3.0"))
        Price(quote="10 GOLD", base="1 USD")
        Price("10 GOLD", "1 USD")
        Price(Amount("10 GOLD"), Amount("1 USD"))
