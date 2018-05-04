import unittest
import mock
from pprint import pprint
from bitshares import BitShares
from bitshares.account import Account
from bitshares.amount import Amount
from bitshares.asset import Asset
from bitshares.instance import set_shared_bitshares_instance
from bitsharesbase.operationids import getOperationNameForId

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = BitShares(
            "wss://node.testnet.bitshares.eu",
            nobroadcast=True,
            # We want to bundle many operations into a single transaction
            bundle=True,
            # Overwrite wallet to use this list of wifs only
            wif={"active": wif}
        )
        self.bts.set_default_account("init0")
        set_shared_bitshares_instance(self.bts)

    def test_account(self):
        Account("witness-account")
        Account("1.2.3")
        asset = Asset("1.3.0")
        symbol = asset["symbol"]
        account = Account("witness-account", full=True)
        self.assertEqual(account.name, "witness-account")
        self.assertEqual(account["name"], account.name)
        self.assertEqual(account["id"], "1.2.1")
        self.assertIsInstance(account.balance("1.3.0"), Amount)
        # self.assertIsInstance(account.balance({"symbol": symbol}), Amount)
        self.assertIsInstance(account.balances, list)
        for h in account.history(limit=1):
            pass

        # BlockchainObjects method
        account.cached = False
        self.assertTrue(account.items())
        account.cached = False
        self.assertIn("id", account)
        account.cached = False
        self.assertEqual(account["id"], "1.2.1")
        self.assertEqual(str(account), "<Account 1.2.1>")
        self.assertIsInstance(Account(account), Account)

    def test_account_upgrade(self):
        account = Account("witness-account")
        tx = account.upgrade()
        ops = tx["operations"]
        op = ops[0][1]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "account_upgrade"
        )
        self.assertTrue(
            op["upgrade_to_lifetime_member"]
        )
        self.assertEqual(
            op["account_to_upgrade"],
            "1.2.1",
        )

    def test_openorders(self):
        account = Account("witness-account")
        self.assertIsInstance(account.openorders, list)

    def test_calls(self):
        account = Account("witness-account")
        self.assertIsInstance(account.callpositions, dict)

    def test_whitelist(self):
        from bitsharesbase.operations import Account_whitelist
        account = Account("witness-account")
        tx = account.whitelist("committee-account")
        self.assertEqual(len(tx["operations"]), 1)
        self.assertEqual(tx["operations"][0][0], 7)
        self.assertEqual(tx["operations"][0][1]["authorizing_account"], account["id"])
        self.assertEqual(tx["operations"][0][1]["new_listing"], Account_whitelist.white_listed)

    def test_blacklist(self):
        from bitsharesbase.operations import Account_whitelist
        account = Account("witness-account")
        tx = account.blacklist("committee-account")
        self.assertEqual(len(tx["operations"]), 1)
        self.assertEqual(tx["operations"][0][0], 7)
        self.assertEqual(tx["operations"][0][1]["authorizing_account"], account["id"])
        self.assertEqual(tx["operations"][0][1]["new_listing"], Account_whitelist.black_listed)

    def test_unlist(self):
        from bitsharesbase.operations import Account_whitelist
        account = Account("witness-account")
        tx = account.nolist("committee-account")
        self.assertEqual(len(tx["operations"]), 1)
        self.assertEqual(tx["operations"][0][0], 7)
        self.assertEqual(tx["operations"][0][1]["authorizing_account"], account["id"])
        self.assertEqual(tx["operations"][0][1]["new_listing"], Account_whitelist.no_listing)

    def test_accountupdate(self):
        from bitshares.account import AccountUpdate
        t = {'id': '2.6.29',
             'lifetime_fees_paid': '44261516129',
             'most_recent_op': '2.9.0',
             'owner': '1.2.29',
             'pending_fees': 0,
             'pending_vested_fees': 16310,
             'total_core_in_orders': '6788845277634',
             'total_ops': 0}
        update = AccountUpdate(t)
        self.assertEqual(update["owner"], "1.2.29")
        self.assertIsInstance(update.account, Account)
        update.__repr__()

        update = AccountUpdate("committee-account")
        self.assertEqual(update["owner"], "1.2.0")
        self.assertIsInstance(update.account, Account)
        update.__repr__()
