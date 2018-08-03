import unittest
from pprint import pprint
from bitshares import storage
from bitsharesbase.account import PrivateKey


def pubprivpair(wif):
    return(
        str(wif),
        str(PrivateKey(wif).pubkey)
    )


class Testcases(unittest.TestCase):

    def test_configstorage(self):
        for config in [
            storage.base.BaseStore(),
            storage.base.DefaultConfigurationStore(),
            storage.sqlite.DefaultSqliteConfigurationStore(),
        ]:
            config["node"] = "example"
            config["foobar"] = "action"
            self.assertIn("foobar", config)
            self.assertEqual(config["foobar"], "action")

            self.assertTrue(len(list(iter(config))) >= 1)
            self.assertTrue(len(list(config.items())) >= 1)

            self.assertEqual(config.get("non-exist", "bana"), "bana")

            config.delete("foobar")
            config["empty"] = "notempty"
            self.assertNotIn("foobar", config)
            config.wipe()
            self.assertNotIn("empty", config)

    def test_keystore(self):
        password = "foobar"
        for keys in [
            storage.base.InRamKeyStore(),
            storage.base.DefaultEncryptedKeyStore(storage=storage.base.BaseStore()),
            storage.sqlite.DefaultSqliteKeyStore(profile="testing")
        ]:

            if isinstance(keys, storage.base.DefaultEncryptedKeyStore):
                keys.newMaster(password)
                assert keys.unlocked()

            keys.add(
                *pubprivpair("5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3")
            )
            # Duplicate key
            keys.add(
                *pubprivpair("5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3")
            )
            self.assertIn(
                "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                keys.getPublicKeys()
            )

            self.assertEqual(
                keys.getPrivateKeyForPublicKey(
                    "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"
                ),
                "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
            )

            self.assertEqual(len(keys.getPublicKeys()), 1)
            keys.add(
                *pubprivpair("5Hqr1Rx6v3MLAvaYCxLYqaSEsm4eHaDFkLksPF2e1sDS7omneaZ")
            )
            self.assertEqual(len(keys.getPublicKeys()), 2)
            self.assertEqual(
                keys.getPrivateKeyForPublicKey(
                    "BTS5u9tEsKaqtCpKibrXJAMhaRUVBspB5pr9X34PPdrSbvBb6ajZY"
                ),
                "5Hqr1Rx6v3MLAvaYCxLYqaSEsm4eHaDFkLksPF2e1sDS7omneaZ"
            )
            keys.delete("BTS5u9tEsKaqtCpKibrXJAMhaRUVBspB5pr9X34PPdrSbvBb6ajZY")
            self.assertEqual(len(keys.getPublicKeys()), 1)

    def test_masterpassword(self):
        password = "foobar"
        config = storage.base.BaseStore()
        keys = storage.base.DefaultEncryptedKeyStore(storage=config)
        self.assertFalse(keys.has_masterpassword())
        master = keys.newMaster(password)
        self.assertEqual(
            len(master),
            len("66eaab244153031e8172e6ffed3217288515ddb63646bbefa981a654bdf25b9f")
        )
        with self.assertRaises(Exception):
            keys.newMaster(master)

        keys.lock()

        with self.assertRaises(Exception):
            keys.changePassword("foobar")

        keys.unlock(password)
        self.assertEqual(
            keys.decrypted_master,
            master
        )

        new_pass = "new_secret_password"
        keys.changePassword(new_pass)
        keys.lock()
        keys.unlock(new_pass)
        self.assertEqual(
            keys.decrypted_master,
            master
        )

    def test_wrongmastermass(self):
        from bitshares.exceptions import WrongMasterPasswordException
        config = storage.base.BaseStore()
        keys = storage.base.DefaultEncryptedKeyStore(storage=config)
        keys.newMaster("foobar")
        keys.lock()
        with self.assertRaises(WrongMasterPasswordException):
            keys.unlock("foobar2")
