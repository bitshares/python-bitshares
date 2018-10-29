import unittest
from pprint import pprint

from bitsharesbase.objects import CallOrderExtension, AccountCreateExtensions

from .fixtures import fixture_data, bitshares, wif


class Testcases(unittest.TestCase):

    def setUp(self):
        fixture_data()

    def test_callOrderExstension(self):
        x = CallOrderExtension(target_collateral_ratio=200000)
        self.assertIn("target_collateral_ratio", x.json)
        self.assertEqual(x.json["target_collateral_ratio"], 200000)

    def test_callOrderExstension2(self):
        x = CallOrderExtension({"target_collateral_ratio": 200000})
        self.assertIn("target_collateral_ratio", x.json)
        self.assertEqual(x.json["target_collateral_ratio"], 200000)

    def test_AccountCreateExtension(self):
        x = AccountCreateExtensions({
            "buyback_options": {
                "asset_to_buy": "1.3.127",
                "asset_to_buy_issuer": "1.2.31",
                "markets": ["1.3.20"]},
            "null_ext": {},
            "owner_special_authority":
                [1, {"asset": "1.3.127",
                     "num_top_holders": 10}]
        })
        self.assertIn("buyback_options", x.json)
        self.assertIn("asset_to_buy", x.json["buyback_options"])
