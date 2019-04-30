import mock
import string
import unittest
import random
from pprint import pprint
from bitshares import BitShares
from bitshares.account import Account
from bitsharesbase.operationids import getOperationNameForId
from bitshares.amount import Amount
from bitsharesbase.account import PrivateKey
from bitsharesbase.asset_permissions import todict
from bitshares.instance import set_shared_bitshares_instance
from .fixtures import fixture_data, bitshares


class Testcases(unittest.TestCase):

    def setUp(self):
        fixture_data()

    def test_connect(self):
        bitshares.connect()

    def test_set_default_account(self):
        bitshares.set_default_account("init0")

    def test_info(self):
        info = bitshares.info()
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
        tx1 = bitshares.new_tx()
        tx2 = bitshares.new_tx()
        bitshares.transfer("init1", 1, "BTS", append_to=tx1)
        bitshares.transfer("init1", 2, "BTS", append_to=tx2)
        bitshares.transfer("init1", 3, "BTS", append_to=tx1)
        tx1 = tx1.json()
        tx2 = tx2.json()
        ops1 = tx1["operations"]
        ops2 = tx2["operations"]
        self.assertEqual(len(ops1), 2)
        self.assertEqual(len(ops2), 1)

    def test_transfer(self):
        tx = bitshares.transfer(
            "1.2.101", 1.33, "BTS", memo="Foobar", account="init0")
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "transfer"
        )
        op = tx["operations"][0][1]
        self.assertIn("memo", op)
        self.assertEqual(op["from"], "1.2.100")
        self.assertEqual(op["to"], "1.2.101")
        amount = Amount(op["amount"])
        self.assertEqual(float(amount), 1.33)

    def test_create_account(self):
        name = ''.join(random.choice(string.ascii_lowercase) for _ in range(12))
        key1 = PrivateKey()
        key2 = PrivateKey()
        key3 = PrivateKey()
        key4 = PrivateKey()
        tx = bitshares.create_account(
            name,
            registrar="init0",   # 1.2.100
            referrer="init1",    # 1.2.101
            referrer_percent=33,
            owner_key=format(key1.pubkey, "BTS"),
            active_key=format(key2.pubkey, "BTS"),
            memo_key=format(key3.pubkey, "BTS"),
            additional_owner_keys=[format(key4.pubkey, "BTS")],
            additional_active_keys=[format(key4.pubkey, "BTS")],
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
            format(key4.pubkey, "BTS"),
            [x[0] for x in op[role]["key_auths"]])
        self.assertIn(
            format(key4.pubkey, "BTS"),
            [x[0] for x in op[role]["key_auths"]])
        self.assertIn(
            "1.2.0",
            [x[0] for x in op[role]["account_auths"]])
        role = "owner"
        self.assertIn(
            format(key4.pubkey, "BTS"),
            [x[0] for x in op[role]["key_auths"]])
        self.assertIn(
            format(key4.pubkey, "BTS"),
            [x[0] for x in op[role]["key_auths"]])
        self.assertIn(
            "1.2.0",
            [x[0] for x in op[role]["account_auths"]])
        self.assertEqual(
            op["options"]["voting_account"],
            "1.2.100")
        self.assertEqual(
            op["registrar"],
            "1.2.100")
        self.assertEqual(
            op["referrer"],
            "1.2.101")
        self.assertEqual(
            op["referrer_percent"],
            33 * 100)

    def test_create_asset(self):
        symbol = "FOOBAR"
        precision = 7
        max_supply = 100000
        description = "Test asset"
        is_bitasset = True
        market_fee_percent = 0.1
        max_market_fee = 10
        blacklist_authorities = ["init1"]
        blacklist_authorities_ids = [Account(a)["id"] for a in blacklist_authorities]
        blacklist_markets = ["BTS"]
        blacklist_markets_ids = ["1.3.0"]
        permissions = {
            "charge_market_fee": True,
            "white_list": True,
            "override_authority": True,
            "transfer_restricted": True,
            "disable_force_settle": True,
            "global_settle": True,
            "disable_confidential": True,
            "witness_fed_asset": True,
            "committee_fed_asset": True,
        }
        flags = {
            "charge_market_fee": False,
            "white_list": False,
            "override_authority": False,
            "transfer_restricted": False,
            "disable_force_settle": False,
            "global_settle": False,
            "disable_confidential": False,
            "witness_fed_asset": False,
            "committee_fed_asset": False,
        }
        tx = bitshares.create_asset(
            symbol,
            precision,
            max_supply,
            market_fee_percent=market_fee_percent,
            max_market_fee=max_market_fee,
            description=description,
            is_bitasset=is_bitasset,
            blacklist_authorities=blacklist_authorities,
            blacklist_markets=blacklist_markets,
            permissions=permissions,
            flags=flags,
        )
        self.assertEqual(getOperationNameForId(tx["operations"][0][0]), "asset_create")
        op = tx["operations"][0][1]
        self.assertEqual(op["issuer"], "1.2.100")
        self.assertEqual(op["symbol"], symbol)
        self.assertEqual(op["precision"], precision)
        self.assertEqual(
            op["common_options"]["max_supply"], int(max_supply * 10 ** precision)
        )
        self.assertEqual(
            op["common_options"]["market_fee_percent"], int(market_fee_percent * 100)
        )
        self.assertEqual(
            op["common_options"]["max_market_fee"],
            int(max_market_fee * 10 ** precision),
        )
        self.assertEqual(op["common_options"]["description"], description)
        self.assertEqual(
            op["common_options"]["blacklist_authorities"], blacklist_authorities_ids
        )
        self.assertEqual(
            op["common_options"]["blacklist_markets"], blacklist_markets_ids
        )
        self.assertEqual(
            todict(op["common_options"]["issuer_permissions"]), permissions
        )
        self.assertEqual(todict(op["common_options"]["flags"]), flags)

    def test_weight_threshold(self):

        auth = {'account_auths': [['1.2.0', '1']],
                'extensions': [],
                'key_auths': [
                    ['BTS55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n', 1],
                    ['BTS7GM9YXcsoAJAgKbqW2oVj7bnNXFNL4pk9NugqKWPmuhoEDbkDv', 1]],
                'weight_threshold': 3}  # threshold fine
        bitshares._test_weights_treshold(auth)
        auth = {'account_auths': [['1.2.0', '1']],
                'extensions': [],
                'key_auths': [
                    ['BTS55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n', 1],
                    ['BTS7GM9YXcsoAJAgKbqW2oVj7bnNXFNL4pk9NugqKWPmuhoEDbkDv', 1]],
                'weight_threshold': 4}  # too high

        with self.assertRaises(ValueError):
            bitshares._test_weights_treshold(auth)

    def test_allow(self):
        tx = bitshares.allow(
            "BTS55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n",
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
            ["BTS55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n", '1'],
            op["owner"]["key_auths"])
        self.assertEqual(op["owner"]["weight_threshold"], 1)

    def test_disallow(self):
        with self.assertRaisesRegex(ValueError, ".*Changes nothing.*"):
            bitshares.disallow(
                "BTS55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n",
                weight=1,
                threshold=1,
                permission="owner"
            )
        with self.assertRaisesRegex(ValueError, "Cannot have threshold of 0"):
            bitshares.disallow(
                "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                weight=1,
                threshold=1,
                permission="owner"
            )
        bitshares.disallow(
            "BTS5i8bEmtnN4fP4jAsBe17z9CCuQcHLkRyTuRZXYZeN2kVCL1sXa",
            weight=1,
            threshold=1,
            permission="active"
        )

    def test_update_memo_key(self):
        tx = bitshares.update_memo_key("BTS55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n")
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "account_update"
        )
        op = tx["operations"][0][1]
        self.assertEqual(
            op["new_options"]["memo_key"],
            "BTS55VCzsb47NZwWe5F3qyQKedX9iHBHMVVFSc96PDvV7wuj7W86n")

    def test_approvewitness(self):
        tx = bitshares.approvewitness("1.6.1")
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "account_update"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "1:0",
            op["new_options"]["votes"])

    def test_approvecommittee(self):
        tx = bitshares.approvecommittee("1.5.0")
        self.assertEqual(
            getOperationNameForId(tx["operations"][0][0]),
            "account_update"
        )
        op = tx["operations"][0][1]
        self.assertIn(
            "0:11",
            op["new_options"]["votes"])
