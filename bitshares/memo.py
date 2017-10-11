from bitshares.instance import shared_bitshares_instance
import random
from bitsharesbase import memo as BtsMemo
from bitsharesbase.account import PrivateKey, PublicKey
from .account import Account
from .exceptions import MissingKeyError


class Memo(object):
    """ Deals with Memos that are attached to a transfer

        :param bitshares.account.Account from_account: Account that has sent the memo
        :param bitshares.account.Account to_account: Account that has received the memo
        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance

        A memo is encrypted with a shared secret derived from a private key of
        the sender and a public key of the receiver. Due to the underlying
        mathematics, the same shared secret can be derived by the private key
        of the receiver and the public key of the sender. The encrypted message
        is perturbed by a nonce that is part of the transmitted message.

        .. code-block:: python

            from bitshares.memo import Memo
            m = Memo("bitshareseu", "wallet.xeroc")
            enc = (m.encrypt("foobar"))
            print(enc)
            >> {'nonce': '17329630356955254641', 'message': '8563e2bb2976e0217806d642901a2855'}
            print(m.decrypt(enc))
            >> foobar

    """
    def __init__(
        self,
        from_account,
        to_account,
        bitshares_instance=None
    ):

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        self.to_account = Account(to_account, bitshares_instance=self.bitshares)
        self.from_account = Account(from_account, bitshares_instance=self.bitshares)

    def encrypt(self, memo):
        """ Encrypt a memo

            :param str memo: clear text memo message
            :returns: encrypted memo
            :rtype: str
        """
        if not memo:
            return None

        nonce = str(random.getrandbits(64))
        memo_wif = self.bitshares.wallet.getPrivateKeyForPublicKey(
            self.from_account["options"]["memo_key"]
        )
        if not memo_wif:
            raise MissingKeyError("Memo key for %s missing!" % self.from_account["name"])

        enc = BtsMemo.encode_memo(
            PrivateKey(memo_wif),
            PublicKey(
                self.to_account["options"]["memo_key"],
                prefix=self.bitshares.rpc.chain_params["prefix"]
            ),
            nonce,
            memo
        )

        return {
            "message": enc,
            "nonce": nonce,
            "from": self.from_account["options"]["memo_key"],
            "to": self.to_account["options"]["memo_key"]
        }

    def decrypt(self, memo):
        """ Decrypt a memo

            :param str memo: encrypted memo message
            :returns: encrypted memo
            :rtype: str
        """
        if not memo:
            return None

        memo_wif = self.bitshares.wallet.getPrivateKeyForPublicKey(
            self.to_account["options"]["memo_key"]
        )
        if not memo_wif:
            raise MissingKeyError("Memo key for %s missing!" % self.to_account["name"])

        # TODO: Use pubkeys of the message, not pubkeys of account!
        return BtsMemo.decode_memo(
            PrivateKey(memo_wif),
            PublicKey(
                self.from_account["options"]["memo_key"],
                prefix=self.bitshares.rpc.chain_params["prefix"]
            ),
            memo.get("nonce"),
            memo.get("message")
        )
