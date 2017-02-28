from bitshares.instance import shared_bitshares_instance
from .account import Account
from .exceptions import WitnessDoesNotExistsException


class Witness(dict):
    """ Read data about a witness in the chain

        :param str account_name: Name of the witness
        :param bitshares bitshares_instance: BitShares() instance to use when accesing a RPC
        :param bool lazy: Use lazy loading

    """
    def __init__(
        self,
        witness,
        bitshares_instance=None,
        lazy=False
    ):
        self.cached = False
        self.witness = witness

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if not lazy:
            self.refresh()

    def refresh(self):
        account = Account(self.witness)
        witness = self.bitshares.rpc.get_witness_by_account(account["id"])
        if not witness:
            raise WitnessDoesNotExistsException
        super(Witness, self).__init__(witness)
        self.cached = True

    def __getitem__(self, key):
        if not self.cached:
            self.refresh()
        return super(Witness, self).__getitem__(key)

    def items(self):
        if not self.cached:
            self.refresh()
        return super(Witness, self).items()
