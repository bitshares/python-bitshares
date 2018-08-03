import logging
import os
from graphenebase import bip38
# from bitsharesbase.account import PrivateKey
from .storage import DefaultConfigurationStore, InRamKeyStore, DefaultEncryptedKeyStore
from .instance import BlockchainInstance
from .account import Account
from .exceptions import (
    KeyNotFound,
    InvalidWifError,
    WalletExists,
    WalletLocked,
    NoWalletException,
    OfflineHasNoRPCException
)


log = logging.getLogger(__name__)


class Wallet():
    """ The wallet is meant to maintain access to private keys for
        your accounts. It either uses manually provided private keys
        or uses a SQLite database managed by storage.py.

        :param BitSharesNodeRPC rpc: RPC connection to a BitShares node
        :param array,dict,string keys: Predefine the wif keys to shortcut the
               wallet database

        Three wallet operation modes are possible:

        * **Wallet Database**: Here, pybitshares loads the keys from the
          locally stored wallet SQLite database (see ``storage.py``).
          To use this mode, simply call ``BitShares()`` without the
          ``keys`` parameter
        * **Providing Keys**: Here, you can provide the keys for
          your accounts manually. All you need to do is add the wif
          keys for the accounts you want to use as a simple array
          using the ``keys`` parameter to ``BitShares()``.
        * **Force keys**: This more is for advanced users and
          requires that you know what you are doing. Here, the
          ``keys`` parameter is a dictionary that overwrite the
          ``active``, ``owner``, ``posting`` or ``memo`` keys for
          any account. This mode is only used for *foreign*
          signatures!
    """
    def __init__(self, *args, **kwargs):
        BlockchainInstance.__init__(self, *args, **kwargs)

        self.config = kwargs.get(
            "config_store",
            DefaultConfigurationStore()
        )
        self.store = kwargs.get(
            "key_store",
            InRamKeyStore(config=self.config)
        )

        # Compatibility after name change from wif->keys
        if "wif" in kwargs and "keys" not in kwargs:
            kwargs["keys"] = kwargs["wif"]

        if "keys" in kwargs:
            self.setKeys(kwargs["keys"])

    @property
    def prefix(self):
        if self.blockchain.is_connected():
            prefix = self.blockchain.prefix
        else:
            # If not connected, load prefix from config
            prefix = self.config["prefix"]
        return prefix or "BTS"   # default prefix is BTS

    @property
    def rpc(self):
        if not self.blockchain.is_connected():
            raise OfflineHasNoRPCException("No RPC available in offline mode!")
        return self.blockchain.rpc

    def setKeys(self, loadkeys):
        """ This method is strictly only for in memory keys that are
            passed to Wallet/BitShares with the ``keys`` argument
        """
        log.debug(
            "Force setting of private keys. Not using the wallet database!")
        if isinstance(loadkeys, dict):
            loadkeys = list(loadkeys.values())
        elif not isinstance(loadkeys, list):
            loadkeys = [loadkeys]

        for wif in loadkeys:
            assert hasattr(wif, "pubkey"), "Requires an instance of PrivateKey"
            pub = str(wif.pubkey)
            self.store.add(str(wif), pub)

    def unlock(self, pwd=None):
        """ Unlock the wallet database
        """
        if isinstance(self.store, DefaultEncryptedKeyStore):
            return self.store.unlock()

    def lock(self):
        """ Lock the wallet database
        """
        if isinstance(self.store, DefaultEncryptedKeyStore):
            return self.store.lock()

    def unlocked(self):
        """ Is the wallet database unlocked?
        """
        if isinstance(self.store, DefaultEncryptedKeyStore):
            return self.store.locked()
        if isinstance(self.store, InRamKeyStore):
            return True

    def locked(self):
        """ Is the wallet database locked?
        """
        if isinstance(self.store, InRamKeyStore):
            return False

        if isinstance(self.store, DefaultEncryptedKeyStore):
            try:
                self.store.tryUnlockFromEnv()
            except:
                pass
            return self.store.locked()

    def changePassphrase(self, new_pwd):
        """ Change the passphrase for the wallet database
        """
        assert not self.locked()
        self.masterpwd.changePassword(new_pwd)

    def created(self):
        """ Do we have a wallet database already?
        """
        if len(self.store.getPublicKeys()):
            # Already keys installed
            return True
        else:
            return False

    def create(self, pwd):
        """ Alias for newWallet()
        """
        pass

    def newWallet(self, pwd):
        """ Create a new wallet database
        """
        pass

    def addPrivateKey(self, wif):
        """ Add a private key to the wallet database
        """
        assert hasattr(wif, "pubkey"), "Requires an instance of PrivateKey"
        pub = str(wif.pubkey)
        self.store.add(str(wif), pub)

    def getPrivateKeyForPublicKey(self, pub):
        """ Obtain the private key for a given public key

            :param str pub: Public Key
        """
        return self.store.getPrivateKeyForPublicKey(pub)

    def removePrivateKeyFromPublicKey(self, pub):
        """ Remove a key from the wallet database
        """
        self.store.delete(str(pub))

    def removeAccount(self, account):
        """ Remove all keys associated with a given account
        """
        accounts = self.getAccounts()
        for a in accounts:
            if a["name"] == account:
                self.store.delete(a["pubkey"])

    def getOwnerKeyForAccount(self, name):
        """ Obtain owner Private Key for an account from the wallet database
        """
        account = self.rpc.get_account(name)
        for authority in account["owner"]["key_auths"]:
            key = self.getPrivateKeyForPublicKey(authority[0])
            if key:
                return key
        return False

    def getMemoKeyForAccount(self, name):
        """ Obtain owner Memo Key for an account from the wallet database
        """
        account = self.rpc.get_account(name)
        key = self.getPrivateKeyForPublicKey(
            account["options"]["memo_key"])
        if key:
            return key
        return False

    def getActiveKeyForAccount(self, name):
        """ Obtain owner Active Key for an account from the wallet database
        """
        account = self.rpc.get_account(name)
        for authority in account["active"]["key_auths"]:
            key = self.getPrivateKeyForPublicKey(authority[0])
            if key:
                return key
        return False

    def getAccountFromPrivateKey(self, wif):
        """ Obtain account name from private key
        """
        assert hasattr(wif, "pubkey"), "Requires an instance of PrivateKey"
        pub = str(wif.pubkey)
        return self.getAccountFromPublicKey(pub)

    def getAccountsFromPublicKey(self, pub):
        """ Obtain all accounts associated with a public key
        """
        names = self.rpc.get_key_references([pub])
        for name in names:
            for i in name:
                yield i

    def getAccountFromPublicKey(self, pub):
        """ Obtain the first account name from public key
        """
        # FIXME, this only returns the first associated key.
        # If the key is used by multiple accounts, this
        # will surely lead to undesired behavior
        names = self.rpc.get_key_references([pub])[0]
        if not names:
            return None
        else:
            return names[0]

    def getAllAccounts(self, pub):
        """ Get the account data for a public key (all accounts found for this
            public key)
        """
        for id in self.getAccountsFromPublicKey(pub):
            try:
                account = Account(id, blockchain_instance=self.blockchain)
            except:
                continue
            yield {"name": account["name"],
                   "account": account,
                   "type": self.getKeyType(account, pub),
                   "pubkey": pub}

    def getKeyType(self, account, pub):
        """ Get key type
        """
        for authority in ["owner", "active"]:
            for key in account[authority]["key_auths"]:
                if pub == key[0]:
                    return authority
        if pub == account["options"]["memo_key"]:
            return "memo"
        return None

    def getAccounts(self):
        """ Return all accounts installed in the wallet database
        """
        pubkeys = self.getPublicKeys()
        accounts = []
        for pubkey in pubkeys:
            # Filter those keys not for our network
            if pubkey[:len(self.prefix)] == self.prefix:
                accounts.extend(self.getAllAccounts(pubkey))
        return accounts

    def getPublicKeys(self):
        """ Return all installed public keys
        """
        return self.store.getPublicKeys()

    def wipe(self, sure=False):
        if not sure:
            log.error(
                "You need to confirm that you are sure "
                "and understand the implications of "
                "wiping your wallet!"
            )
            return
        else:
            self.store.wipe()
