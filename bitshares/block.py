from .exceptions import BlockDoesNotExistsException
from .utils import parse_time
from .blockchainobject import BlockchainObject


class Block(BlockchainObject):
    """ Read a single block from the chain

        :param int block: block number
        :param bitshares.bitshares.BitShares bitshares_instance: BitShares
            instance
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
    def refresh(self):
        """ Even though blocks never change, you freshly obtain its contents
            from an API with this method
        """
        block = self.bitshares.rpc.get_block(self.identifier)
        if not block:
            raise BlockDoesNotExistsException
        super(Block, self).__init__(block, bitshares_instance=self.bitshares)

    def time(self):
        """ Return a datatime instance for the timestamp of this block
        """
        return parse_time(self['timestamp'])


class BlockHeader(BlockchainObject):
    def refresh(self):
        """ Even though blocks never change, you freshly obtain its contents
            from an API with this method
        """
        block = self.bitshares.rpc.get_block_header(self.identifier)
        if not block:
            raise BlockDoesNotExistsException
        super(BlockHeader, self).__init__(
            block,
            bitshares_instance=self.bitshares
        )

    def time(self):
        """ Return a datatime instance for the timestamp of this block
        """
        return parse_time(self['timestamp'])
