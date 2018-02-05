import unittest
import mock
from bitshares import BitShares
from bitshares.message import Message
from bitshares.instance import set_shared_bitshares_instance

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
core_unit = "PPY"


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = BitShares(
            nobroadcast=True,
            wif=[wif]
        )
        set_shared_bitshares_instance(self.bts)

    def test_sign_message(self):
        def new_refresh(self):
            dict.__init__(
                self, {
                    "name": "init0",
                    "options": {
                        "memo_key": "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"
                    }})

        with mock.patch(
            "bitshares.account.Account.refresh",
            new=new_refresh
        ):
            p = Message("message foobar").sign()
            Message(p).verify()

    def test_verify_message(self):
        def new_refresh(self):
            dict.__init__(
                self, {
                    "name": "init0",
                    "options": {
                        "memo_key": "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"
                    }})

        with mock.patch(
            "bitshares.account.Account.refresh",
            new=new_refresh
        ):
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
                "-----END BITSHARES SIGNED MESSAGE-----\n"
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
                "-----END BITSHARES SIGNED MESSAGE-----"
            ).verify()
