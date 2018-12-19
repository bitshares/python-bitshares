# -*- coding: utf-8 -*-
import logging

from datetime import datetime, timedelta

from graphenecommon.chain import AbstractGrapheneChain

from bitsharesapi.bitsharesnoderpc import BitSharesNodeRPC
from bitsharesbase import operations
from bitsharesbase.account import PublicKey

from .account import Account
from .amount import Amount
from .asset import Asset
from .committee import Committee
from .exceptions import AccountExistsException
from .instance import set_shared_blockchain_instance, shared_blockchain_instance
from .price import Price
from .storage import get_default_config_store
from .transactionbuilder import ProposalBuilder, TransactionBuilder
from .vesting import Vesting
from .wallet import Wallet
from .witness import Witness
from .worker import Worker


# from .utils import formatTime

log = logging.getLogger(__name__)


class BitShares(AbstractGrapheneChain):
    """ Connect to the BitShares network.

        :param str node: Node to connect to *(optional)*
        :param str rpcuser: RPC user *(optional)*
        :param str rpcpassword: RPC password *(optional)*
        :param bool nobroadcast: Do **not** broadcast a transaction!
            *(optional)*
        :param bool debug: Enable Debugging *(optional)*
        :param array,dict,string keys: Predefine the wif keys to shortcut the
            wallet database *(optional)*
        :param bool offline: Boolean to prevent connecting to network (defaults
            to ``False``) *(optional)*
        :param str proposer: Propose a transaction using this proposer
            *(optional)*
        :param int proposal_expiration: Expiration time (in seconds) for the
            proposal *(optional)*
        :param int proposal_review: Review period (in seconds) for the proposal
            *(optional)*
        :param int expiration: Delay in seconds until transactions are supposed
            to expire *(optional)*
        :param str blocking: Wait for broadcasted transactions to be included
            in a block and return full transaction (can be "head" or
            "irrversible")
        :param bool bundle: Do not broadcast transactions right away, but allow
            to bundle operations *(optional)*

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
        http://uptick.rocks. It is **highly** recommended that you
        pick your own node instead. Default settings can be changed with:

        .. code-block:: python

            uptick set node <host>

        where ``<host>`` starts with ``ws://`` or ``wss://``.

        The purpose of this class it to simplify interaction with
        BitShares.

        The idea is to have a class that allows to do this:

        .. code-block:: python

            from bitshares import BitShares
            bitshares = BitShares()
            print(bitshares.info())

        All that is requires is for the user to have added a key with
        ``uptick``

        .. code-block:: bash

            uptick addkey

        and setting a default author:

        .. code-block:: bash

            uptick set default_account xeroc

        This class also deals with edits, votes and reading content.
    """

    def define_classes(self):
        from .blockchainobject import BlockchainObject

        self.wallet_class = Wallet
        self.account_class = Account
        self.rpc_class = BitSharesNodeRPC
        self.default_key_store_app_name = "bitshares"
        self.proposalbuilder_class = ProposalBuilder
        self.transactionbuilder_class = TransactionBuilder
        self.blockchainobject_class = BlockchainObject

    # -------------------------------------------------------------------------
    # Simple Transfer
    # -------------------------------------------------------------------------
    def transfer(self, to, amount, asset, memo="", account=None, **kwargs):
        """ Transfer an asset to another account.

            :param str to: Recipient
            :param float amount: Amount to transfer
            :param str asset: Asset to transfer
            :param str memo: (optional) Memo, may begin with `#` for encrypted
                messaging
            :param str account: (optional) the source account for the transfer
                if not ``default_account``
        """
        from .memo import Memo

        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        account = Account(account, blockchain_instance=self)
        amount = Amount(amount, asset, blockchain_instance=self)
        to = Account(to, blockchain_instance=self)

        memoObj = Memo(from_account=account, to_account=to, blockchain_instance=self)

        op = operations.Transfer(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "from": account["id"],
                "to": to["id"],
                "amount": {"amount": int(amount), "asset_id": amount.asset["id"]},
                "memo": memoObj.encrypt(memo),
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account, "active", **kwargs)

    # -------------------------------------------------------------------------
    # Account related calls
    # -------------------------------------------------------------------------
    def create_account(
        self,
        account_name,
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
        proxy_account="proxy-to-self",
        storekeys=True,
        **kwargs
    ):
        """ Create new account on BitShares

            The brainkey/password can be used to recover all generated keys
            (see `bitsharesbase.account` for more details.

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
            :param array additional_owner_accounts: Additional owner account
                names
            :param array additional_active_accounts: Additional acctive account
                names
            :param bool storekeys: Store new keys in the wallet (default:
                ``True``)
            :raises AccountExistsException: if the account already exists on
                the blockchain

        """
        if not registrar and self.config["default_account"]:
            registrar = self.config["default_account"]
        if not registrar:
            raise ValueError(
                "Not registrar account given. Define it with "
                + "registrar=x, or set the default_account using uptick"
            )
        if password and (owner_key or active_key or memo_key):
            raise ValueError("You cannot use 'password' AND provide keys!")

        try:
            Account(account_name, blockchain_instance=self)
            raise AccountExistsException
        except Exception:
            pass

        referrer = Account(referrer, blockchain_instance=self)
        registrar = Account(registrar, blockchain_instance=self)

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
                # self.wallet.addPrivateKey(str(owner_privkey))
                self.wallet.addPrivateKey(str(active_privkey))
                self.wallet.addPrivateKey(str(memo_privkey))
        elif owner_key and active_key and memo_key:
            active_pubkey = PublicKey(active_key, prefix=self.prefix)
            owner_pubkey = PublicKey(owner_key, prefix=self.prefix)
            memo_pubkey = PublicKey(memo_key, prefix=self.prefix)
        else:
            raise ValueError(
                "Call incomplete! Provide either a password or public keys!"
            )
        owner = format(owner_pubkey, self.prefix)
        active = format(active_pubkey, self.prefix)
        memo = format(memo_pubkey, self.prefix)

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
            addaccount = Account(k, blockchain_instance=self)
            owner_accounts_authority.append([addaccount["id"], 1])
        for k in additional_active_accounts:
            addaccount = Account(k, blockchain_instance=self)
            active_accounts_authority.append([addaccount["id"], 1])

        # voting account
        voting_account = Account(
            proxy_account or "proxy-to-self", blockchain_instance=self
        )

        op = {
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "registrar": registrar["id"],
            "referrer": referrer["id"],
            "referrer_percent": referrer_percent * 100,
            "name": account_name,
            "owner": {
                "account_auths": owner_accounts_authority,
                "key_auths": owner_key_authority,
                "address_auths": [],
                "weight_threshold": 1,
            },
            "active": {
                "account_auths": active_accounts_authority,
                "key_auths": active_key_authority,
                "address_auths": [],
                "weight_threshold": 1,
            },
            "options": {
                "memo_key": memo,
                "voting_account": voting_account["id"],
                "num_witness": 0,
                "num_committee": 0,
                "votes": [],
                "extensions": [],
            },
            "extensions": {},
            "prefix": self.prefix,
        }
        op = operations.Account_create(**op)
        return self.finalizeOp(op, registrar, "active", **kwargs)

    def upgrade_account(self, account=None, **kwargs):
        """ Upgrade an account to Lifetime membership

            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        op = operations.Account_upgrade(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account_to_upgrade": account["id"],
                "upgrade_to_lifetime_member": True,
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def _test_weights_treshold(self, authority):
        """ This method raises an error if the threshold of an authority cannot
            be reached by the weights.

            :param dict authority: An authority of an account
            :raises ValueError: if the threshold is set too high
        """
        weights = 0
        for a in authority["account_auths"]:
            weights += int(a[1])
        for a in authority["key_auths"]:
            weights += int(a[1])
        if authority["weight_threshold"] > weights:
            raise ValueError("Threshold too restrictive!")
        if authority["weight_threshold"] == 0:
            raise ValueError("Cannot have threshold of 0")

    def allow(
        self,
        foreign,
        weight=None,
        permission="active",
        account=None,
        threshold=None,
        **kwargs
    ):
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
        from copy import deepcopy

        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        if permission not in ["owner", "active"]:
            raise ValueError("Permission needs to be either 'owner', or 'active")
        account = Account(account, blockchain_instance=self)

        if not weight:
            weight = account[permission]["weight_threshold"]

        authority = deepcopy(account[permission])
        try:
            pubkey = PublicKey(foreign, prefix=self.prefix)
            authority["key_auths"].append([str(pubkey), weight])
        except Exception:
            try:
                foreign_account = Account(foreign, blockchain_instance=self)
                authority["account_auths"].append([foreign_account["id"], weight])
            except Exception:
                raise ValueError("Unknown foreign account or invalid public key")
        if threshold:
            authority["weight_threshold"] = threshold
            self._test_weights_treshold(authority)

        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                permission: authority,
                "extensions": {},
                "prefix": self.prefix,
            }
        )
        if permission == "owner":
            return self.finalizeOp(op, account["name"], "owner", **kwargs)
        else:
            return self.finalizeOp(op, account["name"], "active", **kwargs)

    def disallow(
        self, foreign, permission="active", account=None, threshold=None, **kwargs
    ):
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
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        if permission not in ["owner", "active"]:
            raise ValueError("Permission needs to be either 'owner', or 'active")
        account = Account(account, blockchain_instance=self)
        authority = account[permission]

        try:
            pubkey = PublicKey(foreign, prefix=self.prefix)
            affected_items = list(
                filter(lambda x: x[0] == str(pubkey), authority["key_auths"])
            )
            authority["key_auths"] = list(
                filter(lambda x: x[0] != str(pubkey), authority["key_auths"])
            )
        except Exception:
            try:
                foreign_account = Account(foreign, blockchain_instance=self)
                affected_items = list(
                    filter(
                        lambda x: x[0] == foreign_account["id"],
                        authority["account_auths"],
                    )
                )
                authority["account_auths"] = list(
                    filter(
                        lambda x: x[0] != foreign_account["id"],
                        authority["account_auths"],
                    )
                )
            except Exception:
                raise ValueError("Unknown foreign account or unvalid public key")

        if not affected_items:
            raise ValueError("Changes nothing!")
        removed_weight = affected_items[0][1]

        # Define threshold
        if threshold:
            authority["weight_threshold"] = threshold

        # Correct threshold (at most by the amount removed from the
        # authority)
        try:
            self._test_weights_treshold(authority)
        except Exception:
            log.critical(
                "The account's threshold will be reduced by %d" % (removed_weight)
            )
            authority["weight_threshold"] -= removed_weight
            self._test_weights_treshold(authority)

        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                permission: authority,
                "extensions": {},
            }
        )
        if permission == "owner":
            return self.finalizeOp(op, account["name"], "owner", **kwargs)
        else:
            return self.finalizeOp(op, account["name"], "active", **kwargs)

    def update_memo_key(self, key, account=None, **kwargs):
        """ Update an account's memo public key

            This method does **not** add any private keys to your
            wallet but merely changes the memo public key.

            :param str key: New memo public key
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")

        PublicKey(key, prefix=self.prefix)

        account = Account(account, blockchain_instance=self)
        account["options"]["memo_key"] = key
        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                "new_options": account["options"],
                "extensions": {},
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    # -------------------------------------------------------------------------
    #  Approval and Disapproval of witnesses, workers, committee, and proposals
    # -------------------------------------------------------------------------
    def approvewitness(self, witnesses, account=None, **kwargs):
        """ Approve a witness

            :param list witnesses: list of Witness name or id
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        options = account["options"]

        if not isinstance(witnesses, (list, set, tuple)):
            witnesses = {witnesses}

        for witness in witnesses:
            witness = Witness(witness, blockchain_instance=self)
            options["votes"].append(witness["vote_id"])

        options["votes"] = list(set(options["votes"]))
        options["num_witness"] = len(
            list(filter(lambda x: float(x.split(":")[0]) == 1, options["votes"]))
        )
        options["voting_account"] = "1.2.5"  # Account("proxy-to-self")["id"]

        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                "new_options": options,
                "extensions": {},
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def disapprovewitness(self, witnesses, account=None, **kwargs):
        """ Disapprove a witness

            :param list witnesses: list of Witness name or id
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        options = account["options"]

        if not isinstance(witnesses, (list, set, tuple)):
            witnesses = {witnesses}

        for witness in witnesses:
            witness = Witness(witness, blockchain_instance=self)
            if witness["vote_id"] in options["votes"]:
                options["votes"].remove(witness["vote_id"])

        options["votes"] = list(set(options["votes"]))
        options["num_witness"] = len(
            list(filter(lambda x: float(x.split(":")[0]) == 1, options["votes"]))
        )
        options["voting_account"] = "1.2.5"  # Account("proxy-to-self")["id"]

        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                "new_options": options,
                "extensions": {},
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def approvecommittee(self, committees, account=None, **kwargs):
        """ Approve a committee

            :param list committees: list of committee member name or id
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        options = account["options"]

        if not isinstance(committees, (list, set, tuple)):
            committees = {committees}

        for committee in committees:
            committee = Committee(committee, blockchain_instance=self)
            options["votes"].append(committee["vote_id"])

        options["votes"] = list(set(options["votes"]))
        options["num_committee"] = len(
            list(filter(lambda x: float(x.split(":")[0]) == 0, options["votes"]))
        )
        options["voting_account"] = "1.2.5"  # Account("proxy-to-self")["id"]

        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                "new_options": options,
                "extensions": {},
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def disapprovecommittee(self, committees, account=None, **kwargs):
        """ Disapprove a committee

            :param list committees: list of committee name or id
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        options = account["options"]

        if not isinstance(committees, (list, set, tuple)):
            committees = {committees}

        for committee in committees:
            committee = Committee(committee, blockchain_instance=self)
            if committee["vote_id"] in options["votes"]:
                options["votes"].remove(committee["vote_id"])

        options["votes"] = list(set(options["votes"]))
        options["num_committee"] = len(
            list(filter(lambda x: float(x.split(":")[0]) == 0, options["votes"]))
        )
        options["voting_account"] = "1.2.5"  # Account("proxy-to-self")["id"]

        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                "new_options": options,
                "extensions": {},
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def approveproposal(self, proposal_ids, account=None, approver=None, **kwargs):
        """ Approve Proposal

            :param list proposal_id: Ids of the proposals
            :param str appprover: The account or key to use for approval
                (defaults to ``account``)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        from .proposal import Proposal

        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        is_key = approver and approver[:3] == self.prefix
        if not approver and not is_key:
            approver = account
        elif approver and not is_key:
            approver = Account(approver, blockchain_instance=self)
        else:
            approver = PublicKey(approver)

        if not isinstance(proposal_ids, (list, set, tuple)):
            proposal_ids = {proposal_ids}

        op = []
        for proposal_id in proposal_ids:
            proposal = Proposal(proposal_id, blockchain_instance=self)
            update_dict = {
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "fee_paying_account": account["id"],
                "proposal": proposal["id"],
                "prefix": self.prefix,
            }
            if is_key:
                update_dict.update({"key_approvals_to_add": [str(approver)]})
            else:
                update_dict.update({"active_approvals_to_add": [approver["id"]]})
            op.append(operations.Proposal_update(**update_dict))
        if is_key:
            self.txbuffer.appendSigner(approver, "active")
            return self.finalizeOp(op, account["name"], "active", **kwargs)
        return self.finalizeOp(op, approver, "active", **kwargs)

    def disapproveproposal(self, proposal_ids, account=None, approver=None, **kwargs):
        """ Disapprove Proposal

            :param list proposal_ids: Ids of the proposals
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        from .proposal import Proposal

        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        if not approver:
            approver = account
        else:
            approver = Account(approver, blockchain_instance=self)

        if not isinstance(proposal_ids, (list, set, tuple)):
            proposal_ids = {proposal_ids}

        op = []
        for proposal_id in proposal_ids:
            proposal = Proposal(proposal_id, blockchain_instance=self)
            op.append(
                operations.Proposal_update(
                    **{
                        "fee": {"amount": 0, "asset_id": "1.3.0"},
                        "fee_paying_account": account["id"],
                        "proposal": proposal["id"],
                        "active_approvals_to_remove": [approver["id"]],
                        "prefix": self.prefix,
                    }
                )
            )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def approveworker(self, workers, account=None, **kwargs):
        """ Approve a worker

            :param list workers: list of worker member name or id
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        options = account["options"]

        if not isinstance(workers, (list, set, tuple)):
            workers = {workers}

        for worker in workers:
            worker = Worker(worker, blockchain_instance=self)
            options["votes"].append(worker["vote_for"])
        options["votes"] = list(set(options["votes"]))
        options["voting_account"] = "1.2.5"  # Account("proxy-to-self")["id"]

        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                "new_options": options,
                "extensions": {},
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def disapproveworker(self, workers, account=None, **kwargs):
        """ Disapprove a worker

            :param list workers: list of worker name or id
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        options = account["options"]

        if not isinstance(workers, (list, set, tuple)):
            workers = {workers}

        for worker in workers:
            worker = Worker(worker, blockchain_instance=self)
            if worker["vote_for"] in options["votes"]:
                options["votes"].remove(worker["vote_for"])
        options["votes"] = list(set(options["votes"]))
        options["voting_account"] = "1.2.5"  # Account("proxy-to-self")["id"]

        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                "new_options": options,
                "extensions": {},
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def unset_proxy(self, account=None, **kwargs):
        """ Unset the proxy account to start voting yourself
        """
        return self.set_proxy("proxy-to-self", account=account, **kwargs)

    def set_proxy(self, proxy_account, account=None, **kwargs):
        """ Set a specific proxy for account

            :param bitshares.account.Account proxy_account: Account to be
                    proxied
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        proxy = Account(proxy_account, blockchain_instance=self)
        options = account["options"]
        options["voting_account"] = proxy["id"]

        op = operations.Account_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": account["id"],
                "new_options": options,
                "extensions": {},
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def cancel(self, orderNumbers, account=None, **kwargs):
        """ Cancels an order you have placed in a given market. Requires
            only the "orderNumbers". An order number takes the form
            ``1.7.xxx``.

            :param str orderNumbers: The Order Object ide of the form
                ``1.7.xxxx``
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, full=False, blockchain_instance=self)

        if not isinstance(orderNumbers, (list, set, tuple)):
            orderNumbers = {orderNumbers}

        op = []
        for order in orderNumbers:
            op.append(
                operations.Limit_order_cancel(
                    **{
                        "fee": {"amount": 0, "asset_id": "1.3.0"},
                        "fee_paying_account": account["id"],
                        "order": order,
                        "extensions": [],
                        "prefix": self.prefix,
                    }
                )
            )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def vesting_balance_withdraw(self, vesting_id, amount=None, account=None, **kwargs):
        """ Withdraw vesting balance

            :param str vesting_id: Id of the vesting object
            :param bitshares.amount.Amount Amount: to withdraw ("all" if not
                provided")
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)

        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)

        if not amount:
            obj = Vesting(vesting_id, blockchain_instance=self)
            amount = obj.claimable

        op = operations.Vesting_balance_withdraw(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "vesting_balance": vesting_id,
                "owner": account["id"],
                "amount": {"amount": int(amount), "asset_id": amount["asset"]["id"]},
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active")

    def publish_price_feed(
        self, symbol, settlement_price, cer=None, mssr=110, mcr=200, account=None
    ):
        """ Publish a price feed for a market-pegged asset

            :param str symbol: Symbol of the asset to publish feed for
            :param bitshares.price.Price settlement_price: Price for settlement
            :param bitshares.price.Price cer: Core exchange Rate (default
                ``settlement_price + 5%``)
            :param float mssr: Percentage for max short squeeze ratio (default:
                110%)
            :param float mcr: Percentage for maintenance collateral ratio
                (default: 200%)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)

            .. note:: The ``account`` needs to be allowed to produce a
                      price feed for ``symbol``. For witness produced
                      feeds this means ``account`` is a witness account!
        """
        assert mcr > 100
        assert mssr > 100
        assert isinstance(
            settlement_price, Price
        ), "settlement_price needs to be instance of `bitshares.price.Price`!"
        assert cer is None or isinstance(
            cer, Price
        ), "cer needs to be instance of `bitshares.price.Price`!"
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        asset = Asset(symbol, blockchain_instance=self, full=True)
        backing_asset = asset["bitasset_data"]["options"]["short_backing_asset"]
        assert (
            asset["id"] == settlement_price["base"]["asset"]["id"]
            or asset["id"] == settlement_price["quote"]["asset"]["id"]
        ), "Price needs to contain the asset of the symbol you'd like to produce a feed for!"
        assert asset.is_bitasset, "Symbol needs to be a bitasset!"
        assert (
            settlement_price["base"]["asset"]["id"] == backing_asset
            or settlement_price["quote"]["asset"]["id"] == backing_asset
        ), "The Price needs to be relative to the backing collateral!"

        settlement_price = settlement_price.as_base(symbol)

        if cer:
            cer = cer.as_base(symbol)
            if cer["quote"]["asset"]["id"] != "1.3.0":
                raise ValueError("CER must be defined against core asset '1.3.0'")
        else:
            if settlement_price["quote"]["asset"]["id"] != "1.3.0":
                raise ValueError(
                    "CER must be manually provided because it relates to core asset '1.3.0'"
                )
            cer = settlement_price.as_quote(symbol) * 0.95

        op = operations.Asset_publish_feed(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "publisher": account["id"],
                "asset_id": asset["id"],
                "feed": {
                    "settlement_price": settlement_price.as_base(symbol).json(),
                    "core_exchange_rate": cer.as_base(symbol).json(),
                    "maximum_short_squeeze_ratio": int(mssr * 10),
                    "maintenance_collateral_ratio": int(mcr * 10),
                },
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active")

    def update_cer(self, symbol, cer, account=None):
        """ Update the Core Exchange Rate (CER) of an asset

            :param str symbol: Symbol of the asset to publish feed for
            :param bitshares.price.Price cer: Core exchange Rate
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)

        """
        assert isinstance(
            cer, Price
        ), "cer needs to be instance of `bitshares.price.Price`!"
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        asset = Asset(symbol, blockchain_instance=self, full=True)
        assert (
            asset["id"] == cer["base"]["asset"]["id"]
            or asset["id"] == cer["quote"]["asset"]["id"]
        ), "Price needs to contain the asset of the symbol you'd like to produce a feed for!"

        cer = cer.as_base(symbol)
        if cer["quote"]["asset"]["id"] != "1.3.0":
            raise ValueError("CER must be defined against core asset '1.3.0'")

        options = asset["options"]
        options.update({"core_exchange_rate": cer.as_base(symbol).json()})
        op = operations.Asset_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": account["id"],
                "asset_to_update": asset["id"],
                "new_options": options,
                "extensions": [],
                "prefix": self.prefix,
            }
        )
        return self.finalizeOp(op, account["name"], "active")

    def update_witness(self, witness_identifier, url=None, key=None, **kwargs):
        """ Upgrade a witness account

            :param str witness_identifier: Identifier for the witness
            :param str url: New URL for the witness
            :param str key: Public Key for the signing
        """
        witness = Witness(witness_identifier)
        account = witness.account
        op = operations.Witness_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "prefix": self.prefix,
                "witness": witness["id"],
                "witness_account": account["id"],
                "new_url": url,
                "new_signing_key": key,
            }
        )
        return self.finalizeOp(op, account["name"], "active", **kwargs)

    def reserve(self, amount, account=None, **kwargs):
        """ Reserve/Burn an amount of this shares

            This removes the shares from the supply

            :param bitshares.amount.Amount amount: The amount to be burned.
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        assert isinstance(amount, Amount)
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        op = operations.Asset_reserve(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "payer": account["id"],
                "amount_to_reserve": {
                    "amount": int(amount),
                    "asset_id": amount["asset"]["id"],
                },
                "extensions": [],
            }
        )
        return self.finalizeOp(op, account, "active", **kwargs)

    def create_worker(
        self,
        name,
        daily_pay,
        end,
        url="",
        begin=None,
        payment_type="vesting",
        pay_vesting_period_days=0,
        account=None,
        **kwargs
    ):
        """ Create a worker

            This removes the shares from the supply

            **Required**

            :param str name: Name of the worke
            :param bitshares.amount.Amount daily_pay: The amount to be paid
                daily
            :param datetime end: Date/time of end of the worker

            **Optional**

            :param str url: URL to read more about the worker
            :param datetime begin: Date/time of begin of the worker
            :param string payment_type: ["burn", "refund", "vesting"] (default:
                "vesting")
            :param int pay_vesting_period_days: Days of vesting (default: 0)
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        from bitsharesbase.transactions import timeformat

        assert isinstance(daily_pay, Amount)
        assert daily_pay["asset"]["id"] == "1.3.0"
        if not begin:
            begin = datetime.utcnow() + timedelta(seconds=30)
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)

        if payment_type == "refund":
            initializer = [0, {}]
        elif payment_type == "vesting":
            initializer = [1, {"pay_vesting_period_days": pay_vesting_period_days}]
        elif payment_type == "burn":
            initializer = [2, {}]
        else:
            raise ValueError('payment_type not in ["burn", "refund", "vesting"]')

        op = operations.Worker_create(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "owner": account["id"],
                "work_begin_date": begin.strftime(timeformat),
                "work_end_date": end.strftime(timeformat),
                "daily_pay": int(daily_pay),
                "name": name,
                "url": url,
                "initializer": initializer,
            }
        )
        return self.finalizeOp(op, account, "active", **kwargs)

    def fund_fee_pool(self, symbol, amount, account=None, **kwargs):
        """ Fund the fee pool of an asset

            :param str symbol: The symbol to fund the fee pool of
            :param float amount: The amount to be burned.
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        assert isinstance(amount, float)
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        amount = Amount(amount, "1.3.0", blockchain_instance=self)
        account = Account(account, blockchain_instance=self)
        asset = Asset(symbol, blockchain_instance=self)
        op = operations.Asset_fund_fee_pool(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "from_account": account["id"],
                "asset_id": asset["id"],
                "amount": int(amount),
                "extensions": [],
            }
        )
        return self.finalizeOp(op, account, "active", **kwargs)

    def create_committee_member(self, url="", account=None, **kwargs):
        """ Create a committee member

            :param str url: URL to read more about the worker
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)

        op = operations.Committee_member_create(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "committee_member_account": account["id"],
                "url": url,
            }
        )
        return self.finalizeOp(op, account, "active", **kwargs)

    def account_whitelist(
        self,
        account_to_whitelist,
        lists=["white"],  # set of 'white' and/or 'black'
        account=None,
        **kwargs
    ):
        """ Account whitelisting

            :param str account_to_whitelist: The account we want to add
                to either the white- or the blacklist
            :param set lists: (defaults to ``('white')``). Lists the
                user should be added to. Either empty set, 'black',
                'white' or both.
            :param str account: (optional) the account to allow access
                to (defaults to ``default_account``)
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)
        account_to_list = Account(account_to_whitelist, blockchain_instance=self)

        if not isinstance(lists, (set, list)):
            raise ValueError('"lists" must be of instance list()')

        new_listing = operations.Account_whitelist.no_listing
        if "white" in lists:
            new_listing += operations.Account_whitelist.white_listed
        if "black" in lists:
            new_listing += operations.Account_whitelist.black_listed

        op = operations.Account_whitelist(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "authorizing_account": account["id"],
                "account_to_list": account_to_list["id"],
                "new_listing": new_listing,
            }
        )
        return self.finalizeOp(op, account, "active", **kwargs)

    def bid_collateral(
        self, additional_collateral, debt_covered, account=None, **kwargs
    ):
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, blockchain_instance=self)

        if not isinstance(additional_collateral, (Amount)):
            raise ValueError("additional_collateral must be of type Amount")

        if not isinstance(debt_covered, (Amount)):
            raise ValueError("debt_covered must be of type Amount")

        op = operations.Bid_collateral(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "bidder": account["id"],
                "additional_collateral": additional_collateral.json(),
                "debt_covered": debt_covered.json(),
                "extensions": [],
            }
        )
        return self.finalizeOp(op, account, "active", **kwargs)
