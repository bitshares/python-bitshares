import unittest
from bitshares import BitShares, exceptions
from bitshares.instance import set_shared_bitshares_instance
from bitshares.account import Account
from bitshares.committee import Committee
from .fixtures import fixture_data


class Testcases(unittest.TestCase):

    def setUp(self):
        fixture_data()

    def test_Committee(self):
        with self.assertRaises(
            exceptions.AccountDoesNotExistsException
        ):
            Committee("FOObarNonExisting")

        c = Committee("xeroc")
        self.assertEqual(c["id"], "1.5.27")
        self.assertIsInstance(c.account, Account)

        with self.assertRaises(
            exceptions.CommitteeMemberDoesNotExistsException
        ):
            Committee("nathan")
