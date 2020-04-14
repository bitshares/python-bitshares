# -*- coding: utf-8 -*-
from .account import Account
from .instance import BlockchainInstance
from graphenecommon.aio.genesisbalance import (
    GenesisBalance as GrapheneGenesisBalance,
    GenesisBalances as GrapheneGenesisBalances,
)

from bitsharesbase.account import Address, PublicKey
from bitsharesbase import operations


@BlockchainInstance.inject
class GenesisBalance(GrapheneGenesisBalance):
    """
    Read data about a Genesis Balances from the chain.

    :param str identifier: identifier of the balance
    :param bitshares blockchain_instance: bitshares() instance to use when
        accesing a RPC
    """

    type_id = 15

    def define_classes(self):
        self.account_class = Account
        self.operations = operations
        self.address_class = Address
        self.publickey_class = PublicKey


@BlockchainInstance.inject
class GenesisBalances(GrapheneGenesisBalances):
    """List genesis balances that can be claimed from the keys in the wallet."""

    def define_classes(self):
        self.genesisbalance_class = GenesisBalance
        self.publickey_class = PublicKey
        self.address_class = Address
