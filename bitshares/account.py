from . import bitshares as bts
from .exceptions import AccountDoesNotExistsException


class Account(dict):
    def __init__(self, account, bitshares_instance=None):
        self.name = account
        if not isinstance(account, Account):
            if not bitshares_instance:
                bitshares_instance = bts.BitShares()
            self.bitshares = bitshares_instance

            account = self.bitshares.rpc.get_account(self.name)
            if not account:
                raise AccountDoesNotExistsException
        super(Account, self).__init__(account)
