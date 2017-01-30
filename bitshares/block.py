import bitshares as bts
from .exceptions import BlockDoesNotExistsException


class Block(dict):
    def __init__(self, block, bitshares_instance=None):
        self.cached = False
        self.block = block

        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance

        if isinstance(block, Block):
            super(Block, self).__init__(block)
            self.cached = True

    def refresh(self):
        block = self.bitshares.rpc.get_block(self.block)
        if not block:
            raise BlockDoesNotExistsException
        super(Block, self).__init__(block)
        self.cached = True

    def __getitem__(self, key):
        if not self.cached:
            self.refresh()
        return super(Block, self).__getitem__(key)

    def items(self):
        if not self.cached:
            self.refresh()
        return super(Block, self).items()
