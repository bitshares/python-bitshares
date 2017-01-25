from bitsharesbase.account import PrivateKey, GPHPrivateKey
from . import bitshares as bts
from bitsharesbase import bip38
from .exceptions import (
    NoWallet,
    InvalidWifError,
    WalletExists
)
import os
import json
from appdirs import user_data_dir
import logging
from .account import Account

log = logging.getLogger(__name__)


class Wallet():
    """ The wallet is meant to maintain access to private keys for
        your accounts. It either uses manually provided private keys
        or uses a SQLite database managed by storage.py.

        :param SteemNodeRPC rpc: RPC connection to a Steem node
        :param array,dict,string keys: Predefine the wif keys to shortcut the wallet database

        Three wallet operation modes are possible:

        * **Wallet Database**: Here, steemlibs loads the keys from the
          locally stored wallet SQLite database (see ``storage.py``).
          To use this mode, simply call ``Steem()`` without the
          ``keys`` parameter
        * **Providing Keys**: Here, you can provide the keys for
          your accounts manually. All you need to do is add the wif
          keys for the accounts you want to use as a simple array
          using the ``keys`` parameter to ``Steem()``.
        * **Force keys**: This more is for advanced users and
          requires that you know what you are doing. Here, the
          ``keys`` parameter is a dictionary that overwrite the
          ``active``, ``owner``, ``posting`` or ``memo`` keys for
          any account. This mode is only used for *foreign*
          signatures!
    """
    keys = []
    rpc = None
    masterpassword = None

    # Keys from database
    configStorage = None
    MasterPassword = None
    keyStorage = None

    # Manually provided keys
    keys = {}  # struct with pubkey as key and wif as value
    keyMap = {}  # type:wif pairs to force certain keys

    def __init__(self, *args, **kwargs):
        Wallet.rpc = bts.BitShares.rpc
        self.prefix = Wallet.rpc.chain_params["prefix"]

        # Compatibility after name change from wif->keys
        if "wif" in kwargs and "keys" not in kwargs:
            kwargs["keys"] = kwargs["wif"]

        if "keys" in kwargs:
            self.setKeys(kwargs["keys"])
        else:
            """ If no keys are provided manually we load the SQLite
                keyStorage
            """
            from .storage import (keyStorage,
                                  MasterPassword,
                                  configStorage)
            self.configStorage = configStorage
            self.MasterPassword = MasterPassword
            self.keyStorage = keyStorage

    def setKeys(self, loadkeys):
        """ This method is strictly only for in memory keys that are
            passed to Wallet/BitShares with the ``keys`` argument
        """
        log.debug("Force setting of private keys. Not using the wallet database!")
        if isinstance(loadkeys, dict):
            Wallet.keyMap = loadkeys
            loadkeys = list(loadkeys.values())
        elif not isinstance(loadkeys, list):
            loadkeys = [loadkeys]

        for wif in loadkeys:
            try:
                key = PrivateKey(wif)
            except:
                raise InvalidWifError
            self.keys[format(key.pubkey, self.prefix)] = str(key)

    def unlock(self, pwd=None):
        """ Unlock the wallet database
        """
        if not self.created():
            self.newWallet()

        if (self.masterpassword is None and
                self.configStorage[self.MasterPassword.config_key]):
            if pwd is None:
                pwd = self.getPassword()
            masterpwd = self.MasterPassword(pwd)
            self.masterpassword = masterpwd.decrypted_master

    def lock(self):
        """ Lock the wallet database
        """
        self.masterpassword = None

    def locked(self):
        """ Is the wallet database locked?
        """
        return False if self.masterpassword else True

    def changePassphrase(self):
        """ Change the passphrase for the wallet database
        """
        # Open Existing Wallet
        pwd = self.getPassword()
        masterpwd = self.MasterPassword(pwd)
        self.masterpassword = masterpwd.decrypted_master
        # Provide new passphrase
        print("Please provide the new password")
        newpwd = self.getPassword(confirm=True)
        # Change passphrase
        masterpwd.changePassword(newpwd)

    def created(self):
        """ Do we have a wallet database already?
        """
        if len(self.getPublicKeys()):
            # Already keys installed
            return True
        elif self.MasterPassword.config_key in self.configStorage:
            # no keys but a master password
            return True
        else:
            return False

    def newWallet(self):
        """ Create a new wallet database
        """
        if self.created():
            raise WalletExists("You already have created a wallet!")
        print("Please provide a password for the new wallet")
        pwd = self.getPassword(confirm=True)
        masterpwd = self.MasterPassword(pwd)
        self.masterpassword = masterpwd.decrypted_master

    def encrypt_wif(self, wif):
        """ Encrypt a wif key
        """
        self.unlock()
        return format(bip38.encrypt(PrivateKey(wif), self.masterpassword), "encwif")

    def decrypt_wif(self, encwif):
        """ decrypt a wif key
        """
        try:
            # Try to decode as wif
            PrivateKey(encwif)
            return encwif
        except:
            pass
        self.unlock()
        return format(bip38.decrypt(encwif, self.masterpassword), "wif")

    def getPassword(self, confirm=False, text='Passphrase: '):
        """ Obtain a password from the user
        """
        import getpass
        if "UNLOCK" in os.environ:
            # overwrite password from environmental variable
            return os.environ.get("UNLOCK")
        if confirm:
            # Loop until both match
            while True:
                pw = self.getPassword(confirm=False)
                if not pw:
                    print(
                        "You cannot chosen an empty password! " +
                        "If you want to automate the use of the libs, " +
                        "please use the `UNLOCK` environmental variable!"
                    )
                    continue
                else:
                    pwck = self.getPassword(
                        confirm=False,
                        text="Confirm Passphrase: "
                    )
                    if (pw == pwck):
                        return(pw)
                    else:
                        print("Given Passphrases do not match!")
        else:
            # return just one password
            return getpass.getpass(text)

    def addPrivateKey(self, wif):
        """ Add a private key to the wallet database
        """
        # it could be either graphenebase or bitsharesbase so we can't check the type directly
        if isinstance(wif, PrivateKey) or isinstance(wif, GPHPrivateKey):
            wif = str(wif)
        try:
            pub = format(PrivateKey(wif).pubkey, self.prefix)
        except:
            raise InvalidWifError("Invalid Private Key Format. Please use WIF!")

        if self.keyStorage:
            # Test if wallet exists
            if not self.created():
                self.newWallet()
            self.keyStorage.add(self.encrypt_wif(wif), pub)

    def getPrivateKeyForPublicKey(self, pub):
        """ Obtain the private key for a given public key

            :param str pub: Public Key
        """
        if self.keyStorage:
            # Test if wallet exists
            if not self.created():
                self.newWallet()

            return self.decrypt_wif(self.keyStorage.getPrivateKeyForPublicKey(pub))
        else:
            if pub in self.keys:
                return self.keys[pub]
            elif len(self.keys) == 1:
                # If there is only one key in my overwrite-storage, then
                # use that one! Feather it will has sufficient
                # authorization is left to ensure by the developer
                return list(self.keys.values())[0]

    def removePrivateKeyFromPublicKey(self, pub):
        """ Remove a key from the wallet database
        """
        if self.keyStorage:
            # Test if wallet exists
            if not self.created():
                self.newWallet()
            self.keyStorage.delete(pub)

    def removeAccount(self, account):
        """ Remove all keys associated with a given account
        """
        accounts = self.getAccounts()
        for a in accounts:
            if a["name"] == account:
                self.removePrivateKeyFromPublicKey(a["pubkey"])

    def getOwnerKeyForAccount(self, name):
        """ Obtain owner Private Key for an account from the wallet database
        """
        if "owner" in Wallet.keyMap:
            return Wallet.keyMap.get("owner")
        else:
            account = self.rpc.get_account(name)
            if not account:
                return
            for authority in account["owner"]["key_auths"]:
                key = self.getPrivateKeyForPublicKey(authority[0])
                if key:
                    return key
            return False

    def getMemoKeyForAccount(self, name):
        """ Obtain owner Memo Key for an account from the wallet database
        """
        if "memo" in Wallet.keyMap:
            return Wallet.keyMap.get("memo")
        else:
            account = self.rpc.get_account(name)
            if not account:
                return
            key = self.getPrivateKeyForPublicKey(account["options"]["memo_key"])
            if key:
                return key
            return False

    def getActiveKeyForAccount(self, name):
        """ Obtain owner Active Key for an account from the wallet database
        """
        if "active" in Wallet.keyMap:
            return Wallet.keyMap.get("active")
        else:
            account = self.rpc.get_account(name)
            if not account:
                return
            for authority in account["active"]["key_auths"]:
                key = self.getPrivateKeyForPublicKey(authority[0])
                if key:
                    return key
            return False

    def getAccountFromPrivateKey(self, wif):
        """ Obtain account name from private key
        """
        pub = format(PrivateKey(wif).pubkey, self.prefix)
        return self.getAccountFromPublicKey(pub)

    def getAccountFromPublicKey(self, pub):
        """ Obtain account name from public key
        """
        # FIXME, this only returns the first associated key.
        # If the key is used by multiple accounts, this
        # will surely lead to undesired behavior
        names = self.rpc.get_key_references([pub])[0]
        if not names:
            return None
        else:
            return names[0]

    def getAccount(self, pub):
        """ Get the account data for a public key
        """
        name = self.getAccountFromPublicKey(pub)
        if not name:
            return {"name": None,
                    "type": None,
                    "pubkey": pub
                    }
        else:
            try:
                account = Account(name)
            except:
                return
            keyType = self.getKeyType(account, pub)
            return {"name": account["name"],
                    "account": account,
                    "type": keyType,
                    "pubkey": pub
                    }

    def getKeyType(self, account, pub):
        """ Get key type
        """
        if pub == account["options"]["memo_key"]:
            return "memo"
        for authority in ["owner", "active"]:
            for key in account[authority]["key_auths"]:
                if pub == key[0]:
                    return authority
        return None

    def getAccounts(self):
        """ Return all accounts installed in the wallet database
        """
        pubkeys = self.getPublicKeys()
        accounts = []
        for pubkey in pubkeys:
            # Filter those keys not for our network
            if pubkey[:len(self.prefix)] == self.prefix:
                accounts.append(self.getAccount(pubkey))
        return accounts

    def getPublicKeys(self):
        """ Return all installed public keys
        """
        if self.keyStorage:
            return self.keyStorage.getPublicKeys()
        else:
            return list(self.keys.keys())
