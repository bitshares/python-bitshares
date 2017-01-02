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
            mode == "head_block_number"
        else:
            raise ValueError("invalid value for 'mode'!")

    def info(self):
        """ This call returns the *dynamic global properties*
        """
        return self.bitshares.rpc.get_dynamic_global_properties()

    def get_current_block_num(self):
        """ This call returns the current block

        """
        return self.info().get(self.mode)

    def get_current_block(self):
        """ This call returns the current block
        """
        return Block(self.get_current_block(self.mode))

    def blocks(self, **kwargs):
        """ Yield Blocks as a generator

            :param int start: Start at this block
            :param int stop: Stop at this block
        """
        return self.bitshares.rpc.block_stream(**kwargs)

    def operations(self, **kwargs):
        """ Yield specific operations as a generator

            :param array opNames: List of operations to filter by
            :param int start: Start at this block
            :param int stop: Stop at this block
        """
        return self.bitshares.rpc.stream(**kwargs)
