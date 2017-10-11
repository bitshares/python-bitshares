from bitshares.instance import shared_bitshares_instance
from .account import Account
from .exceptions import CommitteeMemberDoesNotExistsException
from .blockchainobject import BlockchainObject


class Committee(BlockchainObject):
    """ Read data about a Committee Member in the chain

        :param str member: Name of the Committee Member
        :param bitshares bitshares_instance: BitShares() instance to use when accesing a RPC
        :param bool lazy: Use lazy loading

    """
    type_id = 5

    def refresh(self):
        account = Account(self.identifier)
        member = self.bitshares.rpc.get_committee_member_by_account(account["id"])
        if not member:
            raise CommitteeMemberDoesNotExistsException
        super(Committee, self).__init__(member)
        self.cached = True

    @property
    def account(self):
        return Account(self.identifier)
