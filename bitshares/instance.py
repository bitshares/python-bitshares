import bitshares as bts

_shared_bitshares_instance = None


def shared_bitshares_instance():
    """ This method will initialize ``_shared_bitshares_instance`` and return it.
        The purpose of this method is to have offer single default
        bitshares instance that can be reused by multiple classes.
    """
    global _shared_bitshares_instance
    if not _shared_bitshares_instance:
        _shared_bitshares_instance = bts.BitShares()
    return _shared_bitshares_instance


def set_shared_bitshares_instance(bitshares_instance):
    """ This method allows us to override default bitshares instance for all users of
        ``_shared_bitshares_instance``.

        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance
    """
    global _shared_bitshares_instance
    _shared_bitshares_instance = bitshares_instance
