# -*- coding: utf-8 -*-
from graphenecommon.instance import AbstractBlockchainInstanceProvider, SharedInstance


class BlockchainInstance(AbstractBlockchainInstanceProvider):
    """ This is a class that allows compatibility with previous
        naming conventions
    """

    def __init__(self, *args, **kwargs):
        # Also allow 'bitshares_instance'
        if kwargs.get("bitshares_instance"):
            kwargs["blockchain_instance"] = kwargs["bitshares_instance"]
        if kwargs.get("blockchain_instance"):
            SharedInstance.instance = kwargs["blockchain_instance"]

    def get_instance_class(self):
        """ Should return the Chain instance class, e.g. `bitshares.BitShares`
        """
        import bitshares as bts

        return bts.BitShares

    @property
    def bitshares(self):
        """ Alias for the specific blockchain
        """
        return self.blockchain


def shared_blockchain_instance():
    return BlockchainInstance().shared_blockchain_instance()


def set_shared_blockchain_instance(instance):
    # clear cache
    inst = shared_blockchain_instance()
    inst.clear_cache()
    BlockchainInstance().set_shared_blockchain_instance(instance)


def set_shared_config(config):
    shared_blockchain_instance().set_shared_config(config)


shared_bitshares_instance = shared_blockchain_instance
set_shared_bitshares_instance = set_shared_blockchain_instance
