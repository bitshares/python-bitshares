from . import bitshares as bts
from .amount import Amount
from .exceptions import AccountDoesNotExistsException


class Account(dict):
    def __init__(self, account, bitshares_instance=None):
        self.cached = False
        self.name = account

        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance

        if isinstance(account, Account):
            super(Account, self).__init__(account)
            self.cached = True

    def refresh(self):
        account = self.bitshares.rpc.get_account(self.name)
        if not account:
            raise AccountDoesNotExistsException
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

    @property
    def balances(self):
        balances = self.bitshares.rpc.get_account_balances(self["id"], [])
        return [Amount(b) for b in balances if int(b["amount"]) > 0]
