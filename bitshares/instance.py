import bitshares as bts


class SharedInstance():
    instance = None
    config = {}


def shared_bitshares_instance():
    """ This method will initialize ``SharedInstance.instance`` and return it.
        The purpose of this method is to have offer single default
        bitshares instance that can be reused by multiple classes.
    """
    if not SharedInstance.instance:
        clear_cache()
        SharedInstance.instance = bts.BitShares(**SharedInstance.config)
    return SharedInstance.instance


def set_shared_bitshares_instance(bitshares_instance):
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
    SharedInstance.config = config
