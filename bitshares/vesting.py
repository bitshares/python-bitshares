from .instance import shared_bitshares_instance
from .account import Account
from .exceptions import VestingBalanceDoesNotExistsException


class Vesting(dict):
    """ Read data about a Vesting Balance in the chain

        :param str id: Id of the vesting balance
        :param bitshares bitshares_instance: BitShares() instance to use when accesing a RPC

    """
    def __init__(
        self,
        id,
        bitshares_instance=None,
    ):
        self.id = id

        self.bitshares = bitshares_instance or shared_bitshares_instance()
        self.refresh()

    def refresh(self):
        a, b, c = self.id.split(".")
        assert int(a) == 1 and int(b) == 13, "Valid vesting balances are 1.13.x"
        obj = self.bitshares.rpc.get_objects([self.id])[0]
        super(Vesting, self).__init__(obj)

    @property
    def account(self):
        return Account(self["owner"])
