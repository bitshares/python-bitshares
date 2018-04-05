import unittest
from transnet import Transnet, exceptions
from transnet.instance import set_shared_transnet_instance
from transnet.account import Account
from transnet.committee import Committee


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = Transnet(
            nobroadcast=True,
        )
        set_shared_transnet_instance(self.bts)

    def test_Committee(self):
        with self.assertRaises(
            exceptions.AccountDoesNotExistsException
        ):
            Committee("FOObarNonExisting")

        c = Committee("init0")
        self.assertEqual(c["id"], "1.5.0")
        self.assertIsInstance(c.account, Account)

        with self.assertRaises(
            exceptions.CommitteeMemberDoesNotExistsException
        ):
            Committee("nathan")
