from .account import Account
from .exceptions import CommitteeMemberDoesNotExistsException
from .blockchainobject import BlockchainObject


class Committee(BlockchainObject):
    """ Read data about a Committee Member in the chain

        :param str member: Name of the Committee Member
        :param transnet transnet_instance: Transnet() instance to use when
            accesing a RPC
        :param bool lazy: Use lazy loading

    """
    type_id = 5

    def refresh(self):
        if self.test_valid_objectid(self.identifier):
            _, i, _ = self.identifier.split(".")
            if int(i) == 2:
                account = Account(
                    self.identifier, transnet_instance=self.transnet)
                member = self.transnet.rpc.get_committee_member_by_account(
                    account["id"])
            elif int(i) == 5:
                member = self.transnet.rpc.get_object(self.identifier)
            else:
                raise CommitteeMemberDoesNotExistsException
        else:
            # maybe identifier is an account name
            account = Account(
                self.identifier, transnet_instance=self.transnet)
            member = self.transnet.rpc.get_committee_member_by_account(
                account["id"])

        if not member:
            raise CommitteeMemberDoesNotExistsException
        super(Committee, self).__init__(
            member, transnet_instance=self.transnet)
        self.account_id = account["id"]

    @property
    def account(self):
        return Account(self.account_id)
