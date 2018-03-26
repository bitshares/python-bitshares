import transnet as trns


class SharedInstance():
    instance = None


def shared_transnet_instance():
    """ This method will initialize ``SharedInstance.instance`` and return it.
        The purpose of this method is to have offer single default
        transnet instance that can be reused by multiple classes.
    """
    if not SharedInstance.instance:
        clear_cache()
        SharedInstance.instance = trns.Transnet()
    return SharedInstance.instance


def set_shared_transnet_instance(transnet_instance):
    """ This method allows us to override default transnet instance for all users of
        ``SharedInstance.instance``.

        :param transnet.transnet.Transnet transnet_instance: Transnet instance
    """
    clear_cache()
    SharedInstance.instance = transnet_instance


def clear_cache():
    """ Clear Caches
    """
    from .blockchainobject import BlockchainObject
    BlockchainObject.clear_cache()
