# -*- coding: utf-8 -*-
import bitshares as bts

from graphenecommon.instance import (
    BlockchainInstance as GrapheneBlockchainInstance,
    SharedInstance,
)


class BlockchainInstance(GrapheneBlockchainInstance):
    """ This is a class that allows compatibility with previous
        naming conventions
    """

    def __init__(self, *args, **kwargs):
        # Also allow 'bitshares_instance'
        if kwargs.get("bitshares_instance"):
            kwargs["blockchain_instance"] = kwargs["bitshares_instance"]
        GrapheneBlockchainInstance.__init__(self, *args, **kwargs)

    def get_instance_class(self):
        """ Should return the Chain instance class, e.g. `bitshares.BitShares`
        """
        return bts.BitShares

    @property
    def bitshares(self):
        """ Alias for the specific blockchain
        """
        return self.blockchain


def shared_blockchain_instance():
    return BlockchainInstance().shared_blockchain_instance()


def set_shared_blockchain_instance(instance):
    shared_blockchain_instance().clear_cache()  # clear cache
    BlockchainInstance().set_shared_blockchain_instance(instance)


def set_shared_config(config):
    shared_blockchain_instance().set_shared_config(config)


shared_bitshares_instance = shared_blockchain_instance
set_shared_bitshares_instance = set_shared_blockchain_instance
