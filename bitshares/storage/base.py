import os
import hashlib

from graphenebase import bip38
from bitsharesbase.account import PrivateKey
from binascii import hexlify

from ..aes import AESCipher

class BaseStore(dict):
    defaults = {}

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
        return dict.__iter__(self)

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
        keys = list(self.keys()).copy()
        for key in keys:
            self.delete(key)


class DefaultConfigurationStore(BaseStore):

    defaults = {
        "node": "wss://node.bitshares.eu",
        "rpcpassword": "",
        "rpcuser": "",
        "order-expiration": 7 * 24 * 60 * 60,
    }


class MasterPassword(object):
    """ The keys are encrypted with a Masterpassword that is stored in
        the configurationStore. It has a checksum to verify correctness
        of the password
    """

    password = None
    decrypted_master = None

    #: This key identifies the encrypted master password stored in the
    #: confiration
    storage_key = "encrypted_master_password"

    def __init__(self, storage=None):
        """ The encrypted private keys in `keys` are encrypted with a
            random encrypted masterpassword that is stored in the
            configuration.
        """
        self.storage = storage

    @property
    def masterkey(self):
        return self.decrypted_master

    def has_masterpassword(self):
        return self.storage_key in self.storage

    def unlocked(self):
        return bool(self.password)

    def lock(self):
        self.password = None

    def unlock(self, password):
        """ The password is used to encrypt this masterpassword. To
            decrypt the keys stored in the keys database, one must use
            BIP38, decrypt the masterpassword from the configuration
            store with the user password, and use the decrypted
            masterpassword to decrypt the BIP38 encrypted private keys
            from the keys storage!

            :param str password: Password to use for en-/de-cryption
        """
        self.password = password
        if self.storage_key not in self.storage:
            self.newMaster()
            self.saveEncrytpedMaster()
        else:
            self.decryptEncryptedMaster()

    def decryptEncryptedMaster(self):
        """ Decrypt the encrypted masterpassword
        """
        aes = AESCipher(self.password)
        checksum, encrypted_master = self.storage[self.storage_key].split("$")
        try:
            decrypted_master = aes.decrypt(encrypted_master)
        except:
            raise WrongMasterPasswordException
        if checksum != self.deriveChecksum(decrypted_master):
            raise WrongMasterPasswordException
        self.decrypted_master = decrypted_master

    def saveEncrytpedMaster(self):
        self.storage[self.storage_key] = self.getEncryptedMaster()

    def newMaster(self, password):
        """ Generate a new random masterpassword
        """
        # make sure to not overwrite an existing key
        if (self.storage_key in self.storage and
                self.storage[self.storage_key]):
            raise Exception("Storage already has a masterpassword!")

        self.decrypted_master = hexlify(os.urandom(32)).decode("ascii")

        # Encrypt and save master
        self.password = password
        self.saveEncrytpedMaster()
        return self.masterkey

    def deriveChecksum(self, s):
        """ Derive the checksum
        """
        checksum = hashlib.sha256(bytes(s, "ascii")).hexdigest()
        return checksum[:4]

    def getEncryptedMaster(self):
        """ Obtain the encrypted masterkey
        """
        if not self.masterkey:
            raise Exception("master not decrypted")
        if not self.unlocked():
            raise Exception("Need to unlock storage!")
        aes = AESCipher(self.password)
        return "{}${}".format(
            self.deriveChecksum(self.masterkey),
            aes.encrypt(self.masterkey)
        )

    def changePassword(self, newpassword):
        """ Change the password
        """
        assert self.unlocked()
        self.password = newpassword
        self.saveEncrytpedMaster()

class BaseKeyStore(BaseStore):

    defaults = {}

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


class DefaultEncryptedKeyStore(BaseKeyStore, MasterPassword):

    defaults = {}

    def __init__(self, *args, **kwargs):
        MasterPassword.__init__(self, *args, **kwargs)

    # Interface to deal with encrypted keys
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
        assert self.unlocked()
        wif = self.get(pub, None)
        if wif:
            return format(
                bip38.decrypt(wif, self.masterkey),
                "wif"
            )

    def add(self, wif, pub=None):
        """ Add a new public/private key pair (correspondence has to be
            checked elsewhere!)

           :param str pub: Public key
           :param str wif: Private key
        """
        assert self.unlocked()
        if not pub:
            pub = str(PrivateKey(wif).pubkey)
        self[pub] = format(bip38.encrypt(
                PrivateKey(wif),
                self.masterkey
            ), "encwif")


class InRamKeyStore(BaseKeyStore):

    defaults = {
        # Well-known key
        "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV": "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
    }

    # Interface to deal with encrypted keys
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

    def add(self, wif, pub=None):
        """ Add a new public/private key pair (correspondence has to be
            checked elsewhere!)

           :param str pub: Public key
           :param str wif: Private key
        """
        if not pub:
            pub = str(PrivateKey(wif).pubkey)
        self[pub] = wif
