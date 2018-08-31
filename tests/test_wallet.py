import unittest
from bitshares import storage
from bitshares.wallet import Wallet
from bitshares.exceptions import KeyNotFound
from bitsharesbase.account import PrivateKey
from .fixtures import fixture_data


class Testcases(unittest.TestCase):

    def setUp(self):
        fixture_data()

    def test_init(self):
        config = storage.InRamConfigurationStore()
        key_store = storage.InRamPlainKeyStore(config=config)
        wallet = Wallet(key_store=key_store)
        # InRamStore does not come with a default key
        self.assertFalse(wallet.created())

        self.assertTrue(bool(wallet.rpc))
        self.assertEqual(wallet.prefix, "BTS")
        wif1 = PrivateKey()
        wif2 = PrivateKey()
        wallet.setKeys([
            wif1, wif2
        ])
        self.assertIn(
            str(wif1.pubkey),
            wallet.store.getPublicKeys()
        )
        self.assertIn(
            str(wif2.pubkey),
            wallet.store.getPublicKeys()
        )
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
        # wallet.unlock("")
        # wallet.lock()
        # is unlocked because InRamKeyStore and not encrypted
        self.assertFalse(wallet.store.is_encrypted())
        self.assertFalse(wallet.is_encrypted())
        self.assertTrue(wallet.unlocked())
        self.assertFalse(wallet.locked())

        wif3 = PrivateKey()
        wallet.addPrivateKey(wif3)
        self.assertIn(
            str(wif3.pubkey),
            wallet.store.getPublicKeys()
        )
        self.assertEqual(
            wallet.getPrivateKeyForPublicKey(
                wif3.pubkey
            ),
            str(wif3)
        )

        wallet.removePrivateKeyFromPublicKey(wif3.pubkey)
        with self.assertRaises(KeyNotFound):
            wallet.getPrivateKeyForPublicKey(
                wif3.pubkey
            )
