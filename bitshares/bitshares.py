import json
import logging
import random
import re
from datetime import datetime, timedelta

from bitsharesapi.noderpc import BitSharesNodeRPC
from bitsharesbase.account import PrivateKey, PublicKey
from bitsharesbase import transactions, operations
from .asset import Asset
from .account import Account
from .amount import Amount
from .storage import configStorage as config
from .exceptions import (
    AccountExistsException,
    AccountDoesNotExistsException,
    InsufficientAuthorityError,
    MissingKeyError,
)
from .wallet import Wallet
from .transactionbuilder import TransactionBuilder

log = logging.getLogger(__name__)

prefix = "BTS"


class BitShares(object):
    """ The purpose of this class it to simplify interaction with
        BitShares.

        The idea is to have a class that allows to do this:

        .. code-block:: python

            from bitshares import BitShares
            bitshares = BitShares()
            print(bitshares.info())

        All that is requires is for the user to have added a key with uptick

        .. code-block:: bash

            uptick addkey

        and setting a default author:

        .. code-block:: bash

            uptick set default_account xeroc

        This class also deals with edits, votes and reading content.
    """

    wallet = None
    rpc = None
    debug = None
    nobroadcast = None
    unsigned = None
    expiration = None

    def __init__(self,
                 node="",
                 rpcuser="",
                 rpcpassword="",
                 debug=False,
                 **kwargs):
        """ Connect to the BitShares network.

            :param str node: Node to connect to *(optional)*
            :param str rpcuser: RPC user *(optional)*
            :param str rpcpassword: RPC password *(optional)*
            :param bool nobroadcast: Do **not** broadcast a transaction! *(optional)*
            :param bool debug: Enable Debugging *(optional)*
            :param array,dict,string keys: Predefine the wif keys to shortcut the wallet database
            :param bool skipcreatewallet: Skip creation of a wallet

            Three wallet operation modes are possible:

            * **Wallet Database**: Here, the bitshareslibs load the keys from the
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
              ``active``, ``owner``, or ``memo`` keys for
              any account. This mode is only used for *foreign*
              signatures!

            If no node is provided, it will connect to the node of
            http://uptick.rocks. It is **highly** recommended that you pick your own
            node instead. Default settings can be changed with:

            .. code-block:: python

                uptick set node <host>

            where ``<host>`` starts with ``ws://`` or ``wss://``.
        """
        # More specific set of APIs to register to
        if "apis" not in kwargs:
            kwargs["apis"] = [
                "database",
                "network_broadcast",
                "account_by_key",
                "follow",
            ]

        if not BitShares.rpc:
            """ Connect to BitShares network
            """
            if not node:
                if "node" in config:
                    node = config["node"]
                else:
                    raise ValueError("A BitShares node needs to be provided!")
            if not rpcuser and "rpcuser" in config:
                rpcuser = config["rpcuser"]
            if not rpcpassword and "rpcpassword" in config:
                rpcpassword = config["rpcpassword"]
            BitShares.rpc = BitSharesNodeRPC(node, rpcuser, rpcpassword, **kwargs)

        if BitShares.debug is None:
            BitShares.debug = debug
        if BitShares.nobroadcast is None:
            BitShares.nobroadcast = kwargs.get("nobroadcast", False)
        if BitShares.unsigned is None:
            BitShares.unsigned = kwargs.pop("unsigned", False)
        if BitShares.expiration is None:
            BitShares.expiration = int(kwargs.pop("expires", 30))

        # Compatibility after name change from wif->keys
        if "wif" in kwargs and "keys" not in kwargs:
            kwargs["keys"] = kwargs["wif"]

        if self.wallet is None:
            if "keys" in kwargs:
                BitShares.wallet = Wallet(self.rpc, keys=kwargs["keys"])
            else:
                BitShares.wallet = Wallet(self.rpc)

    def newWallet(self):
        self.wallet.newWallet()

    def finalizeOp(self, op, account, permission):
        tx = TransactionBuilder()
        tx.appendOps(op)
        tx.appendSigner(account, permission)
        tx.constructTx()
        tx.sign()
        return tx.broadcast()

    def info(self):
        """ Returns the global properties
        """
        return self.rpc.get_dynamic_global_properties()

    def create_account(self,
                       account_name,
                       json_meta={},
                       registrar=None,
                       referrer="1.2.35641",
                       referrer_percent=50,
                       owner_key=None,
                       active_key=None,
                       memo_key=None,
                       password=None,
                       additional_owner_keys=[],
                       additional_active_keys=[],
                       additional_owner_accounts=[],
                       additional_active_accounts=[],
                       storekeys=True,
                       ):
        """ Create new account on BitShares

            The brainkey/password can be used to recover all generated keys (see
            `bitsharesbase.account` for more details.

            By default, this call will use ``default_account`` to
            register a new name ``account_name`` with all keys being
            derived from a new brain key that will be returned. The
            corresponding keys will automatically be installed in the
            wallet.

            .. warning:: Don't call this method unless you know what
                          you are doing! Be sure to understand what this
                          method does and where to find the private keys
                          for your account.

            .. note:: Please note that this imports private keys
                      (if password is present) into the wallet by
                      default. However, it **does not import the owner
                      key** for security reasons. Do NOT expect to be
                      able to recover it from the wallet if you lose
                      your password!

            :param str account_name: (**required**) new account name
            :param str json_meta: Optional meta data for the account
            :param str registrar: which account should pay the registration fee
                                (defaults to ``default_account``)
            :param str owner_key: Main owner key
            :param str active_key: Main active key
            :param str memo_key: Main memo_key
            :param str password: Alternatively to providing keys, one
                                 can provide a password from which the
                                 keys will be derived
            :param array additional_owner_keys:  Additional owner public keys
            :param array additional_active_keys: Additional active public keys
            :param array additional_owner_accounts: Additional owner account names
            :param array additional_active_accounts: Additional acctive account names
            :param bool storekeys: Store new keys in the wallet (default: ``True``)
            :raises AccountExistsException: if the account already exists on the blockchain

        """
        if not registrar and config["default_account"]:
            registrar = config["default_account"]
        if not registrar:
            raise ValueError(
                "Not registrar account given. Define it with " +
                "registrar=x, or set the default_account using uptick")
        if password and (owner_key or active_key or memo_key):
            raise ValueError(
                "You cannot use 'password' AND provide keys!"
            )

        try:
            Account(account_name)
            raise AccountExistsException
        except:
            pass

        referrer = Account(referrer)
        registrar = Account(registrar)

        " Generate new keys from password"
        from bitsharesbase.account import PasswordKey, PublicKey
        if password:
            active_key = PasswordKey(account_name, password, role="active")
            owner_key = PasswordKey(account_name, password, role="owner")
            memo_key = PasswordKey(account_name, password, role="memo")
            active_pubkey = active_key.get_public_key()
            owner_pubkey = owner_key.get_public_key()
            memo_pubkey = memo_key.get_public_key()
            active_privkey = active_key.get_private_key()
            # owner_privkey   = owner_key.get_private_key()
            memo_privkey = memo_key.get_private_key()
            # store private keys
            if storekeys:
                # self.wallet.addPrivateKey(owner_privkey)
                self.wallet.addPrivateKey(active_privkey)
                self.wallet.addPrivateKey(memo_privkey)
        elif (owner_key and active_key and memo_key):
            active_pubkey = PublicKey(active_key, prefix=prefix)
            owner_pubkey = PublicKey(owner_key, prefix=prefix)
            memo_pubkey = PublicKey(memo_key, prefix=prefix)
        else:
            raise ValueError(
                "Call incomplete! Provide either a password or public keys!"
            )

        owner = format(owner_pubkey, prefix)
        active = format(active_pubkey, prefix)
        memo = format(memo_pubkey, prefix)

        owner_key_authority = [[owner, 1]]
        active_key_authority = [[active, 1]]
        owner_accounts_authority = []
        active_accounts_authority = []

        # additional authorities
        for k in additional_owner_keys:
            owner_key_authority.append([k, 1])
        for k in additional_active_keys:
            active_key_authority.append([k, 1])

        for k in additional_owner_accounts:
            owner_accounts_authority.append([k, 1])
        for k in additional_active_accounts:
            active_accounts_authority.append([k, 1])

        op = {
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "registrar": registrar["id"],
            "referrer": referrer["id"],
            "referrer_percent": referrer_percent * 100,
            "name": account_name,
            'owner': {'account_auths': owner_accounts_authority,
                      'key_auths': owner_key_authority,
                      "address_auths": [],
                      'weight_threshold': 1},
            'active': {'account_auths': active_accounts_authority,
                       'key_auths': active_key_authority,
                       "address_auths": [],
                       'weight_threshold': 1},
            "options": {"memo_key": memo,
                        "voting_account": "1.2.5",
                        "num_witness": 0,
                        "num_committee": 0,
                        "votes": [],
                        "extensions": []
                        },
            "extensions": {}
        }
        op = operations.Account_create(**op)
        return self.finalizeOp(op, registrar, "active")

    def transfer(self, to, amount, asset, memo="", account=None):
        """ Transfer an asset to another account.

            :param str to: Recipient
            :param float amount: Amount to transfer
            :param str asset: Asset to transfer
            :param str memo: (optional) Memo, may begin with `#` for encrypted messaging
            :param str account: (optional) the source account for the transfer if not ``default_account``
        """
        if not account:
            if "default_account" in config:
                account = config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        account = Account(account, bitshares_instance=self)
        amount = Amount(amount, asset, bitshares_instance=self)
        to = Account(to, bitshares_instance=self)

        if memo:
            from .memo import Memo
            memo = Memo(account, to, memo, bitshares_instance=self)

        op = operations.Transfer(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "from": account["id"],
            "to": to["id"],
            "amount": {
                "amount": int(amount),
                "asset_id": amount.asset["id"]
            },
            "memo": memo.encrytped_memo if memo else ""
        })
        return self.finalizeOp(op, account, "active")

    def allow(self, foreign, weight=None, permission="active",
              account=None, threshold=None):
        """ Give additional access to an account by some other public
            key or account.

            :param str foreign: The foreign account that will obtain access
            :param int weight: (optional) The weight to use. If not
                define, the threshold will be used. If the weight is
                smaller than the threshold, additional signatures will
                be required. (defaults to threshold)
            :param str permission: (optional) The actual permission to
                modify (defaults to ``active``)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
            :param int threshold: The threshold that needs to be reached
                by signatures to be able to interact
        """
        if not account:
            if "default_account" in config:
                account = config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        if permission not in ["owner", "active"]:
            raise ValueError(
                "Permission needs to be either 'owner', or 'active"
            )
        account = self.rpc.get_account(account)
        if not account:
            raise AccountDoesNotExistsException(account)

        if not weight:
            weight = account[permission]["weight_threshold"]

        authority = account[permission]
        try:
            pubkey = PublicKey(foreign)
            authority["key_auths"].append([
                str(pubkey),
                weight
            ])
        except:
            try:
                foreign_account = Account(foreign)
                authority["account_auths"].append([
                    foreign_account["id"],
                    weight
                ])
            except:
                raise ValueError(
                    "Unknown foreign account or unvalid public key"
                )
        if threshold:
            authority["weight_threshold"] = threshold
            self._test_weights_treshold(authority)

        op = operations.Account_update(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "account": account["id"],
            permission: authority,
            "extensions": {}
        })
        if permission == "owner":
            return self.finalizeOp(op, account["name"], "owner")
        else:
            return self.finalizeOp(op, account["name"], "active")

    def disallow(self, foreign, permission="active",
                 account=None, threshold=None):
        """ Remove additional access to an account by some other public
            key or account.

            :param str foreign: The foreign account that will obtain access
            :param str permission: (optional) The actual permission to
                modify (defaults to ``active``)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
            :param int threshold: The threshold that needs to be reached
                by signatures to be able to interact
        """
        if not account:
            if "default_account" in config:
                account = config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        if permission not in ["owner", "active"]:
            raise ValueError(
                "Permission needs to be either 'owner', or 'active"
            )
        account = self.rpc.get_account(account)
        if not account:
            raise AccountDoesNotExistsException(account)
        authority = account[permission]

        try:
            pubkey = PublicKey(foreign)
            affected_items = list(
                filter(lambda x: x[0] == str(pubkey),
                       authority["key_auths"]))
            authority["key_auths"] = list(filter(
                lambda x: x[0] != str(pubkey),
                authority["key_auths"]
            ))
        except:
            try:
                foreign_account = self.rpc.get_account(foreign)
                affected_items = list(
                    filter(lambda x: x[0] == foreign_account["name"],
                           authority["account_auths"]))
                authority["account_auths"] = list(filter(
                    lambda x: x[0] != foreign_account["name"],
                    authority["account_auths"]
                ))
            except:
                raise ValueError(
                    "Unknown foreign account or unvalid public key"
                )

        removed_weight = affected_items[0][1]

        # Define threshold
        if threshold:
            authority["weight_threshold"] = threshold

        # Correct threshold (at most by the amount removed from the
        # authority)
        try:
            self._test_weights_treshold(authority)
        except:
            log.critical(
                "The account's threshold will be reduced by %d"
                % (removed_weight)
            )
            authority["weight_threshold"] -= removed_weight
            self._test_weights_treshold(authority)

        op = operations.Account_update(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "account": account["id"],
            permission: authority,
            "extensions": {}
        })
        if permission == "owner":
            return self.finalizeOp(op, account["name"], "owner")
        else:
            return self.finalizeOp(op, account["name"], "active")

    def update_memo_key(self, key, account=None):
        """ Update an account's memo public key

            This method does **not** add any private keys to your
            wallet but merely changes the memo public key.

            :param str key: New memo public key
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in config:
                account = config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        PublicKey(key)  # raises exception if invalid

        account = self.rpc.get_account(account)
        if not account:
            raise AccountDoesNotExistsException(account)
        account["options"].update({
            "memo_key": "BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE"}
        )
        op = operations.Account_update(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "account": account["id"],
            "new_options": account["options"],
            "extensions": {}
        })
        return self.finalizeOp(op, account["name"], "active")
