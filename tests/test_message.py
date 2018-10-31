import unittest
import mock
from bitshares.message import Message
from .fixtures import fixture_data, bitshares


class Testcases(unittest.TestCase):

    def setUp(self):
        fixture_data()

    def test_sign_message(self):
        p = Message("message foobar", blockchain_instance=bitshares).sign(account="init0")
        Message(p, blockchain_instance=bitshares).verify()

    def test_verify_message(self):
        Message(
            "-----BEGIN BITSHARES SIGNED MESSAGE-----\n"
            "message foobar\n"
            "-----BEGIN META-----\n"
            "account=init0\n"
            "memokey=BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV\n"
            "block=23814223\n"
            "timestamp=2018-01-24T11:42:33\n"
            "-----BEGIN SIGNATURE-----\n"
            "2034f601e175a25cf9f60a828650301f57c9efab53929b6a82fb413feb8a786fcb3ba4238dd8bece03aee38526ee363324d43944d4a3f9dc624fbe53ef5f0c9a5e\n"
            "-----END BITSHARES SIGNED MESSAGE-----\n",
            blockchain_instance=bitshares
        ).verify()

        Message(
            "-----BEGIN BITSHARES SIGNED MESSAGE-----"
            "message foobar\n"
            "-----BEGIN META-----"
            "account=init0\n"
            "memokey=BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV\n"
            "block=23814223\n"
            "timestamp=2018-01-24T11:42:33"
            "-----BEGIN SIGNATURE-----"
            "2034f601e175a25cf9f60a828650301f57c9efab53929b6a82fb413feb8a786fcb3ba4238dd8bece03aee38526ee363324d43944d4a3f9dc624fbe53ef5f0c9a5e\n"
            "-----END BITSHARES SIGNED MESSAGE-----",
            blockchain_instance=bitshares
        ).verify()
