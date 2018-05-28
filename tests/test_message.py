import unittest
import mock
from bitshares import BitShares
from bitshares.account import Account
from bitshares.message import Message
from bitshares.instance import set_shared_bitshares_instance
from bitshares.blockchainobject import ObjectCache, BlockchainObject
from bitsharesbase.account import PrivateKey

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = BitShares(
            nobroadcast=True,
            wif=[wif]
        )
        set_shared_bitshares_instance(self.bts)
        self.bts.set_default_account("init0")

        cache = ObjectCache(default_expiration=5, no_overwrite=True)
        init0 = {
            'active': {'account_auths': [],
                       'address_auths': [],
                       'key_auths': [[str(PrivateKey(wif).pubkey),
                                      1]],
                       'weight_threshold': 1},
            'active_special_authority': [0, {}],
            'blacklisted_accounts': [],
            'blacklisting_accounts': [],
            'cashback_vb': '1.13.102',
            'id': '1.2.90742',
            'lifetime_referrer': '1.2.90742',
            'lifetime_referrer_fee_percentage': 8000,
            'membership_expiration_date': '1969-12-31T23:59:59',
            'name': 'init0',
            'network_fee_percentage': 2000,
            'options': {'extensions': [],
                        'memo_key': str(PrivateKey(wif).pubkey),
                        'num_committee': 0,
                        'num_witness': 0,
                        'votes': [],
                        'voting_account': '1.2.5'},
            'owner': {'account_auths': [],
                      'address_auths': [],
                      'key_auths': [[str(PrivateKey(wif).pubkey),
                                     1]],
                      'weight_threshold': 1},
            'owner_special_authority': [0, {}],
            'referrer': '1.2.90742',
            'referrer_rewards_percentage': 0,
            'registrar': '1.2.90742',
            'statistics': '2.6.90742',
            'top_n_control_flags': 0,
            'whitelisted_accounts': [],
            'whitelisting_accounts': []}
        cache[init0["id"]] = init0
        cache[init0["name"]] = init0
        BlockchainObject._cache = cache

    def test_sign_message(self):
        p = Message("message foobar").sign()
        Message(p).verify()

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
