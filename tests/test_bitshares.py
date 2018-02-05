import mock
import string
import unittest
import random
from pprint import pprint
from bitshares import BitShares
from bitsharesbase.operationids import getOperationNameForId
from bitshares.amount import Amount
from bitsharesbase.account import PrivateKey
from bitshares.instance import set_shared_bitshares_instance

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
core_unit = "TEST"


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = BitShares(
            "wss://node.testnet.bitshares.eu",
            nobroadcast=True,
            keys={"active": wif, "owner": wif, "memo": wif},
        )
        # from getpass import getpass
        # self.bts.wallet.unlock(getpass())
        set_shared_bitshares_instance(self.bts)
        self.bts.set_default_account("init0")

    def test_connect(self):
        self.bts.connect()

    def test_set_default_account(self):
        self.bts.set_default_account("init0")

    def test_info(self):
        info = self.bts.info()
        for key in ['current_witness',
                    'head_block_id',
                    'head_block_number',
                    'id',
                    'last_irreversible_block_num',
                    'next_maintenance_time',
                    'recently_missed_count',
                    'time']:
            self.assertTrue(key in info)

    def test_finalizeOps(self):
        bts = self.bts
        tx1 = bts.new_tx()
        tx2 = bts.new_tx()
        self.bts.transfer("init1", 1, core_unit, append_to=tx1)
        self.bts.transfer("init1", 2, core_unit, append_to=tx2)
        self.bts.transfer("init1", 3, core_unit, append_to=tx1)
        tx1 = tx1.json()
        tx2 = tx2.json()
        ops1 = tx1["operations"]
        ops2 = tx2["operations"]
        self.assertEqual(len(ops1), 2)
        self.assertEqual(len(ops2), 1)

    def test_transfer(self):
        bts = self.bts
        tx = bts.transfer(
            "1.2.8", 1.33, core_unit, memo="Foobar", account="1.2.7")
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "transfer"
        )
        op = tx["operations"][0][1]
        self.assertIn("memo", op)
        self.assertEqual(op["from"], "1.2.7")
        self.assertEqual(op["to"], "1.2.8")
        amount = Amount(op["amount"])
        self.assertEqual(float(amount), 1.33)

    def test_create_account(self):
        bts = self.bts
        name = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
        key1 = PrivateKey()
        key2 = PrivateKey()
        key3 = PrivateKey()
        key4 = PrivateKey()
        tx = bts.create_account(
            name,
            registrar="init0",   # 1.2.7
            referrer="init1",    # 1.2.8
            referrer_percent=33,
            owner_key=format(key1.pubkey, core_unit),
            active_key=format(key2.pubkey, core_unit),
            memo_key=format(key3.pubkey, core_unit),
            additional_owner_keys=[format(key4.pubkey, core_unit)],
            additional_active_keys=[format(key4.pubkey, core_unit)],
            additional_owner_accounts=["committee-account"],  # 1.2.0
            additional_active_accounts=["committee-account"],
            proxy_account="init0",
            storekeys=False
        )
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "account_create"
        )
        op = tx["operations"][0][1]
        role = "active"
        self.assertIn(
            format(key4.pubkey, core_unit),
            [x[0] for x in op[role]["key_auths"]])
        self.assertIn(
            format(key4.pubkey, core_unit),
            [x[0] for x in op[role]["key_auths"]])
        self.assertIn(
            "1.2.0",
            [x[0] for x in op[role]["account_auths"]])
        role = "owner"
        self.assertIn(
            format(key4.pubkey, core_unit),
            [x[0] for x in op[role]["key_auths"]])
        self.assertIn(
            format(key4.pubkey, core_unit),
            [x[0] for x in op[role]["key_auths"]])
        self.assertIn(
            "1.2.0",
            [x[0] for x in op[role]["account_auths"]])
        self.assertEqual(
            op["options"]["voting_account"],
            "1.2.6")
        self.assertEqual(
            op["registrar"],
            "1.2.6")
        self.assertEqual(
            op["referrer"],
            "1.2.7")
        self.assertEqual(
            op["referrer_percent"],
            33 * 100)

    def test_weight_threshold(self):
        bts = self.bts

        auth = {'account_auths': [['1.2.0', '1']],
                'extensions': [],
                'key_auths': [
                    ['TEST55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n', 1],
                    ['TEST7GM9YXcsoAJAgKbqW2oVj7bnNXFNL4pk9NugqKWPmuhoEDbkDv', 1]],
                'weight_threshold': 3}  # threshold fine
        bts._test_weights_treshold(auth)
        auth = {'account_auths': [['1.2.0', '1']],
                'extensions': [],
                'key_auths': [
                    ['TEST55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n', 1],
                    ['TEST7GM9YXcsoAJAgKbqW2oVj7bnNXFNL4pk9NugqKWPmuhoEDbkDv', 1]],
                'weight_threshold': 4}  # too high

        with self.assertRaises(ValueError):
            bts._test_weights_treshold(auth)

    def test_allow(self):
        bts = self.bts
        tx = bts.allow(
            "TEST55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n",
            weight=1,
            threshold=1,
            permission="owner"
        )
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "account_update"
        )
        op = tx["operations"][0][1]
        self.assertIn("owner", op)
        self.assertIn(
            ["TEST55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n", '1'],
            op["owner"]["key_auths"])
        self.assertEqual(op["owner"]["weight_threshold"], 1)

    def test_disallow(self):
        bts = self.bts
        with self.assertRaisesRegex(ValueError, ".*Changes nothing.*"):
            bts.disallow(
                "TEST55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n",
                weight=1,
                threshold=1,
                permission="owner"
            )
        with self.assertRaisesRegex(ValueError, ".*Changes nothing!.*"):
            bts.disallow(
                "TEST6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                weight=1,
                threshold=1,
                permission="owner"
            )

    def test_update_memo_key(self):
        bts = self.bts
        tx = bts.update_memo_key("TEST55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n")
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "account_update"
        )
        op = tx["operations"][0][1]
        self.assertEqual(
            op["new_options"]["memo_key"],
            "TEST55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n")

    def test_approvewitness(self):
        bts = self.bts
        tx = bts.approvewitness("init0")
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "account_update"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "1:0",
            op["new_options"]["votes"])

    def test_approvecommittee(self):
        bts = self.bts
        tx = bts.approvecommittee("init0")
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "account_update"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "0:11",
            op["new_options"]["votes"])
