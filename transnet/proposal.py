from .instance import shared_transnet_instance
from .account import Account
from .exceptions import ProposalDoesNotExistException
from .blockchainobject import BlockchainObject
import logging
log = logging.getLogger(__name__)


class Proposal(BlockchainObject):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param transnet transnet_instance: Transnet() instance to use when accesing a RPC

    """
    type_id = 10

    def refresh(self):
        proposal = self.transnet.rpc.get_objects([self.identifier])
        if not any(proposal):
            raise ProposalDoesNotExistException
        super(Proposal, self).__init__(proposal[0], transnet_instance=self.transnet)

    @property
    def proposed_operations(self):
        yield from self["proposed_transaction"]["operations"]


class Proposals(list):
    """ Obtain a list of pending proposals for an account

        :param str account: Account name
        :param transnet transnet_instance: Transnet() instance to use when accesing a RPC
    """
    def __init__(self, account, transnet_instance=None):
        self.transnet = transnet_instance or shared_transnet_instance()

        account = Account(account, transnet_instance=self.transnet)
        proposals = self.transnet.rpc.get_proposed_transactions(account["id"])

        super(Proposals, self).__init__(
            [
                Proposal(x, transnet_instance=self.transnet)
                for x in proposals
            ]
        )
