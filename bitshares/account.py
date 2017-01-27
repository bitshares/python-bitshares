from . import bitshares as bts
from .amount import Amount
from .exceptions import AccountDoesNotExistsException


class Account(dict):
    def __init__(
        self,
        account,
        full=False,
        lazy=False,
        bitshares_instance=None
    ):
        self.cached = False
        self.name = account.strip().lower()
        self.full = full

        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance

        if isinstance(account, Account):
            super(Account, self).__init__(account)
            self.name = account["name"]
            self.cached = True

        if not lazy and not self.cached:
            self.refresh()

    def refresh(self):
        account = self.bitshares.rpc.get_account(self.name)
        if not account:
            raise AccountDoesNotExistsException
        if self.full:
            account = self.bitshares.rpc.get_full_accounts([account["id"]], False)[0][1]
            super(Account, self).__init__(account["account"])
            for k, v in account.items():
                if k != "account":
                    self[k] = v
        else:
            super(Account, self).__init__(account)
        self.cached = True

    def __getitem__(self, key):
        if not self.cached:
            self.refresh()
        return super(Account, self).__getitem__(key)

    def items(self):
        if not self.cached:
            self.refresh()
        return super(Account, self).items()

    def virtual_op_count(self):
        try:
            last_item = self.bitshares.rpc.get_account_history(self.name, -1, 0)[0][0]
        except IndexError:
            return 0
        else:
            return last_item

    @property
    def balances(self):
        balances = self.bitshares.rpc.get_account_balances(self["id"], [])
        return [Amount(b) for b in balances if int(b["amount"]) > 0]

    def balance(self, symbol):
        balances = self.balances
        for b in balances:
            if b["symbol"] == symbol:
                return b

    @property
    def call_positions(self):
        from .dex import Dex
        dex = Dex(bitshares_instance=self.bitshares)
        return dex.list_debt_positions(self["name"])

    @property
    def openorders(self):
        """ Returns open Orders
        """
        from .price import Order
        if not self.full:
            self.full = True
            self.refresh()
        return [Order(o) for o in self["limit_orders"]]

    def history(self, filter_by=None, start=0):
        """ Take all elements from start to last from history, oldest first.
        """
        batch_size = 1000
        max_index = self.virtual_op_count()
        if not max_index:
            return

        start_index = start + batch_size
        i = start_index
        while True:
            if i == start_index:
                limit = batch_size
            else:
                limit = batch_size - 1
            history = self.bitshares.rpc.get_account_history(self.name, i, limit)
            for item in history:
                index = item[0]
                if index >= max_index:
                    return

                op_type = item[1]['op'][0]
                op = item[1]['op'][1]
                timestamp = item[1]['timestamp']
                trx_id = item[1]['trx_id']

                def construct_op(account_name):
                    r = {
                        "index": index,
                        "account": account_name,
                        "trx_id": trx_id,
                        "timestamp": timestamp,
                        "type": op_type,
                    }
                    r.update(op)
                    return r

                if filter_by is None:
                    yield construct_op(self.name)
                else:
                    if type(filter_by) is list:
                        if op_type in filter_by:
                            yield construct_op(self.name)

                    if type(filter_by) is str:
                        if op_type == filter_by:
                            yield construct_op(self.name)
            i += batch_size

    def rawhistory(
        self, first=None,
        last=1, limit=100,
        only_ops=[], exclude_ops=[]
    ):
        """ Returns a generator for individual account transactions. The
            latest operation will be first. This call can be used in a
            ``for`` loop.

            :param int first: sequence number of the first transaction to return (*optional*)
            :param int limit: limit number of transactions to return (*optional*)
            :param array only_ops: Limit generator by these operations (*optional*)
            :param array exclude_ops: Exclude thse operations from generator (*optional*)
        """
        _limit=100
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
            first = int(mostrecent[0].get("id").split(".")[2]) + 1

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
                if exclude_ops and i[1]["op"][0] in exclude_ops:
                    continue
                if not only_ops or i[1]["op"][0] in only_ops:
                    cnt += 1
                    yield i
                    if limit >= 0 and cnt >= limit:
                        raise StopIteration

            if not txs:
                break
            if len(txs) < _limit:
                break
            first = int(txs[-1]["id"].split(".")[2])
