from .instance import shared_bitshares_instance
from .account import Account
from .exceptions import ProposalDoesNotExistException
from .blockchainobject import BlockchainObject
import logging
log = logging.getLogger(__name__)


class Proposal(BlockchainObject):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param bitshares bitshares_instance: BitShares() instance to use when accesing a RPC

    """
    type_id = 10

    def refresh(self):
        proposal = self.bitshares.rpc.get_objects([self.identifier])
        if not any(proposal):
            raise ProposalDoesNotExistException
        super(Proposal, self).__init__(proposal[0], bitshares_instance=self.bitshares)

    @property
    def proposed_operations(self):
        yield from self["proposed_transaction"]["operations"]


class Proposals(list):
    """ Obtain a list of pending proposals for an account

        :param str account: Account name
        :param bitshares bitshares_instance: BitShares() instance to use when accesing a RPC
    """
    def __init__(self, account, bitshares_instance=None):
        self.bitshares = bitshares_instance or shared_bitshares_instance()

        account = Account(account, bitshares_instance=self.bitshares)
        proposals = self.bitshares.rpc.get_proposed_transactions(account["id"])

        super(Proposals, self).__init__(
            [
                Proposal(x, bitshares_instance=self.bitshares)
                for x in proposals
            ]
        )
