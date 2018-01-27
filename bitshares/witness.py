from bitshares.instance import shared_bitshares_instance
from .account import Account
from .exceptions import WitnessDoesNotExistsException
from .blockchainobject import BlockchainObject


class Witness(BlockchainObject):
    """ Read data about a witness in the chain

        :param str account_name: Name of the witness
        :param bitshares bitshares_instance: BitShares() instance to use when
               accesing a RPC

    """
    type_ids = [6, 2]

    def refresh(self):
        if self.test_valid_objectid(self.identifier):
            _, i, _ = self.identifier.split(".")
            if int(i) == 6:
                witness = self.bitshares.rpc.get_object(self.identifier)
            else:
                witness = self.bitshares.rpc.get_witness_by_account(
                    self.identifier)
        else:
            account = Account(
                self.identifier, bitshares_instance=self.bitshares)
            witness = self.bitshares.rpc.get_witness_by_account(account["id"])
        if not witness:
            raise WitnessDoesNotExistsException
        super(Witness, self).__init__(witness, bitshares_instance=self.bitshares)

    @property
    def account(self):
        return Account(self["witness_account"], bitshares_instance=self.bitshares)


class Witnesses(list):
    """ Obtain a list of **active** witnesses and the current schedule

        :param bitshares bitshares_instance: BitShares() instance to use when
            accesing a RPC
    """
    def __init__(self, bitshares_instance=None):
        self.bitshares = bitshares_instance or shared_bitshares_instance()
        self.schedule = self.bitshares.rpc.get_object(
            "2.12.0").get("current_shuffled_witnesses", [])

        super(Witnesses, self).__init__(
            [
                Witness(x, lazy=True, bitshares_instance=self.bitshares)
                for x in self.schedule
            ]
        )
