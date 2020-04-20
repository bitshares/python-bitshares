# -*- coding: utf-8 -*-
from .instance import BlockchainInstance
from ..block import Block as SyncBlock, BlockHeader as SyncBlockHeader
from graphenecommon.aio.block import (
    Block as GrapheneBlock,
    BlockHeader as GrapheneBlockHeader,
)


@BlockchainInstance.inject
class Block(GrapheneBlock, SyncBlock):
    """
    Read a single block from the chain.

    :param int block: block number
    :param bitshares.aio.bitshares.BitShares blockchain_instance: BitShares
        instance
    :param bool lazy: Use lazy loading
    :param loop: async event loop

    Instances of this class are dictionaries that come with additional
    methods (see below) that allow dealing with a block and it's
    corresponding functions.

    .. code-block:: python

        from bitshares.aio.block import Block
        block = await Block(1)
        print(block)
    """

    pass


@BlockchainInstance.inject
class BlockHeader(GrapheneBlockHeader, SyncBlockHeader):
    pass
