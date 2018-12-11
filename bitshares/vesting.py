# -*- coding: utf-8 -*-
from .amount import Amount
from .account import Account
from .instance import BlockchainInstance
from graphenecommon.vesting import Vesting as GrapheneVesting


@BlockchainInstance.inject
class Vesting(GrapheneVesting):
    """ Read data about a Vesting Balance in the chain

        :param str id: Id of the vesting balance
        :param bitshares blockchain_instance: BitShares() instance to use when
            accesing a RPC

    """

    type_id = 13
    account_class = Account
    amount_class = Amount
