import unittest
from pprint import pprint
from bitshares import BitShares
from bitshares.blockchain import Blockchain
from bitshares.block import Block
from bitshares.instance import set_shared_bitshares_instance
from bitshares.utils import parse_time


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = BitShares(
            "wss://node.testnet.bitshares.eu",
            nobroadcast=True,
        )
        self.bts.set_default_account("init0")
        set_shared_bitshares_instance(self.bts)
        self.chain = Blockchain(mode="head")

    def test_is_irv(self):
        self.assertFalse(self.chain.is_irreversible_mode())

    def test_info(self):
        info = self.chain.info()
        for i in [
            "time",
            "dynamic_flags",
            "head_block_id",
            "head_block_number",
            "last_budget_time"
        ]:
            self.assertIn(i, info)

    def test_parameters(self):
        info = self.chain.chainParameters()
        for i in [
            "worker_budget_per_day",
            "maintenance_interval",
        ]:
            self.assertIn(i, info)

    def test_network(self):
        info = self.chain.get_network()
        for i in [
            "chain_id",
            "core_symbol",
            "prefix",
        ]:
            self.assertIn(i, info)

    def test_props(self):
        info = self.chain.get_chain_properties()
        for i in [
            "id",
            "chain_id",
            "immutable_parameters",
        ]:
            self.assertIn(i, info)

    def test_block_num(self):
        num = self.chain.get_current_block_num()
        self.assertTrue(num > 100)

    def test_block(self):
        block = self.chain.get_current_block()
        self.assertIsInstance(block, Block)
        self.chain.block_time(1)
        self.chain.block_timestamp(1)

    def test_list_accounts(self):
        for account in self.chain.get_all_accounts():
            self.assertIsInstance(account, str)
            # Break already
            break
