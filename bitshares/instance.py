import bitshares as bts


class BlockchainInstance():
    """ This is a class that allows compatibility with previous
        naming conventions
    """
    def __init__(self, *args, **kwargs):
        if "bitshares_instance" in kwargs and kwargs["bitshares_instance"]:
            self.blockchain = kwargs["bitshares_instance"]
        elif "blockchain_instance" in kwargs and kwargs["blockchain_instance"]:
            self.blockchain = kwargs["blockchain_instance"]
        else:
            self.blockchain = shared_blockchain_instance()

    @property
    def bitshares(self):
        """ Alias for the specific blockchain
        """
        return self.blockchain

    @property
    def chain(self):
        """ Short form for blockchain (for the lazy)
        """
        return self.blockchain


class SharedInstance():
    """ This class merely offers a singelton for the Blockchain Instance
    """
    instance = None
    config = {}


def shared_blockchain_instance():
    """ This method will initialize ``SharedInstance.instance`` and return it.
        The purpose of this method is to have offer single default
        bitshares instance that can be reused by multiple classes.
    """
    if not SharedInstance.instance:
        clear_cache()
        SharedInstance.instance = bts.BitShares(**SharedInstance.config)
    return SharedInstance.instance


def set_shared_blockchain_instance(bitshares_instance):
    """ This method allows us to override default bitshares instance for all
        users of ``SharedInstance.instance``.

        :param bitshares.bitshares.BitShares bitshares_instance: BitShares
            instance
    """
    clear_cache()
    SharedInstance.instance = bitshares_instance


def clear_cache():
    """ Clear Caches
    """
    from .blockchainobject import BlockchainObject
    BlockchainObject.clear_cache()


def set_shared_config(config):
    """ This allows to set a config that will be used when calling
        ``shared_bitshares_instance`` and allows to define the configuration
        without requiring to actually create an instance
    """
    assert isinstance(config, dict)
    SharedInstance.config.update(config)
    # if one is already set, delete
    if SharedInstance.instance:
        clear_cache()
        SharedInstance.instance = None


shared_bitshares_instance = shared_blockchain_instance
set_shared_bitshares_instance = set_shared_blockchain_instance
