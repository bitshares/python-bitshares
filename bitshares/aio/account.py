# -*- coding: utf-8 -*-
from .amount import Amount
from .instance import BlockchainInstance
from graphenecommon.aio.account import (
    Account as GrapheneAccount,
    AccountUpdate as GrapheneAccountUpdate,
)
from bitsharesbase import operations


@BlockchainInstance.inject
class Account(GrapheneAccount):
    """
    This class allows to easily access Account data.

    :param str account_name: Name of the account
    :param bitshares.aio.bitshares.BitShares blockchain_instance: BitShares
           instance
    :param bool full: Obtain all account data including orders, positions, etc.
    :param bool lazy: Use lazy loading
    :param bool full: Obtain all account data including orders, positions,
           etc.
    :returns: Account data
    :rtype: dictionary
    :raises bitshares.exceptions.AccountDoesNotExistsException: if account
            does not exist

    Instances of this class are dictionaries that come with additional
    methods (see below) that allow dealing with an account and it's
    corresponding functions.

    .. code-block:: python

        from bitshares.aio.account import Account
        account = await Account("init0")
        print(account)

    .. note:: This class comes with its own caching function to reduce the
              load on the API server. Instances of this class can be
              refreshed with ``await Account.refresh()``.
    """

    def define_classes(self):
        self.type_id = 2
        self.amount_class = Amount
        self.operations = operations

    @property
    async def call_positions(self):
        """Alias for :func:bitshares.account.Account.callpositions."""
        return await self.callpositions()

    @property
    async def callpositions(self):
        """List call positions (collateralized positions :doc:`mpa`)"""
        await self.ensure_full()
        from .dex import Dex

        dex = Dex(blockchain_instance=self.blockchain)
        return await dex.list_debt_positions(self)

    @property
    async def openorders(self):
        """Returns open Orders."""
        from .price import Order

        await self.ensure_full()
        return [
            await Order(o, blockchain_instance=self.blockchain)
            for o in self["limit_orders"]
        ]


@BlockchainInstance.inject
class AccountUpdate(GrapheneAccountUpdate):
    """
    This purpose of this class is to keep track of account updates as they are pushed
    through by :class:`bitshares.notify.Notify`.

    Instances of this class are dictionaries and take the following
    form:

    .. code-block: js

        {'id': '2.6.29',
         'lifetime_fees_paid': '44261516129',
         'most_recent_op': '2.9.0',
         'owner': '1.2.29',
         'pending_fees': 0,
         'pending_vested_fees': 16310,
         'total_core_in_orders': '6788845277634',
         'total_ops': 0}
    """

    def define_classes(self):
        self.account_class = Account
