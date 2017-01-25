import time
from .block import Block
from . import bitshares as bts
from .utils import parse_time


class Blockchain(object):
    def __init__(
        self,
        bitshares_instance=None,
        mode="irreversible"
    ):
        """ This class allows to access the blockchain and read data
            from it

            :param BitShares bitshares_instance: BitShares() instance to use when accesing a RPC
            :param str mode: (default) Irreversible block
                    (``irreversible``) or actual head block (``head``)
        """
        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance
        if mode == "irreversible":
            self.mode = 'last_irreversible_block_num'
        elif mode == "head":
            self.mode = "head_block_number"
        else:
            raise ValueError("invalid value for 'mode'!")

    def info(self):
        """ This call returns the *dynamic global properties*
        """
        return self.bitshares.rpc.get_dynamic_global_properties()

    def chainParameters(self):
        return self.config()["parameters"]

    def get_network(self):
        return self.bitshares.rpc.get_network()

    def get_chain_properties(self):
        return self.bitshares.rpc.get_chain_properties()

    def config(self):
        """ Returns object 2.0.0
        """
        return self.bitshares.rpc.get_object("2.0.0")

    def get_current_block_num(self):
        """ This call returns the current block
        """
        return self.info().get(self.mode)

    def get_current_block(self):
        """ This call returns the current block
        """
        return Block(self.get_current_block_num())

    def block_time(self, block_num):
        """ Returns a datetime of the block with the given block
            number.

            :param int block_num: Block number
        """
        return Block(block_num).time()

    def block_timestamp(self, block_num):
        """ Returns the timestamp of the block with the given block
            number.

            :param int block_num: Block number
        """
        return int(Block(block_num).time().timestamp())

    def blocks(self, start=None, stop=None):
        """ Yields blocks starting from ``start``.

            :param int start: Starting block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!
        """
        # Let's find out how often blocks are generated!
        block_interval = self.chainParameters().get("block_interval")

        if not start:
            start = self.get_current_block_num()

        # We are going to loop indefinitely
        while True:

            # Get chain properies to identify the
            head_block = self.get_current_block_num()

            # Blocks from start until head block
            for blocknum in range(start, head_block + 1):
                # Get full block
                block = self.bitshares.rpc.get_block(blocknum)
                yield {
                    **block,
                    "block_num": blocknum
                }

            # Set new start
            start = head_block + 1

            if stop and start > stop:
                break

            # Sleep for one block
            time.sleep(block_interval)

    def ops(self, start=None, stop=None, **kwargs):
        """ Yields all operations (including virtual operations) starting from ``start``.

            :param int start: Starting block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!
            :param bool only_virtual_ops: Only yield virtual operations

            This call returns a list with elements that look like
            this and carries only one operation each:::

                {'block': 8411453,
                 'op': ['vote',
                        {'author': 'dana-edwards',
                         'permlink': 'church-encoding-numbers-defined-as-functions',
                         'voter': 'juanmiguelsalas',
                         'weight': 6000}],
                 'timestamp': '2017-01-12T12:26:03',
                }

        """

        for block in self.blocks(start=start, stop=stop, **kwargs):
            for tx in block["transactions"]:
                for op in tx["operations"]:
                    yield {
                        "block": block["block_num"],
                        "op": op,
                        "timestamp": block["timestamp"]
                    }

    def stream(self, opNames=[], *args, **kwargs):
        """ Yield specific operations (e.g. comments) only

            :param array opNames: List of operations to filter for
            :param int start: Start at this block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!
        """
        for op in self.ops(**kwargs):
            if not opNames or op["op"][0] in opNames:
                yield op
    def block_time(self, block_num):
        """ Returns a datetime of the block with the given block
            number.

            :param int block_num: Block number
        """
        return Block(block_num).time()

    def block_timestamp(self, block_num):
        """ Returns the timestamp of the block with the given block
            number.

            :param int block_num: Block number
        """
        return int(Block(block_num).time().timestamp())
