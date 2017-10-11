from bitshares.instance import shared_bitshares_instance
from .exceptions import AccountDoesNotExistsException
from .blockchainobject import BlockchainObject


class Account(BlockchainObject):
    """ This class allows to easily access Account data

        :param str account_name: Name of the account
        :param bitshares.bitshares.BitShares bitshares_instance: BitShares
               instance
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

            from bitshares.account import Account
            account = Account("init0")
            print(account)

        .. note:: This class comes with its own caching function to reduce the
                  load on the API server. Instances of this class can be
                  refreshed with ``Account.refresh()``.

    """

    type_id = 2

    def __init__(
        self,
        account,
        full=False,
        lazy=False,
        bitshares_instance=None
    ):
        self.full = full
        super().__init__(
            account,
            lazy=lazy,
            full=full,
            bitshares_instance=None
        )

    def refresh(self):
        """ Refresh/Obtain an account's data from the API server
        """
        import re
        if re.match("^1\.2\.[0-9]*$", self.identifier):
            account = self.bitshares.rpc.get_objects([self.identifier])[0]
        else:
            account = self.bitshares.rpc.lookup_account_names(
                [self.identifier])[0]
        if not account:
            raise AccountDoesNotExistsException(self.identifier)
        self.identifier = account["id"]

        if self.full:
            account = self.bitshares.rpc.get_full_accounts(
                [account["id"]], False)[0][1]
            super(Account, self).__init__(account["account"])
            for k, v in account.items():
                if k != "account":
                    self[k] = v
        else:
            super(Account, self).__init__(account)

    @property
    def name(self):
        return self["name"]

    @property
    def is_ltm(self):
        """ Is the account a lifetime member (LTM)?
        """
        return self["id"] == self["lifetime_referrer"]

    @property
    def balances(self):
        """ List balances of an account. This call returns instances of
            :class:`bitshares.amount.Amount`.
        """
        from .amount import Amount
        balances = self.bitshares.rpc.get_account_balances(self["id"], [])
        return [
            Amount(b, bitshares_instance=self.bitshares)
            for b in balances if int(b["amount"]) > 0
        ]

    def balance(self, symbol):
        """ Obtain the balance of a specific Asset. This call returns instances of
            :class:`bitshares.amount.Amount`.
        """
        from .amount import Amount
        if isinstance(symbol, dict) and "symbol" in symbol:
            symbol = symbol["symbol"]
        balances = self.balances
        for b in balances:
            if b["symbol"] == symbol:
                return b
        return Amount(0, symbol)

    @property
    def call_positions(self):
        """ Alias for :func:bitshares.account.Account.callpositions
        """
        return self.callpositions()

    @property
    def callpositions(self):
        """ List call positions (collateralized positions :doc:`mpa`)
        """
        if not self.full:
            self.full = True
            self.refresh()
        from .dex import Dex
        dex = Dex(bitshares_instance=self.bitshares)
        return dex.list_debt_positions(self)

    @property
    def openorders(self):
        """ Returns open Orders
        """
        from .price import Order
        if not self.full:
            self.full = True
            self.refresh()
        return [Order(o) for o in self["limit_orders"]]

    def history(
        self, first=None,
        last=0, limit=100,
        only_ops=[], exclude_ops=[]
    ):
        """ Returns a generator for individual account transactions. The
            latest operation will be first. This call can be used in a
            ``for`` loop.

            :param int first: sequence number of the first
                transaction to return (*optional*)
            :param int limit: limit number of transactions to
                return (*optional*)
            :param array only_ops: Limit generator by these
                operations (*optional*)
            :param array exclude_ops: Exclude thse operations from
                generator (*optional*)
        """
        from bitsharesbase.operations import getOperationNameForId
        _limit = 100
        cnt = 0

        mostrecent = self.bitshares.rpc.get_account_history(
            self["id"],
            "1.11.{}".format(0),
            1,
            "1.11.{}".format(9999999999999),
            api="history"
        )
        if not mostrecent:
            raise StopIteration

        if not first:
            # first = int(mostrecent[0].get("id").split(".")[2]) + 1
            first = 9999999999

        while True:
            # RPC call
            txs = self.bitshares.rpc.get_account_history(
                self["id"],
                "1.11.{}".format(last),
                _limit,
                "1.11.{}".format(first - 1),
                api="history"
            )
            for i in txs:
                if exclude_ops and getOperationNameForId(
                    i["op"][0]
                ) in exclude_ops:
                    continue
                if not only_ops or getOperationNameForId(
                    i["op"][0]
                ) in only_ops:
                    cnt += 1
                    yield i
                    if limit >= 0 and cnt >= limit:
                        raise StopIteration

            if not txs:
                break
            if len(txs) < _limit:
                break
            first = int(txs[-1]["id"].split(".")[2])

    def upgrade(self):
        return self.bitshares.upgrade_account(account=self)


class AccountUpdate(dict):
    """ This purpose of this class is to keep track of account updates
        as they are pushed through by :class:`bitshares.notify.Notify`.

        Instances of this class are dictionaries and take the following
        form:

        ... code-block: js

            {'id': '2.6.29',
             'lifetime_fees_paid': '44261516129',
             'most_recent_op': '2.9.0',
             'owner': '1.2.29',
             'pending_fees': 0,
             'pending_vested_fees': 16310,
             'total_core_in_orders': '6788845277634',
             'total_ops': 0}

    """

    def __init__(
        self,
        data,
        bitshares_instance=None
    ):
        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if isinstance(data, dict):
            super(AccountUpdate, self).__init__(data)
        else:
            account = Account(data, bitshares_instance=self.bitshares)
            update = self.bitshares.rpc.get_objects([
                "2.6.%s" % (account["id"].split(".")[2])
            ])[0]
            super(AccountUpdate, self).__init__(update)

    @property
    def account(self):
        """ In oder to obtain the actual
            :class:`bitshares.account.Account` from this class, you can
            use the ``account`` attribute.
        """
        account = Account(self["owner"])
        account.refresh()
        return account

    def __repr__(self):
        return "<AccountUpdate: {}>".format(self["owner"])
