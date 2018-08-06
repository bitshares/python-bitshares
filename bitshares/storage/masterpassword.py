import os
import hashlib
from graphenebase import bip38
from graphenebase.base58 import Base58
from binascii import hexlify
from ..aes import AESCipher
from ..exceptions import WrongMasterPasswordException


class MasterPassword(object):
    """ The keys are encrypted with a Masterpassword that is stored in
        the configurationStore. It has a checksum to verify correctness
        of the password
    """

    password = None
    decrypted_master = None

    #: This key identifies the encrypted master password stored in the
    #: confiration
    config_key = "encrypted_master_password"

    def __init__(self, config=None, **kwargs):
        """ The encrypted private keys in `keys` are encrypted with a
            random encrypted masterpassword that is stored in the
            configuration.

            :param ConfigStore config: Configuration store to get access to the
                encrypted master password
        """
        if config is None:
            raise ValueError("If using encrypted store, a config store is required!")
        self.config = config

    @property
    def masterkey(self):
        return self.decrypted_master

    def has_masterpassword(self):
        return self.config_key in self.config

    def locked(self):
        return not self.unlocked()

    def unlocked(self):
        try:
            self.tryUnlockFromEnv()
        except:
            pass
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
        if self.config_key not in self.config:
            self.newMaster(password)
            self.saveEncrytpedMaster()
        else:
            self.decryptEncryptedMaster()

    def decryptEncryptedMaster(self):
        """ Decrypt the encrypted masterpassword
        """
        aes = AESCipher(self.password)
        checksum, encrypted_master = self.config[self.config_key].split("$")
        try:
            decrypted_master = aes.decrypt(encrypted_master)
        except:
            raise WrongMasterPasswordException
        if checksum != self.deriveChecksum(decrypted_master):
            raise WrongMasterPasswordException
        self.decrypted_master = decrypted_master

    def saveEncrytpedMaster(self):
        self.config[self.config_key] = self.getEncryptedMaster()

    def newMaster(self, password):
        """ Generate a new random masterpassword
        """
        # make sure to not overwrite an existing key
        if (self.config_key in self.config and
                self.config[self.config_key]):
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

    def tryUnlockFromEnv(self):
        if self.unlocked():
            return
        if "UNLOCK" in os.environ:
            log.debug("Trying to use environmental variable to unlock wallet")
            self.unlock(os.environ.get("UNLOCK"))
        else:
            raise WrongMasterPasswordException

    def decrypt(self, wif):
        return format(
            bip38.decrypt(wif, self.masterkey),
            "wif"
        )

    def encrypt(self, wif):
        return format(bip38.encrypt(
            str(wif),
            self.masterkey
        ), "encwif")
