class BaseConfiguration():

    defaults = {
        "node": "wss://node.bitshares.eu",
        "rpcpassword": "",
        "rpcuser": "",
        "order-expiration": 7 * 24 * 60 * 60,
    }

    def __setitem__(self, key, value):
        """ Sets an item in the store
        """
        return dict.__setitem__(self.defaults, key, value)

    def __getitem__(self, key):
        """ Gets an item from the store as if it was a dictionary
        """
        return dict.__getitem__(self.defaults, key)

    def __iter__(self):
        """ Iterates through the store
        """
        return iter(self.store)

    def items(self):
        """ returns all items off the store as tuples
        """
        return self.defaults.items()

    def __len__(self):
        """ return lenght of store
        """
        return len(self.defaults.keys())

    def __contains__(self, key):
        """ Tests if a key is contained in the store.

            May test againsts self.defaults
        """
        return key in self.defaults

    def get(self, key, default=None):
        """ Return the key if exists or a default value
        """
        if key in self:
            return self.__getitem__(key)
        else:
            return default

    def delete(self, key):
        """ Delete a key from the store
        """
        self.defaults.pop(key, None)

    def wipe(self):
        """ Wipe the store
        """
        self.defaults = dict()

    def create(self):
        """ Creates the store if not exists()
        """
        pass

    def exists(self):
        """ Returns True if the store exists
        """
        return True
