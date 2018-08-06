import os
import logging

from .masterpassword import MasterPassword
from .interfaces import KeyInterface, ConfigInterface
from .ram import InRamStore
from .sqlite import SQLiteStore

log = logging.getLogger(__name__)


# Configuration
class InRamConfigurationStore(InRamStore, ConfigInterface):
    """ A simple example that shows how to set defaults
        for the Base Store
    """

    defaults = {
        "node": "wss://node.bitshares.eu",
        "rpcpassword": "",
        "rpcuser": "",
        "order-expiration": 7 * 24 * 60 * 60,
    }


class SqliteConfigurationStore(SQLiteStore, ConfigInterface):
    """ This is the configuration storage that stores key/value
        pairs in the `config` table of the SQLite3 database.
    """
    __tablename__ = "config"
    __key__ = "key"
    __value__ = "value"

    #: Default configuration
    defaults = {
        "node": "wss://node.bitshares.eu",
        "rpcpassword": "",
        "rpcuser": "",
        "order-expiration": 7 * 24 * 60 * 60,
    }


# Keys
class InRamPlainKeyStore(InRamStore, KeyInterface):
    """ A simple Store that stores keys unencrypted in RAM
    """
    def getPublicKeys(self):
        return [k for k, v in self.items()]

    def getPrivateKeyForPublicKey(self, pub):
        return self.get(str(pub), None)

    def add(self, wif, pub):
        self[str(pub)] = str(wif)

    def delete(self, pub):
        InRamStore.delete(self, str(pub))


class InRamEncryptedKeyStore(MasterPassword, InRamStore, KeyInterface):

    # Interface to deal with encrypted keys
    def getPublicKeys(self):
        return [k for k, v in self.items()]

    def getPrivateKeyForPublicKey(self, pub):
        assert self.unlocked()
        wif = self.get(str(pub), None)
        if wif:
            return self.decrypt(wif)  # From Masterpassword

    def add(self, wif, pub):
        assert self.unlocked()  # From Masterpassword
        self[str(pub)] = self.encrypt(str(wif))  # From Masterpassword

    def delete(self, pub):
        InRamStore.delete(self, str(pub))

    def is_encrypted(self):
        return True

    def locked(self):
        return MasterPassword.locked(self)

    def unlock(self, password):
        return MasterPassword.unlock(self, password)

    def lock(self):
        return MasterPassword.lock(self)


class SqlitePlainKeyStore(SQLiteStore, KeyInterface):
    """ This is the key storage that stores the public key and the
        **unencrypted** private key in the `keys` table in the SQLite3
        database.
    """
    __tablename__ = 'keys'
    __key__ = "pub"
    __value__ = "wif"

    def getPublicKeys(self):
        return [k for k, v in self.items()]

    def getPrivateKeyForPublicKey(self, pub):
        return self[pub]

    def add(self, wif, pub=None):
        self[str(pub)] = str(wif)

    def delete(self, pub):
        SQLiteStore.delete(self, str(pub))


class SqliteEncryptedKeyStore(MasterPassword, SQLiteStore, KeyInterface):
    """ This is the key storage that stores the public key and the
        **encrypted** private key in the `keys` table in the SQLite3 database.
    """
    __tablename__ = 'keys'
    __key__ = "pub"
    __value__ = "wif"

    def __init__(self, *args, **kwargs):
        SQLiteStore.__init__(self, *args, **kwargs)
        MasterPassword.__init__(self, *args, **kwargs)

    # Interface to deal with encrypted keys
    def getPublicKeys(self):
        return [k for k, v in self.items()]

    def getPrivateKeyForPublicKey(self, pub):
        assert self.unlocked()
        wif = self.get(str(pub), None)
        if wif:
            return self.decrypt(wif)  # From Masterpassword

    def add(self, wif, pub):
        assert self.unlocked()  # From Masterpassword
        self[str(pub)] = self.encrypt(str(wif))  # From Masterpassword

    def delete(self, pub):
        SQLiteStore.delete(self, str(pub))

    def is_encrypted(self):
        return True

    def locked(self):
        return MasterPassword.locked(self)

    def unlock(self, password):
        return MasterPassword.unlock(self, password)

    def lock(self):
        return MasterPassword.lock(self)
