from .instance import shared_bitshares_instance
from .account import Account
import logging
log = logging.getLogger(__name__)


class Proposal(dict):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param bitshares bitshares_instance: BitShares() instance to use when accesing a RPC

    """
    def __init__(
        self,
        id,
        bitshares_instance=None,
    ):
        self.id = id

        self.bitshares = bitshares_instance or shared_bitshares_instance()
        self.refresh()

    def refresh(self):
        a, b, c = self.id.split(".")
        assert int(a) == 1 and int(b) == 10, "Valid proposal ids are 1.10.x"
        obj = self.bitshares.rpc.get_objects([self.id])[0]
        super(Proposal, self).__init__(obj)
