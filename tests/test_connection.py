
import unittest
from bitshares import BitShares
from bitshares.asset import Asset
from bitshares.instance import set_shared_bitshares_instance, SharedInstance
from bitshares.blockchainobject import BlockchainObject

import logging
log = logging.getLogger()


class Testcases(unittest.TestCase):

    def test_bts1bts2(self):
        b1 = BitShares(
            "wss://node.testnet.bitshares.eu",
            nobroadcast=True,
        )

        b2 = BitShares(
            "wss://node.bitshares.eu",
            nobroadcast=True,
        )

        self.assertNotEqual(b1.rpc.url, b2.rpc.url)

    def test_default_connection(self):
        b1 = BitShares(
            "wss://node.testnet.bitshares.eu",
            nobroadcast=True,
        )
        set_shared_bitshares_instance(b1)
        test = Asset("1.3.0")

        b2 = BitShares(
            "wss://node.bitshares.eu",
            nobroadcast=True,
        )
        set_shared_bitshares_instance(b2)

        bts = Asset("1.3.0")

        self.assertEqual(test["symbol"], "TEST")
        self.assertEqual(bts["symbol"], "BTS")
