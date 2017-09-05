from .instance import shared_bitshares_instance
from .account import Account
from .exceptions import ProposalDoesNotExistException
import logging
log = logging.getLogger(__name__)


class Proposal(dict):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param bitshares bitshares_instance: BitShares() instance to use when accesing a RPC

    """
    type_id = 10

    def refresh(self):
        proposal = self.bitshares.rpc.get_objects([self.identifier])
        if not any(proposal):
            raise ProposalDoesNotExistException
        super(Proposal, self).__init__(proposal[0])

    def __repr__(self):
        return "<proposal %s>" % str(self.id)


class Proposals(list):
    """ Obtain a list of pending proposals for an account

        :param str account: Account name
        :param bitshares bitshares_instance: BitShares() instance to use when accesing a RPC
    """
    def __init__(self, account, bitshares_instance=None):
        self.bitshares = bitshares_instance or shared_bitshares_instance()

        account = Account(account)
        proposals = self.bitshares.rpc.get_proposed_transactions(account["id"])

        super(Proposals, self).__init__(
            [
                Proposal(x, bitshares_instance=self.bitshares)
                for x in proposals
            ]
        )
