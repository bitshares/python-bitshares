# -*- coding: utf-8 -*-
import unittest
import mock
from pprint import pprint
from bitshares import BitShares
from bitshares.account import Account
from bitshares.amount import Amount
from bitshares.asset import Asset
from bitshares.price import Order
from bitshares.instance import set_shared_bitshares_instance
from bitsharesbase.operationids import getOperationNameForId
from .fixtures import fixture_data, bitshares


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_account(self):
        Account("init0")
        Account("1.2.3")
        account = Account("init0", full=True)
        self.assertEqual(account.name, "init0")
        self.assertEqual(account["name"], account.name)
        self.assertEqual(account["id"], "1.2.100")
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
        self.assertEqual(account["id"], "1.2.100")
        self.assertTrue(str(account).startswith("<Account "))
        self.assertIsInstance(Account(account), Account)

    def test_account_upgrade(self):
        account = Account("init0")
        pprint(account)
        tx = account.upgrade()
        ops = tx["operations"]
        op = ops[0][1]
        self.assertEqual(len(ops), 1)
        self.assertEqual(getOperationNameForId(ops[0][0]), "account_upgrade")
        self.assertTrue(op["upgrade_to_lifetime_member"])
        self.assertEqual(op["account_to_upgrade"], "1.2.100")

    def test_openorders(self):
        account = Account("xeroc")
        orders = account.openorders
        self.assertIsInstance(orders, list)

        # If this test fails, it may be that the order expired on-chain!
        #
        # $ uptick sell 100.000 PORNXXX 100000 BTS --account xeroc
        #
        for order in orders:
            self.assertIsInstance(order, Order)
            self.assertEqual(order["for_sale"]["symbol"], "PORNXXX")

    def test_calls(self):
        account = Account("init0")
        self.assertIsInstance(account.callpositions, dict)

    def test_whitelist(self):
        from bitsharesbase.operations import Account_whitelist

        account = Account("init0")
        tx = account.whitelist("committee-account")
        self.assertEqual(len(tx["operations"]), 1)
        self.assertEqual(tx["operations"][0][0], 7)
        self.assertEqual(tx["operations"][0][1]["authorizing_account"], account["id"])
        self.assertEqual(
            tx["operations"][0][1]["new_listing"], Account_whitelist.white_listed
        )

    def test_blacklist(self):
        from bitsharesbase.operations import Account_whitelist

        account = Account("init0")
        tx = account.blacklist("committee-account")
        self.assertEqual(len(tx["operations"]), 1)
        self.assertEqual(tx["operations"][0][0], 7)
        self.assertEqual(tx["operations"][0][1]["authorizing_account"], account["id"])
        self.assertEqual(
            tx["operations"][0][1]["new_listing"], Account_whitelist.black_listed
        )

    def test_unlist(self):
        from bitsharesbase.operations import Account_whitelist

        account = Account("init0")
        tx = account.nolist("committee-account")
        self.assertEqual(len(tx["operations"]), 1)
        self.assertEqual(tx["operations"][0][0], 7)
        self.assertEqual(tx["operations"][0][1]["authorizing_account"], account["id"])
        self.assertEqual(
            tx["operations"][0][1]["new_listing"], Account_whitelist.no_listing
        )

    def test_accountupdate(self):
        from bitshares.account import AccountUpdate

        t = {
            "id": "2.6.29",
            "lifetime_fees_paid": "44261516129",
            "most_recent_op": "2.9.0",
            "owner": "1.2.100",
            "pending_fees": 0,
            "pending_vested_fees": 16310,
            "total_core_in_orders": "6788845277634",
            "total_ops": 0,
        }
        update = AccountUpdate(t)
        self.assertEqual(update["owner"], "1.2.100")
        self.assertIsInstance(update.account, Account)
        update.__repr__()

        update = AccountUpdate("committee-account")
        self.assertEqual(update["owner"], "1.2.0")
        self.assertIsInstance(update.account, Account)
        update.__repr__()
