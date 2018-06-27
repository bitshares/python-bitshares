from .instance import BlockchainInstance
from .account import Account
from .exceptions import ProposalDoesNotExistException
from .blockchainobject import BlockchainObject, ObjectCache
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
    def proposer(self):
        """ Return the proposer of the proposal if available in the backend,
            else returns None
        """
        if "proposer" in self:
            return self["proposer"]

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
    cache = ObjectCache()

    def __init__(self, account, **kwargs):
        BlockchainInstance.__init__(self, **kwargs)

        account = Account(account)
        if account["id"] in Proposals.cache:
            proposals = Proposals.cache[account["id"]]
        else:
            proposals = self.blockchain.rpc.get_proposed_transactions(account["id"])
            Proposals.cache[account["id"]] = proposals

        super(Proposals, self).__init__(
            [
                Proposal(x, blockchain_instance=self.blockchain)
                for x in proposals
            ]
        )
