from .account import Account
from bitsharesbase.objects import Operation
from bitsharesbase.account import PrivateKey, PublicKey
from bitsharesbase.signedtransactions import Signed_Transaction
from bitsharesbase import transactions, operations
from .exceptions import (
    InsufficientAuthorityError,
    MissingKeyError,
)
from . import bitshares as bts
import logging
log = logging.getLogger(__name__)


class Transaction(object):
    def __init__(self, bitshares_instance=None):
        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance

        self.op = []
        self.wifs = []

    def appendOps(self, ops):
        if isinstance(ops, list):
            for op in ops:
                self.op.append(op)
        else:
            self.op.append(ops)

    def appendSigner(self, account, permission):
        account = Account(account, bitshares_instance=self.bitshares)
        if permission == "active":
            wif = self.bitshares.wallet.getActiveKeyForAccount(account["name"])
        elif permission == "owner":
            wif = self.bitshares.wallet.getOwnerKeyForAccount(account["name"])
        else:
            raise ValueError("Invalid permission")
        self.wifs.append(wif)

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
        self.tx = tx.json()

    def sign(self):
        """ Sign a provided transaction witht he provided key(s)

            :param dict tx: The transaction to be signed and returned
            :param string wifs: One or many wif keys to use for signing
                a transaction. If not present, the keys will be loaded
                from the wallet as defined in "missing_signatures" key
                of the transactions.
        """
        try:
            signedtx = Signed_Transaction(**self.tx)
        except:
            raise ValueError("Invalid Transaction Format")

        signedtx.sign(self.wifs)
        self.tx["signatures"].extend(signedtx.json().get("signatures"))

    def broadcast(self):
        """ Broadcast a transaction to the BitShares network

            :param tx tx: Signed transaction to broadcast
        """
        if self.bitshares.nobroadcast:
            log.warning("Not broadcasting anything!")
            return self.tx

        try:
            if not self.bitshares.rpc.verify_authority(self.tx):
                raise InsufficientAuthorityError
        except Exception as e:
            raise e

        try:
            self.bitshares.rpc.broadcast_transaction(self.tx, api="network_broadcast")
        except Exception as e:
            raise e

        return self.tx
