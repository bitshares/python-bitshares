from .instance import BlockchainInstance
from .account import Account
from .exceptions import ProposalDoesNotExistException
from .blockchainobject import BlockchainObject
from .utils import parse_time
import logging
log = logging.getLogger(__name__)


class Proposal(BlockchainObject):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param bitshares blockchain_instance: BitShares() instance to use when accesing a RPC

    """
    type_id = 10

    def refresh(self):
        proposal = self.blockchain.rpc.get_objects([self.identifier])
        if not any(proposal):
            raise ProposalDoesNotExistException
        super(Proposal, self).__init__(proposal[0], blockchain_instance=self.blockchain)

    @property
    def proposed_operations(self):
        yield from self["proposed_transaction"]["operations"]

    @property
    def expiration(self):
        return parse_time(self.get("expiration_time"))

    @property
    def review_period(self):
        return parse_time(self.get("review_period_time"))

    @property
    def is_in_review(self):
        from datetime import datetime, timezone
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        return now > self.review_period


class Proposals(list):
    """ Obtain a list of pending proposals for an account

        :param str account: Account name
        :param bitshares blockchain_instance: BitShares() instance to use when accesing a RPC
    """
    def __init__(self, account, **kwargs):
        BlockchainInstance.__init__(self, **kwargs)

        account = Account(account, blockchain_instance=self.blockchain)
        proposals = self.blockchain.rpc.get_proposed_transactions(account["id"])

        super(Proposals, self).__init__(
            [
                Proposal(x, blockchain_instance=self.blockchain)
                for x in proposals
            ]
        )
