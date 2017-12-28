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
