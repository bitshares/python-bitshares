from .account import Account
from .exceptions import VestingBalanceDoesNotExistsException
from .blockchainobject import BlockchainObject


class Vesting(BlockchainObject):
    """ Read data about a Vesting Balance in the chain

        :param str id: Id of the vesting balance
        :param bitshares bitshares_instance: BitShares() instance to use when accesing a RPC

    """
    type_id = 13

    def refresh(self):
        obj = self.bitshares.rpc.get_objects([self.identifier])[0]
        if not obj:
            raise VestingBalanceDoesNotExistsException
        super(Vesting, self).__init__(obj, bitshares_instance=self.bitshares)

    @property
    def account(self):
        return Account(self["owner"], bitshares_instance=self.bitshares)

    @property
    def claimable(self):
        from .amount import Amount
        if self["policy"][0] == 1:
            p = self["policy"][1]
            ratio = (
                (float(p["coin_seconds_earned"]) /
                    float(self["balance"]["amount"])) /
                float(p["vesting_seconds"])
            ) if float(p["vesting_seconds"]) > 0.0 else 1
            return Amount(
                self["balance"],
                bitshares_instance=self.bitshares
            ) * ratio
        else:
            raise NotImplementedError("This policy isn't implemented yet")

    def claim(self, amount=None):
        return self.bitshares.vesting_balance_withdraw(
            self["id"],
            amount=amount,
            account=self["owner"]
        )
