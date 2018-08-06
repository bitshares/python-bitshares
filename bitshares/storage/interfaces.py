class StoreInterface:

    def __init__(self, *args, **kwargs):
        pass

    def __setitem__(self, key, value):
        """ Sets an item in the store
        """
        pass

    def __getitem__(self, key):
        """ Gets an item from the store as if it was a dictionary
        """
        pass

    def __iter__(self):
        """ Iterates through the store
        """
        pass

    def __len__(self):
        """ return lenght of store
        """
        pass

    def __contains__(self, key):
        """ Tests if a key is contained in the store.
        """
        pass

    def items(self):
        """ returns all items off the store as tuples
        """
        pass

    def get(self, key, default=None):
        """ Return the key if exists or a default value
        """
        pass

    # Specific for this library
    def delete(self, key):
        """ Delete a key from the store
        """
        pass

    def wipe(self):
        """ Wipe the store
        """
        pass


class KeyInterface(StoreInterface):
    """ The BaseKeyStore defines the interface for key storage
    """

    # Interface to deal with encrypted keys
    def getPublicKeys(self):
        """ Returns the public keys stored in the database
        """
        pass

    def getPrivateKeyForPublicKey(self, pub):
        """ Returns the (possibly encrypted) private key that
            corresponds to a public key

           :param str pub: Public key

           The encryption scheme is BIP38
        """
        pass

    def add(self, wif, pub=None):
        """ Add a new public/private key pair (correspondence has to be
            checked elsewhere!)

           :param str pub: Public key
           :param str wif: Private key
        """
        pass

    def delete(self, pub):
        """ Delete a pubkey/privatekey pair from the store
        """
        pass

    def is_encrypted(self):
        """ Returns True/False to indicate required use of unlock
        """
        return False

    def unlock(self, password):
        """ Tries to unlock the wallet if required
        """
        pass

    def locked(self):
        """ is the wallet locked?
        """
        return False

    def lock(self):
        """ Lock the wallet again
        """
        pass


class ConfigInterface(StoreInterface):
    """ The BaseKeyStore defines the interface for key storage
    """
    pass
