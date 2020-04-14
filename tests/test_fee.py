# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from bitshares import BitShares
from bitshares.instance import set_shared_blockchain_instance

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = BitShares(
            nobroadcast=True,
            # We want to bundle many operations into a single transaction
            bundle=True,
            # Overwrite wallet to use this list of wifs only
            wif=[wif],
        )
        set_shared_blockchain_instance(self.bts)
        self.bts.set_default_account("init0")

    def test_fee_on_transfer(self):
        tx = self.bts.transfer(
            "init1", 1, "1.3.0", account="init0", fee_asset="1.3.121"
        )
        op = tx["operations"][0][1]
        self.assertEqual(op["fee"]["asset_id"], "1.3.121")
