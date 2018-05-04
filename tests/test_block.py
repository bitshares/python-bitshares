import unittest
from pprint import pprint
from bitshares import BitShares
from bitshares.block import Block, BlockHeader
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

    def test_block(self):
        block = Block(1)
        self.assertEqual(block["previous"], "0000000000000000000000000000000000000000")
        self.assertEqual(block.time(), parse_time('2016-01-18T10:59:20'))

    def test_blockheader(self):
        header = BlockHeader(1)
        self.assertEqual(header["previous"], "0000000000000000000000000000000000000000")
        self.assertEqual(header.time(), parse_time('2016-01-18T10:59:20'))
