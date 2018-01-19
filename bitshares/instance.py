import bitshares as bts


class SharedInstance():
    instance = None


def shared_bitshares_instance():
    """ This method will initialize ``SharedInstance.instance`` and return it.
        The purpose of this method is to have offer single default
        bitshares instance that can be reused by multiple classes.
    """
    if not SharedInstance.instance:
        clear_cache()
        SharedInstance.instance = bts.BitShares()
    return SharedInstance.instance


def set_shared_bitshares_instance(bitshares_instance):
    """ This method allows us to override default bitshares instance for all users of
        ``SharedInstance.instance``.

        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance
    """
    clear_cache()
    SharedInstance.instance = bitshares_instance


def clear_cache():
    """ Clear Caches
    """
    from .blockchainobject import BlockchainObject
    BlockchainObject.clear_cache()
