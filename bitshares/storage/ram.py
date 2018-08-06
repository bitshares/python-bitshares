from .interfaces import StoreInterface


# StoreInterface is done first, then dict which overwrites the interface
# methods
class InRamStore(dict, StoreInterface):
    defaults = {}

    def __init__(self, *args, **kwargs):
        """ Defines the defaults
        """
        dict.__init__(self, self.defaults)
        dict.update(self, *args, **kwargs)

    # Specific for this library
    def delete(self, key):
        """ Delete a key from the store
        """
        self.pop(key, None)

    def wipe(self):
        """ Wipe the store
        """
        keys = list(self.keys()).copy()
        for key in keys:
            self.delete(key)
