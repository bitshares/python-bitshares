class BaseConfiguration(dict):

    defaults = {
        "node": "wss://node.bitshares.eu",
        "rpcpassword": "",
        "rpcuser": "",
        "order-expiration": 7 * 24 * 60 * 60,
    }

    def __init__(self, *args, **kwargs):
        dict.__init__(self, self.defaults)
        dict.update(self, *args, **kwargs)

    def __setitem__(self, key, value):
        """ Sets an item in the store
        """
        return dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        """ Gets an item from the store as if it was a dictionary
        """
        return dict.__getitem__(self, key)

    def __iter__(self):
        """ Iterates through the store
        """
        return iter(self.store)

    def __len__(self):
        """ return lenght of store
        """
        return dict.__len__(self)

    def __contains__(self, key):
        """ Tests if a key is contained in the store.

            May test againsts self.defaults
        """
        return dict.__contains__(self, key)

    def items(self):
        """ returns all items off the store as tuples
        """
        return dict.items(self)

    def get(self, key, default=None):
        """ Return the key if exists or a default value
        """
        return dict.get(self, key, default)

    # Specific for this library
    def delete(self, key):
        """ Delete a key from the store
        """
        self.pop(key, None)

    def wipe(self):
        """ Wipe the store
        """
        for key in self:
            self.delete(key)

    def create(self):
        """ Creates the store if not exists()
        """
        pass

    def exists(self):
        """ Returns True if the store exists
        """
        return True


class BaseKey(dict):

    defaults = {
        # Well-known key
        "PPY6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV": "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
    }

    def __init__(self, *args, **kwargs):
        dict.__init__(self, self.defaults)
        dict.update(self, *args, **kwargs)

    def __setitem__(self, key, value):
        """ Sets an item in the store
        """
        return dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        """ Gets an item from the store as if it was a dictionary
        """
        return dict.__getitem__(self, key)

    def __iter__(self):
        """ Iterates through the store
        """
        return iter(self.store)

    def __len__(self):
        """ return lenght of store
        """
        return dict.__len__(self)

    def __contains__(self, key):
        """ Tests if a key is contained in the store.

            May test againsts self.defaults
        """
        return dict.__contains__(self, key)

    def items(self):
        """ returns all items off the store as tuples
        """
        return dict.items(self)

    def get(self, key, default=None):
        """ Return the key if exists or a default value
        """
        return dict.get(self, key, default)

    # Specific for this library
    def delete(self, key):
        """ Delete a key from the store
        """
        self.pop(key, None)

    def wipe(self):
        """ Wipe the store
        """
        for key in self:
            self.delete(key)

    def create(self):
        """ Creates the store if not exists()
        """
        pass

    def exists(self):
        """ Returns True if the store exists
        """
        return True

    # Legacy Interface
    def getPublicKeys(self):
        """ Returns the public keys stored in the database
        """
        return self.keys()

    def getPrivateKeyForPublicKey(self, pub):
        """ Returns the (possibly encrypted) private key that
            corresponds to a public key

           :param str pub: Public key

           The encryption scheme is BIP38
        """
        return self.get(pub, None)

    def updateWif(self, pub, wif):
        """ Change the wif to a pubkey

           :param str pub: Public key
           :param str wif: Private key
        """
        self[pub] = wif

    def add(self, wif, pub):
        """ Add a new public/private key pair (correspondence has to be
            checked elsewhere!)

           :param str pub: Public key
           :param str wif: Private key
        """
        self[pub] = wif
