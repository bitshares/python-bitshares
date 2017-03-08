from .account import Account
from bitsharesbase.objects import Operation
from bitsharesbase.account import PrivateKey, PublicKey
from bitsharesbase.signedtransactions import Signed_Transaction
from bitsharesbase import transactions, operations
from .exceptions import (
    InsufficientAuthorityError,
    MissingKeyError,
    InvalidWifError
)
from bitshares.instance import shared_bitshares_instance
import logging
log = logging.getLogger(__name__)


class TransactionBuilder(dict):
    """ This class simplifies the creation of transactions by adding
        operations and signers.
    """

    def __init__(self, tx={}, bitshares_instance=None):
        self.bitshares = bitshares_instance or shared_bitshares_instance()
        self.clear()
        if not isinstance(tx, dict):
            raise ValueError("Invalid TransactionBuilder Format")
        super(TransactionBuilder, self).__init__(tx)

    def appendOps(self, ops):
        """ Append op(s) to the transaction builder

            :param list ops: One or a list of operations
        """
        if isinstance(ops, list):
            for op in ops:
                self.op.append(op)
        else:
            self.op.append(ops)

    def appendSigner(self, account, permission):
        """ Try to obtain the wif key from the wallet by telling which account
            and permission is supposed to sign the transaction
        """
        assert permission in ["active", "owner"], "Invalid permission"
        account = Account(account, bitshares_instance=self.bitshares)
        required_treshold = account[permission]["weight_threshold"]

        def fetchkeys(account, level=0):
            if level > 2:
                return []
            r = []
            for authority in account[permission]["key_auths"]:
                r.append([
                    self.bitshares.wallet.getPrivateKeyForPublicKey(authority[0]),
                    authority[1]  # weight
                ])

            if sum([x[1] for x in r]) < required_treshold:
                # go one level deeper
                for authority in account[permission]["account_auths"]:
                    auth_account = Account(authority[0], bitshares_instance=self.bitshares)
                    r.extend(fetchkeys(auth_account, level + 1))

            return r
        keys = fetchkeys(account)
        self.wifs.extend([x[0] for x in keys])

    def appendWif(self, wif):
        """ Add a wif that should be used for signing of the transaction.
        """ 
        if wif:
            try:
                PrivateKey(wif)
                self.wifs.append(wif)
            except:
                raise InvalidWifError

    def constructTx(self):
        """ Construct the actual transaction and store it in the class's dict
            store
        """
        if isinstance(self.op, list):
            ops = [Operation(o) for o in self.op]
        else:
            ops = [Operation(self.op)]
        ops = transactions.addRequiredFees(self.bitshares.rpc, ops)
        expiration = transactions.formatTimeFromNow(self.bitshares.expiration)
        ref_block_num, ref_block_prefix = transactions.getBlockParams(self.bitshares.rpc)
        tx = Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops
        )
        super(TransactionBuilder, self).__init__(tx.json())

    def sign(self):
        """ Sign a provided transaction witht he provided key(s)

            :param dict tx: The transaction to be signed and returned
            :param string wifs: One or many wif keys to use for signing
                a transaction. If not present, the keys will be loaded
                from the wallet as defined in "missing_signatures" key
                of the transactions.
        """
        self.constructTx()

        # We need to set the default prefix, otherwise pubkeys are
        # presented wrongly!
        if self.bitshares.rpc:
            operations.default_prefix = self.bitshares.rpc.chain_params["prefix"]
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
        """ Broadcast a transaction to the BitShares network

            :param tx tx: Signed transaction to broadcast
        """
        self.sign()

        if self.bitshares.nobroadcast:
            log.warning("Not broadcasting anything!")
            return self

        # Broadcast
        try:
            self.bitshares.rpc.broadcast_transaction(self.json(), api="network_broadcast")
        except Exception as e:
            raise e

        return self

    def clear(self):
        """ Clear the transaction builder and start from scratch
        """
        self.op = []
        self.wifs = []

    def addSigningInformation(self, account, permission):
        """ This is a private method that adds side information to a
            unsigned/partial transaction in order to simplify later
            signing (e.g. for multisig or coldstorage)
        """
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
        self["blockchain"] = self.bitshares.rpc.chain_params

    def json(self):
        """ Show the transaction as plain json
        """
        return dict(self)

    def appendMissingSignatures(self, wifs=[]):
        """ Store which accounts/keys are supposed to sign the transaction

            This method is used for an offline-signer!
        """
        missing_signatures = self.get("missing_signatures", [])
        for pub in missing_signatures:
            wif = self.bitshares.wallet.getPrivateKeyForPublicKey(pub)
            if wif:
                self.appendWif(wif)
