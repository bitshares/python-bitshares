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
from . import bitshares as bts
import logging
log = logging.getLogger(__name__)


class TransactionBuilder(dict):

    def __init__(self, tx={}, bitshares_instance=None):
        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance

        self.op = []
        self.wifs = []
        if not isinstance(tx, dict):
            raise ValueError("Invalid TransactionBuilder Format")
        super(TransactionBuilder, self).__init__(tx)

    def appendOps(self, ops):
        if isinstance(ops, list):
            for op in ops:
                self.op.append(op)
        else:
            self.op.append(ops)
        self.constructTx()

    def appendSigner(self, account, permission):
        account = Account(account, bitshares_instance=self.bitshares)
        if permission == "active":
            wif = self.bitshares.wallet.getActiveKeyForAccount(account["name"])
        elif permission == "owner":
            wif = self.bitshares.wallet.getOwnerKeyForAccount(account["name"])
        else:
            raise ValueError("Invalid permission")
        self.wifs.append(wif)

    def appendWif(self, wif):
        if wif:
            try:
                PrivateKey(wif)
                self.wifs.append(wif)
            except:
                raise InvalidWifError

    def constructTx(self):
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
        try:
            signedtx = Signed_Transaction(**self.json())
        except:
            raise ValueError("Invalid TransactionBuilder Format")

        if not any(self.wifs):
            raise MissingKeyError

        signedtx.sign(self.wifs, chain=self.bitshares.rpc.chain_params)
        self["signatures"].extend(signedtx.json().get("signatures"))

    def broadcast(self):
        """ Broadcast a transaction to the BitShares network

            :param tx tx: Signed transaction to broadcast
        """
        if self.bitshares.nobroadcast:
            log.warning("Not broadcasting anything!")
            return self

        try:
            if not self.bitshares.rpc.verify_authority(self.json()):
                raise InsufficientAuthorityError
        except Exception as e:
            raise e

        try:
            self.bitshares.rpc.broadcast_transaction(self.json(), api="network_broadcast")
        except Exception as e:
            raise e

        return self

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

    def json(self):
        return dict(self)

    def appendMissingSignatures(self, wifs=[]):
        missing_signatures = self.get("missing_signatures", [])
        for pub in missing_signatures:
            wif = self.bitshares.wallet.getPrivateKeyForPublicKey(pub)
            if wif:
                self.appendWif(wif)
