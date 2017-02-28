from bitshares.instance import shared_bitshares_instance
import random
from bitsharesbase import memo as BtsMemo
from bitsharesbase.account import PrivateKey, PublicKey
from .account import Account
from .exceptions import MissingKeyError


class Memo(object):
    def __init__(self, from_account, to_account, memo, bitshares_instance=None):

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        memo_wif = self.bitshares.wallet.getPrivateKeyForPublicKey(
            from_account["options"]["memo_key"]
        )
        if not memo_wif:
            raise MissingKeyError("Memo key for %s missing!" % from_account)

        self.to_account = Account(to_account, bitshares_instance=self.bitshares)
        self.from_account = Account(from_account, bitshares_instance=self.bitshares)
        self.plain_memo = memo

        nonce = str(random.getrandbits(64))
        self.encrytped_memo = BtsMemo.encode_memo(
            PrivateKey(memo_wif),
            PublicKey(self.from_account["options"]["memo_key"]),
            nonce,
            memo
        )
