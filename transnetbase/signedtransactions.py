from graphenebase.signedtransactions import Signed_Transaction as GrapheneSigned_Transaction
from .operations import Operation
from .chains import known_chains
import logging
log = logging.getLogger(__name__)


class Signed_Transaction(GrapheneSigned_Transaction):
    """ Create a signed transaction and offer method to create the
        signature

        :param num refNum: parameter ref_block_num (see ``getBlockParams``)
        :param num refPrefix: parameter ref_block_prefix (see ``getBlockParams``)
        :param str expiration: expiration date
        :param Array operations:  array of operations
    """
    def __init__(self, *args, **kwargs):
        super(Signed_Transaction, self).__init__(*args, **kwargs)

    def sign(self, wifkeys, chain="BTS"):
        return super(Signed_Transaction, self).sign(wifkeys, chain)

    def verify(self, pubkeys=[], chain="BTS"):
        return super(Signed_Transaction, self).verify(pubkeys, chain)

    def getOperationKlass(self):
        return Operation

    def getKnownChains(self):
        return known_chains
