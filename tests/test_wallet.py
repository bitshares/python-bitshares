import unittest
from pprint import pprint
from bitshares import BitShares
from bitshares.wallet import Wallet
from bitshares import storage
from bitsharesbase.account import PrivateKey

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


"""
bitshares = BitShares(
    nobroadcast=True,
    wif=[wif]
)
bitshares.set_default_account("init0")
set_shared_bitshares_instance(bitshares)
"""


class Testcases(unittest.TestCase):

    def test_init(self):
        config = storage.InRamConfigurationStore()
        key_store = storage.InRamPlainKeyStore(config=config)
        wallet = Wallet(key_store=key_store)
        # InRamStore comes with a default key
        self.assertTrue(wallet.created())

        self.assertTrue(bool(wallet.rpc))
        self.assertEqual(wallet.prefix, "BTS")
        wif1 = PrivateKey()
        wif2 = PrivateKey()
        wallet.setKeys([
            wif1, wif2
        ])
        self.assertEqual(
            wallet.getPrivateKeyForPublicKey(
                wif1.pubkey
            ),
            str(wif1)
        )
        self.assertEqual(
            wallet.getPrivateKeyForPublicKey(
                wif2.pubkey
            ),
            str(wif2)
        )
        wallet.unlock("")
        wallet.lock()
        # is unlocked because InRamKeyStore and not encrypted
        self.assertTrue(wallet.unlocked())
        self.assertFalse(wallet.locked())

        wif3 = PrivateKey()
        wallet.addPrivateKey(wif3)
        self.assertEqual(
            wallet.getPrivateKeyForPublicKey(
                wif3.pubkey
            ),
            str(wif3)
        )

        wallet.removePrivateKeyFromPublicKey(wif3.pubkey)
        self.assertFalse(
            bool(wallet.getPrivateKeyForPublicKey(
                wif3.pubkey
            ))
        )
