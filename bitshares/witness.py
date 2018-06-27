from .instance import BlockchainInstance
from .account import Account
from .exceptions import WitnessDoesNotExistsException
from .blockchainobject import BlockchainObject


class Witness(BlockchainObject):
    """ Read data about a witness in the chain

        :param str account_name: Name of the witness
        :param bitshares blockchain_instance: BitShares() instance to use when
               accesing a RPC

    """
    type_ids = [6, 2]

    def refresh(self):
        if self.test_valid_objectid(self.identifier):
            _, i, _ = self.identifier.split(".")
            if int(i) == 6:
                witness = self.blockchain.rpc.get_object(self.identifier)
            else:
                witness = self.blockchain.rpc.get_witness_by_account(
                    self.identifier)
        else:
            account = Account(
                self.identifier, blockchain_instance=self.blockchain)
            witness = self.blockchain.rpc.get_witness_by_account(account["id"])
        if not witness:
            raise WitnessDoesNotExistsException(self.identifier)
        super(Witness, self).__init__(
            witness, blockchain_instance=self.blockchain)

    @property
    def account(self):
        return Account(
            self["witness_account"], blockchain_instance=self.blockchain)

    @property
    def weight(self):
        if not self.is_active:
            return 0
        else:
            account = Account(
                "witness-account",
                blockchain_instance=self.blockchain)
            threshold = account["active"]["weight_threshold"]
            weight = next(
                filter(
                    lambda x: x[0] == self.account["id"],
                    account["active"]["account_auths"]))
            return float(weight[1]) / float(threshold)

    @property
    def is_active(self):
        account = Account(
            "witness-account",
            blockchain_instance=self.blockchain)
        return self.account["id"] in [
            x[0] for x in account["active"]["account_auths"]
        ]


class Witnesses(list):
    """ Obtain a list of **active** witnesses and the current schedule

        :param bool only_active: (False) Only return witnesses that are
            actively producing blocks
        :param bitshares blockchain_instance: BitShares() instance to use when
            accesing a RPC
    """
    def __init__(self, only_active=False, lazy=False, **kwargs):
        BlockchainInstance.__init__(self, **kwargs)
        self.schedule = self.blockchain.rpc.get_object(
            "2.12.0").get("current_shuffled_witnesses", [])

        witnesses = [
            Witness(x, lazy=lazy, blockchain_instance=self.blockchain)
            for x in self.schedule
        ]

        if only_active:
            account = Account(
                "witness-account",
                blockchain_instance=self.blockchain)
            filter_by = [x[0] for x in account["active"]["account_auths"]]
            witnesses = list(
                filter(
                    lambda x: x["witness_account"] in filter_by,
                    witnesses))

        super(Witnesses, self).__init__(witnesses)

    def __contains__(self, item):
        from .account import Account
        if BlockchainObject.objectid_valid(item):
            id = item
        elif isinstance(item, Account):
            id = item["id"]
        else:
            account = Account(item, blockchain_instance=self.blockchain)
            id = account["id"]

        return (
            any([id == x["id"] for x in self]) or
            any([id == x["witness_account"] for x in self])
        )
