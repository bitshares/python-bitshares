from .account import Account
from bitsharesbase.objects import Operation
from bitsharesbase.account import PrivateKey, PublicKey
from bitsharesbase.signedtransactions import Signed_Transaction
from bitsharesbase import transactions, operations
from .exceptions import (
    InsufficientAuthorityError,
    MissingKeyError,
    InvalidWifError,
    WalletLocked
)
from bitshares.instance import shared_bitshares_instance
import logging
log = logging.getLogger(__name__)


class ProposalBuilder:
    """ Proposal Builder allows us to construct an independent Proposal
        that may later be added to an instance ot TransactionBuilder

        :param str proposer: Account name of the proposing user
        :param int proposal_expiration: Number seconds until the proposal is
            supposed to expire
        :param int proposal_review: Number of seconds for review of the
            proposal
        :param bitshares.transactionbuilder.TransactionBuilder: Specify
            your own instance of transaction builder (optional)
        :param bitshares.bitshares.BitShares bitshares_instance: BitShares
            instance
    """
    def __init__(
        self,
        proposer,
        proposal_expiration=None,
        proposal_review=None,
        parent=None,
        bitshares_instance=None,
        *args,
        **kwargs
    ):
        self.bitshares = bitshares_instance or shared_bitshares_instance()

        self.set_expiration(proposal_expiration or 2 * 24 * 60 * 60)
        self.set_review(proposal_review)
        self.set_parent(parent)
        self.set_proposer(proposer)
        self.ops = list()

    def is_empty(self):
        return not (len(self.ops) > 0)

    def set_proposer(self, p):
        self.proposer = p

    def set_expiration(self, p):
        self.proposal_expiration = p

    def set_review(self, p):
        self.proposal_review = p

    def set_parent(self, p):
        self.parent = p

    def appendOps(self, ops, append_to=None):
        """ Append op(s) to the transaction builder

            :param list ops: One or a list of operations
        """
        if isinstance(ops, list):
            self.ops.extend(ops)
        else:
            self.ops.append(ops)
        parent = self.parent
        if parent:
            parent._set_require_reconstruction()

    def list_operations(self):
        return [Operation(o) for o in self.ops]

    def broadcast(self):
        assert self.parent, "No parent transaction provided!"
        self.parent._set_require_reconstruction()
        return self.parent.broadcast()

    def get_parent(self):
        """ This allows to referr to the actual parent of the Proposal
        """
        return self.parent

    def __repr__(self):
        return "<Proposal ops=%s>" % str(self.ops)

    def json(self):
        """ Return the json formated version of this proposal
        """
        raw = self.get_raw()
        if not raw:
            return dict()
        return raw.json()

    def get_raw(self):
        """ Returns an instance of base "Operations" for further processing
        """
        if not self.ops:
            return
        ops = [operations.Op_wrapper(op=o) for o in list(self.ops)]
        proposer = Account(
            self.proposer,
            bitshares_instance=self.bitshares
        )
        data = {
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "fee_paying_account": proposer["id"],
            "expiration_time": transactions.formatTimeFromNow(
                self.proposal_expiration),
            "proposed_ops": [o.json() for o in ops],
            "extensions": []
        }
        if self.proposal_review:
            data.update({
                "review_period_seconds": self.proposal_review
            })
        ops = operations.Proposal_create(**data)
        return Operation(ops)


class TransactionBuilder(dict):
    """ This class simplifies the creation of transactions by adding
        operations and signers.
    """
    def __init__(
        self,
        tx={},
        proposer=None,
        expiration=None,
        bitshares_instance=None
    ):
        self.bitshares = bitshares_instance or shared_bitshares_instance()
        self.clear()
        if tx and isinstance(tx, dict):
            super(TransactionBuilder, self).__init__(tx)
            # Load operations
            self.ops = tx["operations"]
            self._require_reconstruction = False
        else:
            self._require_reconstruction = True
        self.set_expiration(expiration)

    def set_expiration(self, p):
        self.expiration = p

    def is_empty(self):
        return not (len(self.ops) > 0)

    def list_operations(self):
        return [Operation(o) for o in self.ops]

    def _is_signed(self):
        return "signatures" in self and self["signatures"]

    def _is_constructed(self):
        return "expiration" in self and self["expiration"]

    def _is_require_reconstruction(self):
        return self._require_reconstruction

    def _set_require_reconstruction(self):
        self._require_reconstruction = True

    def _unset_require_reconstruction(self):
        self._require_reconstruction = False

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.json())

    def __getitem__(self, key):
        if key not in self:
            self.constructTx()
        return dict(self).__getitem__(key)

    def get_parent(self):
        """ TransactionBuilders don't have parents, they are their own parent
        """
        return self

    def json(self):
        """ Show the transaction as plain json
        """
        if not self._is_constructed() or self._is_require_reconstruction():
            self.constructTx()
        return dict(self)

    def appendOps(self, ops, append_to=None):
        """ Append op(s) to the transaction builder

            :param list ops: One or a list of operations
        """
        if isinstance(ops, list):
            self.ops.extend(ops)
        else:
            self.ops.append(ops)
        self._set_require_reconstruction()

    def appendSigner(self, account, permission):
        """ Try to obtain the wif key from the wallet by telling which account
            and permission is supposed to sign the transaction
        """
        assert permission in ["active", "owner"], "Invalid permission"
        account = Account(account, bitshares_instance=self.bitshares)
        required_treshold = account[permission]["weight_threshold"]

        if self.bitshares.wallet.locked():
            raise WalletLocked()

        def fetchkeys(account, perm, level=0):
            if level > 2:
                return []
            r = []
            for authority in account[perm]["key_auths"]:
                try:
                    wif = self.bitshares.wallet.getPrivateKeyForPublicKey(
                        authority[0])
                    r.append([wif, authority[1]])
                except Exception:
                    pass

            if sum([x[1] for x in r]) < required_treshold:
                # go one level deeper
                for authority in account[perm]["account_auths"]:
                    auth_account = Account(
                        authority[0], bitshares_instance=self.bitshares)
                    r.extend(fetchkeys(auth_account, perm, level + 1))

            return r

        if account not in self.signing_accounts:
            # is the account an instance of public key?
            if isinstance(account, PublicKey):
                self.wifs.add(
                    self.bitshares.wallet.getPrivateKeyForPublicKey(
                        str(account)
                    )
                )
            else:
                account = Account(account, bitshares_instance=self.bitshares)
                required_treshold = account[permission]["weight_threshold"]
                keys = fetchkeys(account, permission)
                if permission != "owner":
                    keys.extend(fetchkeys(account, "owner"))
                for x in keys:
                    self.wifs.add(x[0])

            self.signing_accounts.append(account)

    def appendWif(self, wif):
        """ Add a wif that should be used for signing of the transaction.
        """
        if wif:
            try:
                PrivateKey(wif)
                self.wifs.add(wif)
            except:
                raise InvalidWifError

    def constructTx(self):
        """ Construct the actual transaction and store it in the class's dict
            store
        """
        ops = list()
        for op in self.ops:
            if isinstance(op, ProposalBuilder):
                # This operation is a proposal an needs to be deal with
                # differently
                proposals = op.get_raw()
                if proposals:
                    ops.append(proposals)
            else:
                # otherwise, we simply wrap ops into Operations
                ops.extend([Operation(op)])

        # We no wrap everything into an actual transaction
        ops = transactions.addRequiredFees(self.bitshares.rpc, ops)
        expiration = transactions.formatTimeFromNow(
            self.expiration or self.bitshares.expiration
        )
        ref_block_num, ref_block_prefix = transactions.getBlockParams(
            self.bitshares.rpc)
        self.tx = Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops
        )
        super(TransactionBuilder, self).update(self.tx.json())
        self._unset_require_reconstruction()

    def sign(self):
        """ Sign a provided transaction witht he provided key(s)

            :param dict tx: The transaction to be signed and returned
            :param string wifs: One or many wif keys to use for signing
                a transaction. If not present, the keys will be loaded
                from the wallet as defined in "missing_signatures" key
                of the transactions.
        """
        self.constructTx()

        if "operations" not in self or not self["operations"]:
            return

        # Legacy compatibility!
        # If we are doing a proposal, obtain the account from the proposer_id
        if self.bitshares.proposer:
            proposer = Account(
                self.bitshares.proposer,
                bitshares_instance=self.bitshares)
            self.wifs = set()
            self.signing_accounts = list()
            self.appendSigner(proposer["id"], "active")

        # We need to set the default prefix, otherwise pubkeys are
        # presented wrongly!
        if self.bitshares.rpc:
            operations.default_prefix = (
                self.bitshares.rpc.chain_params["prefix"])
        elif "blockchain" in self:
            operations.default_prefix = self["blockchain"]["prefix"]

        try:
            signedtx = Signed_Transaction(**self.json())
        except:
            raise ValueError("Invalid TransactionBuilder Format")

        if not any(self.wifs):
            raise MissingKeyError

        signedtx.sign(self.wifs, chain=self.bitshares.rpc.chain_params)
        self["signatures"].extend(signedtx.json().get("signatures"))

    def verify_authority(self):
        """ Verify the authority of the signed transaction
        """
        try:
            if not self.bitshares.rpc.verify_authority(self.json()):
                raise InsufficientAuthorityError
        except Exception as e:
            raise e

    def broadcast(self):
        """ Broadcast a transaction to the bitshares network

            :param tx tx: Signed transaction to broadcast
        """
        # Cannot broadcast an empty transaction
        if not self._is_signed():
            self.sign()

        if "operations" not in self or not self["operations"]:
            return

        ret = self.json()

        if self.bitshares.nobroadcast:
            log.warning("Not broadcasting anything!")
            self.clear()
            return ret

        # Broadcast
        try:
            if self.bitshares.blocking:
                ret = self.bitshares.rpc.broadcast_transaction_synchronous(
                    ret, api="network_broadcast")
                ret.update(**ret["trx"])
            else:
                self.bitshares.rpc.broadcast_transaction(
                    ret, api="network_broadcast")
        except Exception as e:
            raise e

        self.clear()
        return ret

    def clear(self):
        """ Clear the transaction builder and start from scratch
        """
        self.ops = []
        self.wifs = set()
        self.signing_accounts = []
        # This makes sure that _is_constructed will return False afterwards
        self["expiration"] = None
        super(TransactionBuilder, self).__init__({})

    def addSigningInformation(self, account, permission):
        """ This is a private method that adds side information to a
            unsigned/partial transaction in order to simplify later
            signing (e.g. for multisig or coldstorage)

            FIXME: Does not work with owner keys!
        """
        self.constructTx()
        self["blockchain"] = self.bitshares.rpc.chain_params

        if isinstance(account, PublicKey):
            self["missing_signatures"] = [
                str(account)
            ]
        else:
            accountObj = Account(account)
            authority = accountObj[permission]
            # We add a required_authorities to be able to identify
            # how to sign later. This is an array, because we
            # may later want to allow multiple operations per tx
            self.update({"required_authorities": {
                accountObj["name"]: authority
            }})
            for account_auth in authority["account_auths"]:
                account_auth_account = Account(account_auth[0])
                self["required_authorities"].update({
                    account_auth[0]: account_auth_account.get(permission)
                })

            # Try to resolve required signatures for offline signing
            self["missing_signatures"] = [
                x[0] for x in authority["key_auths"]
            ]
            # Add one recursion of keys from account_auths:
            for account_auth in authority["account_auths"]:
                account_auth_account = Account(account_auth[0])
                self["missing_signatures"].extend(
                    [x[0] for x in account_auth_account[permission]["key_auths"]]
                )

    def appendMissingSignatures(self):
        """ Store which accounts/keys are supposed to sign the transaction

            This method is used for an offline-signer!
        """
        missing_signatures = self.get("missing_signatures", [])
        for pub in missing_signatures:
            wif = self.bitshares.wallet.getPrivateKeyForPublicKey(pub)
            if wif:
                self.appendWif(wif)
