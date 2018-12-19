# -*- coding: utf-8 -*-
from .block import Block
from .instance import BlockchainInstance
from bitsharesbase import operationids
from graphenecommon.blockchain import Blockchain as GrapheneBlockchain


@BlockchainInstance.inject
class Blockchain(GrapheneBlockchain):
    """ This class allows to access the blockchain and read data
        from it

        :param bitshares.bitshares.BitShares blockchain_instance: BitShares
                 instance
        :param str mode: (default) Irreversible block (``irreversible``) or
                 actual head block (``head``)
        :param int max_block_wait_repetition: (default) 3 maximum wait time for
            next block ismax_block_wait_repetition * block_interval

        This class let's you deal with blockchain related data and methods.
    """

    def define_classes(self):
        self.block_class = Block
        self.operationids = operationids
