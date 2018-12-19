# -*- coding: utf-8 -*-
from .instance import BlockchainInstance
from graphenecommon.block import (
    Block as GrapheneBlock,
    BlockHeader as GrapheneBlockHeader,
)


@BlockchainInstance.inject
class Block(GrapheneBlock):
    """ Read a single block from the chain

        :param int block: block number
        :param bitshares.bitshares.BitShares blockchain_instance: BitShares
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

    def define_classes(self):
        self.type_id = "-none-"


@BlockchainInstance.inject
class BlockHeader(GrapheneBlockHeader):
    def define_classes(self):
        self.type_id = "-none-"
