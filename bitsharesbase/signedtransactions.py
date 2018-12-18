# -*- coding: utf-8 -*-
from graphenebase.signedtransactions import (
    Signed_Transaction as GrapheneSigned_Transaction,
)

from .chains import known_chains
from .operations import Operation


class Signed_Transaction(GrapheneSigned_Transaction):
    """ Create a signed transaction and offer method to create the
        signature

        :param num refNum: parameter ref_block_num (see ``getBlockParams``)
        :param num refPrefix: parameter ref_block_prefix (see ``getBlockParams``)
        :param str expiration: expiration date
        :param Array operations:  array of operations
    """

    known_chains = known_chains
    default_prefix = "BTS"
    operation_klass = Operation
