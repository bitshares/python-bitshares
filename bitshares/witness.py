# -*- coding: utf-8 -*-
from .account import Account
from .blockchainobject import BlockchainObject
from .instance import BlockchainInstance
from graphenecommon.witness import (
    Witness as GrapheneWitness,
    Witnesses as GrapheneWitnesses,
)


@BlockchainInstance.inject
class Witness(GrapheneWitness):
    """ Read data about a witness in the chain

        :param str account_name: Name of the witness
        :param bitshares blockchain_instance: BitShares() instance to use when
               accesing a RPC

    """

    def define_classes(self):
        self.account_class = Account
        self.type_ids = [6, 2]


@BlockchainInstance.inject
class Witnesses(GrapheneWitnesses):
    """ Obtain a list of **active** witnesses and the current schedule

        :param bool only_active: (False) Only return witnesses that are
            actively producing blocks
        :param bitshares blockchain_instance: BitShares() instance to use when
            accesing a RPC
    """

    def define_classes(self):
        self.account_class = Account
        self.witness_class = Witness
