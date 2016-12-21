from . import bitshares as bts
from .exceptions import BlockDoesNotExistsException


class Block(dict):
    def __init__(self, block, bitshares_instance=None):
        self.block = block

        if not isinstance(block, Block):
            if not bitshares_instance:
                bitshares_instance = bts.BitShares()
            self.bitshares = bitshares_instance
            block = self.bitshares.rpc.get_block(block)
            if not block:
                raise BlockDoesNotExistsException
        super(Block, self).__init__(block)
