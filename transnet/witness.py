from transnet.instance import shared_transnet_instance
from .account import Account
from .exceptions import WitnessDoesNotExistsException
from .blockchainobject import BlockchainObject


class Witness(BlockchainObject):
    """ Read data about a witness in the chain

        :param str account_name: Name of the witness
        :param transnet transnet_instance: Transnet() instance to use when
               accesing a RPC

    """
    type_ids = [6, 2]

    def refresh(self):
        if self.test_valid_objectid(self.identifier):
            _, i, _ = self.identifier.split(".")
            if int(i) == 6:
                witness = self.transnet.rpc.get_object(self.identifier)
            else:
                witness = self.transnet.rpc.get_witness_by_account(
                    self.identifier)
        else:
            account = Account(
                self.identifier, transnet_instance=self.transnet)
            witness = self.transnet.rpc.get_witness_by_account(account["id"])
        if not witness:
            raise WitnessDoesNotExistsException
        super(Witness, self).__init__(witness, transnet_instance=self.transnet)

    @property
    def account(self):
        return Account(self["witness_account"], transnet_instance=self.transnet)


class Witnesses(list):
    """ Obtain a list of **active** witnesses and the current schedule

        :param transnet transnet_instance: Transnet() instance to use when
            accesing a RPC
    """
    def __init__(self, transnet_instance=None):
        self.transnet = transnet_instance or shared_transnet_instance()
        self.schedule = self.transnet.rpc.get_object(
            "2.12.0").get("current_shuffled_witnesses", [])

        super(Witnesses, self).__init__(
            [
                Witness(x, lazy=True, transnet_instance=self.transnet)
                for x in self.schedule
            ]
        )
