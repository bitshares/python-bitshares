from bitshares.instance import shared_bitshares_instance

from .exceptions import BlockDoesNotExistsException
from .utils import parse_time


class Block(dict):
    """ Read a single block from the chain

        :param int block: block number
        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance
        :param bool lazy: Use lazy loading

        Instances of this class are dictionaries that come with additional
        methods (see below) that allow dealing with a block and it's
        corresponding functions.

        .. code-block:: python

            from bitshares.block import Block
            block = Block(1)
            print(block)

        .. note:: This class comes with its own caching function to reduce the
                  load on the API server. Instances of this class can be
                  refreshed with ``Account.refresh()``.

    """
    def __init__(
        self,
        block,
        bitshares_instance=None,
        lazy=False
    ):
        self.bitshares = bitshares_instance or shared_bitshares_instance()
        self.cached = False
        self.block = block

        if isinstance(block, Block):
            super(Block, self).__init__(block)
            self.cached = True
        elif not lazy:
            self.refresh()

    def refresh(self):
        """ Even though blocks never change, you freshly obtain its contents
            from an API with this method
        """
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

    def time(self):
        """ Return a datatime instance for the timestamp of this block
        """
        return parse_time(self['timestamp'])
