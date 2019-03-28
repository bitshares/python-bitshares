# -*- coding: utf-8 -*-
import random
import unittest

from pprint import pprint
from binascii import hexlify

from bitshares import BitShares
from bitsharesbase import transactions, memo, account, operations, objects
from bitsharesbase.objects import Operation
from bitsharesbase.signedtransactions import Signed_Transaction
from bitsharesbase.account import PrivateKey
from graphenebase.base58 import ripemd160

from .fixtures import fixture_data, bitshares, wif


prefix = "BTS"
ref_block_num = 34294
ref_block_prefix = 3707022213
expiration = "2016-04-06T08:29:27"


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def doit(self, printWire=False):
        ops = [Operation(self.op)]
        tx = Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops,
        )
        pprint(tx.json())
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], prefix)
        txWire = hexlify(bytes(tx)).decode("ascii")

        if printWire:
            print()
            print(txWire)
            print()

        # Test against Bitshares backened
        live = bitshares.rpc.get_transaction_hex(tx.json())

        # Compare expected result with test unit
        self.assertEqual(self.cm[:-130], txWire[:-130])

        # Compare expected result with online result
        self.assertEqual(live[:-130], txWire[:-130])

        # Compare expected result with online backend
        self.assertEqual(live[:-130], self.cm[:-130])

    def test_call_update(self):
        self.op = operations.Call_order_update(
            **{
                "fee": {"amount": 100, "asset_id": "1.3.0"},
                "delta_debt": {"amount": 10000, "asset_id": "1.3.22"},
                "delta_collateral": {"amount": 100000000, "asset_id": "1.3.0"},
                "funding_account": "1.2.29",
                "extensions": {},
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701036400000000000000001d00e1f"
            "50500000000001027000000000000160000011f2627efb5c5"
            "144440e06ff567f1a09928d699ac6f5122653cd7173362a1a"
            "e20205952c874ed14ccec050be1c86c1a300811763ef3b481"
            "e562e0933c09b40e31fb"
        )
        self.doit()

    def test_limit_order_create(self):
        self.op = operations.Limit_order_create(
            **{
                "fee": {"amount": 100, "asset_id": "1.3.0"},
                "seller": "1.2.29",
                "amount_to_sell": {"amount": 100000, "asset_id": "1.3.0"},
                "min_to_receive": {"amount": 10000, "asset_id": "1.3.105"},
                "expiration": "2016-05-18T09:22:05",
                "fill_or_kill": False,
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701016400000000000000001da08601000"
            "0000000001027000000000000693d343c57000000011f75cbfd49"
            "ae8d9b04af76cc0a7de8b6e30b71167db7fe8e2197ef9d858df18"
            "77043493bc24ffdaaffe592357831c978fd8a296b913979f106de"
            "be940d60d77b50"
        )
        self.doit()

    def test_limit_order_cancel(self):
        self.op = operations.Limit_order_cancel(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "fee_paying_account": "1.2.104",
                "order": "1.7.51840",
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701020000000000000000006880950300000"
            "11f3fb754814f3910c1a8845486b86057d2b4588ae559b4c3810828"
            "c0d4cbec0e5b23517937cd7e0cc5ee8999d0777af7fe56d3c4b2e58"
            "7421bfb7400d4efdae97a"
        )
        self.doit()

    def test_proposal_update(self):
        self.op = operations.Proposal_update(
            **{
                "fee_paying_account": "1.2.1",
                "proposal": "1.10.90",
                "active_approvals_to_add": ["1.2.5"],
                "fee": objects.Asset(amount=12512, asset_id="1.3.0"),
            }
        )
        self.cm = (
            "f68585abf4dce7c804570117e03000000000000000015a01050000000"
            "000000001203255378db6dc19443e74421c954ad7fdcf23f4ea45fe4f"
            "e5a1b078a0f94fb529594819c9799d68efa5cfb5b271a9333a2f516ca"
            "4fb5093226275f48a42d9e8cf"
        )
        self.doit()

    def test_transfer(self):
        pub = format(account.PrivateKey(wif).pubkey, prefix)
        from_account_id = "1.2.0"
        to_account_id = "1.2.1"
        amount = 1000000
        asset_id = "1.3.4"
        message = "abcdefgABCDEFG0123456789"
        nonce = "5862723643998573708"

        fee = objects.Asset(amount=0, asset_id="1.3.0")
        amount = objects.Asset(amount=int(amount), asset_id=asset_id)
        self.op = operations.Transfer(
            **{
                "fee": fee,
                "from": from_account_id,
                "to": to_account_id,
                "amount": amount,
                "memo": {
                    "from": pub,
                    "to": pub,
                    "nonce": nonce,
                    "message": memo.encode_memo(
                        account.PrivateKey(wif),
                        account.PublicKey(pub, prefix=prefix),
                        nonce,
                        message,
                    ),
                },
                "prefix": prefix,
            }
        )
        self.cm = (
            "f68585abf4dce7c804570100000000000000000000000140420"
            "f0000000000040102c0ded2bc1f1305fb0faac5e6c03ee3a192"
            "4234985427b6167ca569d13df435cf02c0ded2bc1f1305fb0fa"
            "ac5e6c03ee3a1924234985427b6167ca569d13df435cf8c94d1"
            "9817945c5120fa5b6e83079a878e499e2e52a76a7739e9de409"
            "86a8e3bd8a68ce316cee50b210000011f39e3fa7071b795491e"
            "3b6851d61e7c959be92cc7deb5d8491cf1c3c8c99a1eb44553c"
            "348fb8f5001a78b18233ac66727e32fc776d48e92d9639d64f6"
            "8e641948"
        )
        self.doit()

    def test_pricefeed(self):
        feed = objects.PriceFeed(
            **{
                "settlement_price": objects.Price(
                    base=objects.Asset(amount=214211, asset_id="1.3.0"),
                    quote=objects.Asset(amount=1241, asset_id="1.3.14"),
                ),
                "core_exchange_rate": objects.Price(
                    base=objects.Asset(amount=1241, asset_id="1.3.0"),
                    quote=objects.Asset(amount=6231, asset_id="1.3.14"),
                ),
                "maximum_short_squeeze_ratio": 1100,
                "maintenance_collateral_ratio": 1750,
            }
        )

        self.op = operations.Asset_publish_feed(
            fee=objects.Asset(amount=100, asset_id="1.3.0"),
            publisher="1.2.0",
            asset_id="1.3.3",
            feed=feed,
        )
        self.cm = (
            "f68585abf4dce7c8045701136400000000000000000003c344030"
            "00000000000d9040000000000000ed6064c04d904000000000000"
            "0057180000000000000e0000012009e13f9066fedc3c8c1eb2ac3"
            "3b15dc67ecebf708890d0f8ab62ec8283d1636002315a189f1f5a"
            "a8497b41b8e6bb7c4dc66044510fae25d8f6aebb02c7cdef10"
        )
        self.doit()

    def test_fee_pool(self):
        self.op = operations.Asset_fund_fee_pool(
            **{
                "fee": {"amount": 10001, "asset_id": "1.3.0"},
                "from_account": "1.2.282",
                "asset_id": "1.3.32",
                "amount": 15557238,
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701101127000000000000009a02207662"
            "ed00000000000000011f39f7dc7745076c9c7e612d40c68ee92d"
            "3f4b2696b1838037ce2a35ac259883ba6c6c49d91ad05a7e78d8"
            "0bb83482c273dbbc911587487bf468b85fb4f537da3d"
        )
        self.doit()

    def test_override_transfer(self):
        self.op = operations.Override_transfer(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.29",
                "from": "1.2.104",
                "to": "1.2.29",
                "amount": {"amount": 100000, "asset_id": "1.3.105"},
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701260000000000000000001d681da086"
            "01000000000069000000012030cc81722c3e67442d2f59deba18"
            "8f6079c8ba2d8318a642e6a70a125655515f20e2bd3adb2ea886"
            "cdbc7f6590c7f8c80818d9176d9085c176c736686ab6c9fd"
        )
        self.doit()

    """
    # TODO FIX THIS UNIT TEST
    def test_create_account(self):
        self.op = operations.Account_create(**{
            "fee": {"amount": 1467634,
                    "asset_id": "1.3.0"
                    },
            "registrar": "1.2.33",
            "referrer": "1.2.27",
            "referrer_percent": 3,
            "name": "foobar-f124",
            "owner": {"weight_threshold": 1,
                      "account_auths": [],
                      'key_auths': [['BTS6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x',
                                    1], [
                                    'BTS6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp',
                                    1]],
                      "address_auths": []
                      },
            "active": {"weight_threshold": 1,
                       "account_auths": [],
                       'key_auths': [['BTS6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x',
                                      1], [
                                     'BTS6zLNtyFVToBsBZDsgMhgjpwysYVbsQD6YhP3kRkQhANUB4w7Qp',
                                     1], [
                                     'BTS8CemMDjdUWSV5wKotEimhK6c4dY7p2PdzC2qM1HpAP8aLtZfE7',
                                     1
                                     ]],
                       "address_auths": []
                       },
            "options": {"memo_key": "BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
                        "voting_account": "1.2.5",
                        "num_witness": 0,
                        "num_committee": 0,
                        "votes": [],
                        "extensions": []
                        },
            "extensions": {
                "buyback_options": {
                    "asset_to_buy": "1.3.127",
                    "asset_to_buy_issuer": "1.2.31",
                    "markets": ["1.3.20"]},
                "null_ext": {},
                "owner_special_authority":
                    [1, {"asset": "1.3.127",
                         "num_top_holders": 10}]
            },
            "prefix": "BTS"
        })
        self.cm = ("f68585abf4dce7c804570105f26416000000000000211b03000b666f"
                   "6f6261722d6631323401000000000202fe8cc11cc8251de6977636b5"
                   "5c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c91"
                   "58990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e01"
                   "000001000000000303b453f46013fdbccb90b09ba169c388c34d8445"
                   "4a3b9fbec68d5a7819a734fca0010002fe8cc11cc8251de6977636b5"
                   "5c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c91"
                   "58990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e01"
                   "0000024ab336b4b14ba6d881675d1c782912783c43dbbe31693aa710"
                   "ac1896bd7c3d6105000000000000030001017f0a037f1f0114000120"
                   "508168b9615d48bd11846b3b9bcf000d1424a7915fb1cfa7f61150b5"
                   "435c060b3147c056a1f889633c43d1b88cb463e8083fa2b62a585af9"
                   "e1b7a7c23d83ae78")
        self.doit()
    """

    def test_update_account(self):
        self.op = operations.Account_update(
            **{
                "fee": {"amount": 1467634, "asset_id": "1.3.0"},
                "account": "1.2.15",
                "owner": {
                    "weight_threshold": 1,
                    "account_auths": [["1.2.96086", 1]],
                    "key_auths": [
                        ["BTS6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x", 1]
                    ],
                    "address_auths": [],
                },
                "active": {
                    "weight_threshold": 1,
                    "account_auths": [["1.2.96086", 1]],
                    "key_auths": [
                        ["BTS8CemMDjdUWSV5wKotEimhK6c4dY7p2PdzC2qM1HpAP8aLtZfE7", 1]
                    ],
                    "address_auths": [],
                },
                "new_options": {
                    "memo_key": "BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
                    "voting_account": "1.2.5",
                    "num_witness": 0,
                    "num_committee": 0,
                    "votes": [],
                    "extensions": [],
                },
                "extensions": {},
                "prefix": "BTS",
            }
        )
        self.cm = (
            "f68585abf4dce7c804570106f264160000000000000"
            "f010100000001d6ee0501000102fe8cc11cc8251de6"
            "977636b55c1ab8a9d12b0b26154ac78e56e7c4257d8"
            "bcf69010000010100000001d6ee0501000103b453f4"
            "6013fdbccb90b09ba169c388c34d84454a3b9fbec68"
            "d5a7819a734fca001000001024ab336b4b14ba6d881"
            "675d1c782912783c43dbbe31693aa710ac1896bd7c3"
            "d61050000000000000000011f78b989df5ab29697a3"
            "311f8d7fa8599c548a93809e173ab550b7d8c5051fa"
            "432699d8e24ea82399990c43528ddaf2b3cd8cd2500"
            "1c91f8094d66ae2620effc25"
        )
        self.doit()

    def test_create_proposal(self):
        self.op = operations.Proposal_create(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "fee_paying_account": "1.2.0",
                "expiration_time": "1970-01-01T00:00:00",
                "proposed_ops": [
                    {
                        "op": [
                            0,
                            {
                                "fee": {"amount": 0, "asset_id": "1.3.0"},
                                "from": "1.2.0",
                                "to": "1.2.0",
                                "amount": {"amount": 0, "asset_id": "1.3.0"},
                                "extensions": [],
                            },
                        ]
                    }
                ],
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457011600000000000000000000000000"
            "00010000000000000000000000000000000000000000000000"
            "00000001204baf7f11a7ff12337fc097ac6e82e7b68f82f02c"
            "c7e24231637c88a91ae5716674acec8a1a305073165c65e520"
            "a64769f5f62c0301ce21ab4f7c67a6801b4266"
        )
        self.doit()

    def test_whitelist(self):
        self.op = operations.Account_whitelist(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "authorizing_account": "1.2.0",
                "account_to_list": "1.2.1",
                "new_listing": 0x1,
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701070000000000000000000001010"
            "000011f14eef2978e40b369273907072dddf4b4043d9f3a08"
            "da125311c4e6b54b3e7c2a3606594fab7cf6ce381544eceda"
            "9945c8c9fccebd587cfa2d2f6a146b1639f8c"
        )
        self.doit()

    def test_vesting_withdraw(self):
        self.op = operations.Vesting_balance_withdraw(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "vesting_balance": "1.13.0",
                "owner": "1.2.0",
                "amount": {"amount": 0, "asset_id": "1.3.0"},
                "prefix": "TEST",
            }
        )
        self.cm = (
            "f68585abf4dce7c80457012100000000000000000000"
            "0000000000000000000000011f07ae9b0d1cb494e248"
            "6b99cccdf78ef8b785522af8f2233de364d4455c0626"
            "935d2d32414a2f7a6b9cdf3451730062965adeec8aa2"
            "03fca97f608411dce84309"
        )
        self.doit()

    def test_upgrade_account(self):
        self.op = operations.Account_upgrade(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account_to_upgrade": "1.2.0",
                "upgrade_to_lifetime_member": True,
                "prefix": prefix,
            }
        )
        self.cm = (
            "f68585abf4dce7c804570108000000000000000000000100000"
            "11f4e42562ada1d3fed8f8eb51dd58117e3a4024959c46955a0"
            "0d2a7e7e8b40ae7204f4617913aaaf028248d43e8c3463b8776"
            "0ca569007dba99a2c49de75bd69b3"
        )
        self.doit()

    def test_witness_update(self):
        self.op = operations.Witness_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "prefix": "TEST",
                "witness": "1.6.63",
                "witness_account": "1.2.212",
                "new_url": "https://example.com",
                "new_signing_key": "BTS5vfCLKyXYb44znYjbrJXCyvvx3SuifhmvemnQsdbf61EtoR36z",
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701150000000000000000003fd401011"
            "368747470733a2f2f6578616d706c652e636f6d0102889f66e3"
            "584423e86b615e3b07593ebec4b1ac0e08ad4a3748f0726dae7"
            "c874f0001205628a49ef823ab54f4b4c56304f5ac57bdc3768c"
            "62ac630a92de9858f5d90fad01c43bdc406293edad734d53dca"
            "a1c96546a50e3ec96d07cf1224ed329177af5"
        )
        self.doit()

    def test_feed_producer_update(self):
        self.op = operations.Asset_update_feed_producers(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.214",
                "asset_to_update": "1.3.132",
                "new_feed_producers": ["1.2.214", "1.2.341", "1.2.2414"],
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457010d000000000000000000d60184010"
            "3d601d502ee120000011f34dc3aafe350f3f8608cc3d0db3b64"
            "a8f40b60d3528c9fa9e88fc3185fc27f4922ef5612f657205ad"
            "6fc6fed68ec78c4776e1fd125278ab03c8477b37e4c569a"
        )
        self.doit()

    def test_asset_reserve(self):
        self.op = operations.Asset_reserve(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "payer": "1.2.0",
                "amount_to_reserve": {"amount": 1234567890, "asset_id": "1.3.0"},
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457010f00000000000000000000d202964"
            "900000000000000011f75065cb1155bfcaabaf55d3357d69679"
            "c7c1fe589b6dc0919fe1dde1a305009c360823a40c28907299a"
            "40c241db9cad86e27369d0e5a76b5832d585505ff177d"
        )
        self.doit()

    def test_bid_collateral(self):
        self.op = operations.Bid_collateral(
            **{
                "fee": {"amount": 100, "asset_id": "1.3.0"},
                "additional_collateral": {"amount": 10000, "asset_id": "1.3.22"},
                "debt_covered": {"amount": 100000000, "asset_id": "1.3.0"},
                "bidder": "1.2.29",
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457012d6400000000000000001d1027000"
            "0000000001600e1f50500000000000000012043b82194bce84d"
            "80b6e03eecf1dc24366fc54ca3d4733b3eb3815ca22e4b38b71"
            "dff62b3d8f151b15a06eb4ae40fce964044297f8632b4817de6"
            "2e94750ce2c5"
        )
        self.doit()

    def test_balance_claim(self):
        self.op = operations.Balance_claim(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "deposit_to_account": "1.2.121",
                "balance_to_claim": "1.15.0",
                "balance_owner_key": "BTS7YFfmNBLpcrhe7hf39NLQfgBjGvtYBtAAc4nDvZKWxVQjF4CeL",
                "total_claimed": {"amount": 229174, "asset_id": "1.3.0"},
                "prefix": prefix,
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701250000000000000000007900035d2"
            "3de4ecd631e7aae2ec37ace7da12ffceea9fae1722ff4c8fa04"
            "2ba9ecd3c2367f03000000000000000120056c75aa663a9bc3f"
            "8d8806c0c32b820d539ee938684b581657a8179769f9f604c3d"
            "1b4d7dcdc04be31ea28722da45aace8f5b983cc1a5c5a42ca79"
            "751d4d0fa"
        )
        self.doit()

    def test_asset_create(self):
        self.op = operations.Asset_create(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.0",
                "symbol": "THING",
                "precision": 0,
                "common_options": {
                    "max_supply": "1000000000000000",
                    "market_fee_percent": 0,
                    "max_market_fee": "1000000000000000",
                    "issuer_permissions": 79,
                    "flags": 0,
                    "core_exchange_rate": {
                        "base": {"amount": 0, "asset_id": "1.3.0"},
                        "quote": {"amount": 0, "asset_id": "1.3.0"},
                    },
                    "whitelist_authorities": ["1.2.0"],
                    "blacklist_authorities": ["1.2.1"],
                    "whitelist_markets": ["1.3.0"],
                    "blacklist_markets": ["1.3.1"],
                    "description": "Foobar think",
                    "extensions": [],
                },
                "bitasset_opts": {
                    "feed_lifetime_sec": 86400,
                    "minimum_feeds": 7,
                    "force_settlement_delay_sec": 86400,
                    "force_settlement_offset_percent": 100,
                    "maximum_force_settlement_volume": 50,
                    "short_backing_asset": "1.3.0",
                    "extensions": [],
                },
                "is_prediction_market": False,
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457010a000000000000000000000554484"
            "94e47000080c6a47e8d030000000080c6a47e8d03004f000000"
            "000000000000000000000000000000000000010001010100010"
            "10c466f6f626172207468696e6b000180510100078051010064"
            "0032000000000000011f1b8ac491bb327921d9346d543e530d8"
            "8acb68bade58296a7a27b0a74a28eaca762260dbb905a6415f6"
            "225a8028a810de6290badc29d16fea0ffd88bc8c0cbec4"
        )
        self.doit()

    def test_asset_update(self):
        self.op = operations.Asset_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.0",
                "asset_to_update": "1.3.0",
                "new_options": {
                    "max_supply": "1000000000000000",
                    "market_fee_percent": 0,
                    "max_market_fee": "1000000000000000",
                    "issuer_permissions": 79,
                    "flags": 0,
                    "core_exchange_rate": {
                        "base": {"amount": 0, "asset_id": "1.3.0"},
                        "quote": {"amount": 0, "asset_id": "1.3.0"},
                    },
                    "whitelist_authorities": [],
                    "blacklist_authorities": [],
                    "whitelist_markets": [],
                    "blacklist_markets": [],
                    "description": "",
                    "extensions": [],
                },
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457010b000000000000000000000000008"
            "0c6a47e8d030000000080c6a47e8d03004f0000000000000000"
            "000000000000000000000000000000000000000000011f51477"
            "1af6ac47a12a387979b6452afcd3f50514277efd7938f5227a7"
            "fe7287db529d251e2b7c31d4a2d8ed59035b78b64f95e6011d9"
            "58ab9504008a56c83cbb6"
        )
        self.doit()

    def test_asset_update_issuer_fail(self):
        with self.assertRaises(ValueError):
            self.op = operations.Asset_update(
                **{
                    "fee": {"amount": 0, "asset_id": "1.3.0"},
                    "issuer": "1.2.0",
                    "asset_to_update": "1.3.0",
                    "new_issuer": "1.2.1",
                    "extensions": [],
                }
            )

    def test_asset_update_issuer(self):
        self.op = operations.Asset_update_issuer(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.0",
                "asset_to_update": "1.3.0",
                "new_issuer": "1.2.1",
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c804570130000000000000000000000001000"
            "001207d24b86eb3e6ae1de872829223d205123aaf2c5d11eab4"
            "6d8a80dbe83a42af03687cd3c43a5dd1d7f4d7a7b5afdf8d69c"
            "42acf9224354b1af7d81bd556724a43"
        )
        self.doit()

    def test_asset_update_bitasset(self):
        self.op = operations.Asset_update_bitasset(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.0",
                "asset_to_update": "1.3.0",
                "new_options": {
                    "feed_lifetime_sec": 86400,
                    "minimum_feeds": 1,
                    "force_settlement_delay_sec": 86400,
                    "force_settlement_offset_percent": 0,
                    "maximum_force_settlement_volume": 2000,
                    "short_backing_asset": "1.3.0",
                    "extensions": [],
                },
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457010c000000000000000000000080510"
            "10001805101000000d0070000000001205e7fed2110783b4fe9"
            "ec1f1a71ad0325fce04fd11d03a534baac5cf18c52c91e6fdae"
            "b76cff9d480a96500cbfde214cadd436e8f66aa61ad3f14973e"
            "42406eca"
        )
        self.doit()

    def test_asset_issue(self):
        message = "abcdefgABCDEFG0123456789"
        nonce = "5862723643998573708"
        pub = format(account.PrivateKey(wif).pubkey, prefix)
        encrypted_memo = memo.encode_memo(
            account.PrivateKey(wif),
            account.PublicKey(pub, prefix=prefix),
            nonce,
            message,
        )
        self.op = operations.Asset_issue(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.0",
                "asset_to_issue": {"amount": 0, "asset_id": "1.3.0"},
                "memo": {
                    "from": pub,
                    "to": pub,
                    "nonce": nonce,
                    "message": encrypted_memo,
                },
                "issue_to_account": "1.2.0",
                "extensions": [],
                "prefix": prefix,
            }
        )
        self.cm = (
            "f68585abf4dce7c80457010e000000000000000000000000000"
            "00000000000000102c0ded2bc1f1305fb0faac5e6c03ee3a192"
            "4234985427b6167ca569d13df435cf02c0ded2bc1f1305fb0fa"
            "ac5e6c03ee3a1924234985427b6167ca569d13df435cf8c94d1"
            "9817945c5120fa5b6e83079a878e499e2e52a76a7739e9de409"
            "86a8e3bd8a68ce316cee50b210000012055139900ea2ae7db9d"
            "4ef0d5d4015d2d993d0590ad32662bda94daba74a5e13411aef"
            "4de6f847e9e4300e5c8c36aa8e5f9032d25fd8ca01abd58c7e9"
            "528677e4"
        )
        self.doit()

    def test_withdraw_permission_create(self):
        self.op = operations.Withdraw_permission_create(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "withdraw_from_account": "1.2.0",
                "authorized_account": "1.2.0",
                "withdrawal_limit": {"amount": 35634, "asset_id": "1.3.0"},
                "withdrawal_period_sec": 53454,
                "periods_until_expiration": 65435354,
                "period_start_time": "1970-01-01T00:00:00",
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701190000000000000000000000328b"
            "00000000000000ced00000da76e603000000000001204879cd"
            "102225b4445eb192470907361b656a26de2b455347802d4a04"
            "38a66a1618577b25bd96bee42f476b97ce3cb36e507d268b09"
            "b3324dddbac1b7617de3f0"
        )
        self.doit()

    def test_committee_create(self):
        self.op = operations.Committee_member_create(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "committee_member_account": "1.2.0",
                "url": "foobar",
            }
        )
        self.cm = (
            "f68585abf4dce7c80457011d0000000000000000000006666f"
            "6f62617200011f26ced69cf1c79c7cd5be14092b15c9bd07f2"
            "a1ea988ac3dff2e8e706d72461b21bef9a8eda4c51b5d484f7"
            "8d31567ef7066d105bcd75c215f8d919673ea57c32"
        )
        self.doit()

    def test_custom(self):
        self.op = operations.Custom(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "payer": "1.2.0",
                "required_auths": ["1.2.100", "1.2.101"],
                "id": "35235",
                "data": hexlify(b"Foobar").decode("ascii"),
            }
        )
        self.cm = (
            "f68585abf4dce7c80457012300000000000000000000026465"
            "a38906466f6f6261720001207c94df60dc9fddb63391b60925"
            "889547d5c1c5aad4bb2e45a215345c3a088974253c9434de38"
            "453802bc5a6e8de3a6bb4e4f603a6ae3e5f8fc83b234a671ee"
            "85"
        )
        self.doit()

    def test_target_collateral_ratio(self):
        self.op = operations.Call_order_update(
            **{
                "fee": {"amount": 100, "asset_id": "1.3.0"},
                "delta_debt": {"amount": 10000, "asset_id": "1.3.22"},
                "delta_collateral": {"amount": 100000000, "asset_id": "1.3.0"},
                "funding_account": "1.2.29",
                "extensions": {"target_collateral_ratio": 12345},
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701036400000000000000001d00e1f5"
            "05000000000010270000000000001601003930000120767cf8d8402b"
            "cffa3fbaf774feb128c5a34c7a25b21d64c2285a99bf254c66"
            "57158b0eeb2fb674b0aed6a31b0ec9e20b903d6b15b6bcb1cd"
            "9dd6ac22b8c5456b"
        )
        self.doit()

    def test_asset_settle(self):
        self.op = operations.Asset_settle(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "account": "1.2.123",
                "amount": {"amount": 1123456, "asset_id": "1.3.0"},
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701110000000000000000007b802411"
            "000000000000000001201a2e956a23ca695a11f284a686c856"
            "e2426b96e139728a3e354095a3586efc75327192bf5a19c77b"
            "97ed53510034210b8913f3e5d281ea49a5addb3a0b450215"
        )
        self.doit()

    def test_asset_global_settle(self):
        self.op = operations.Asset_global_settle(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.123",
                "asset_to_settle": "1.3.0",
                "settle_price": {
                    "base": {"amount": 1123456, "asset_id": "1.3.0"},
                    "quote": {"amount": 78901122, "asset_id": "1.3.0"},
                },
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701120000000000000000007b008024"
            "1100000000000082efb30400000000000000011f1656eada80"
            "7f9890ba44e140a1fe822265562e1c370485543b3f7c3b34f4"
            "0a5c5d76833c853859ad6b22ec6942f6532055844b5fd0a65e"
            "7ae7715ed249e0ce9a"
        )
        self.doit()

    def test_asset_claim_fees(self):
        self.op = operations.Asset_claim_fees(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.123",
                "amount_to_claim": {"amount": 1123456, "asset_id": "1.3.0"},
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457012b0000000000000000007b80241100"
            "00000000000000011f3c93aa7fd19e065361261ad4f7902d73ee"
            "8991f1b47d4bb62298f38e93ace2c26b7e06dff026b77515200f"
            "99c88a07aa5bfd2e7647e412f94a7246185d8c2d31"
        )
        self.doit()

    def test_asset_claim_pool(self):
        self.op = operations.Asset_claim_pool(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": "1.2.123",
                "asset_id": "1.3.1",
                "amount_to_claim": {"amount": 1123456, "asset_id": "1.3.0"},
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457012f0000000000000000007b01802411"
            "000000000000000001200d91db5fb3df23739e0319e780399830"
            "f7271d68b95aabea540cddda33108d34587290a465062cb9c4be"
            "d4f97bc339088f8ccc48935d86d807fb29ff501d4740"
        )
        self.doit()

    """
    def test_htlc_create(self):
        preimage_hash = hexlify(ripemd160(hexlify(b"foobar"))).decode("ascii")
        self.op = operations.Htlc_create(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "from": "1.2.123",
                "to": "1.2.124",
                "amount": {"amount": 1123456, "asset_id": "1.3.0"},
                "preimage_hash": [0, preimage_hash],
                "preimage_size": 200,
                "claim_period_seconds": 120,
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c8045701310000000000000000007b7c8024"
            "1100000000000000a06e327ea7388c18e4740e350ed4e60f"
            "2e04fc41c800780000000000012071efeadf31703b98d155e1"
            "c196cf12bcda11c363518075be2aaca0443382648e2428d277"
            "e79b80bab4ff0b48fd00ed91e7e41d88974a00d50b832a198a"
            "00d62d"
        )
        self.doit(False)

    def test_htlc_redeem(self):
        preimage = hexlify(b"foobar").decode("ascii")
        self.op = operations.Htlc_redeem(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "redeemer": "1.2.124",
                "preimage": preimage,
                "htlc_id": "1.16.132",
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457013200000000000000000084017c06"
            "666f6f6261720000011f21a8d2fa9a0f7c9bcc32a0dbcbf901"
            "5051f8190c4b2239472f900458eae0bb4a7f7be8d88c60eba0"
            "a8972f2e1b397d4e23f1b91eef12c38f11a01307809e4143"
        )
        self.doit(0)

    def test_htlc_extend(self):
        self.op = operations.Htlc_extend(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "htlc_id": "1.16.132",
                "update_issuer": "1.2.124",
                "seconds_to_add": 120,
                "extensions": [],
            }
        )
        self.cm = (
            "f68585abf4dce7c80457013400000000000000000084017c78"
            "000000000001206aaf202129fea824e70b92113d0812fac654"
            "00529d86210674498f03ef33d4bd1055d17020db57092ee95d"
            "c6320840059f85da3fbebaf2a965bb5eca15179f30"
        )
        self.doit(0)
    """

    def compareConstructedTX(self):
        self.maxDiff = None
        self.op = operations.Call_order_update(
            **{
                "fee": {"amount": 100, "asset_id": "1.3.0"},
                "delta_debt": {"amount": 10000, "asset_id": "1.3.22"},
                "delta_collateral": {"amount": 100000000, "asset_id": "1.3.0"},
                "funding_account": "1.2.29",
                "extensions": {"target_collateral_ratio": 12345},
            }
        )
        ops = [Operation(self.op)]
        tx = Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops,
        )
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], prefix)
        txWire = hexlify(bytes(tx)).decode("ascii")
        print("=" * 80)
        pprint(tx.json())
        print("=" * 80)

        # Test against Bitshares backened
        self.cm = bitshares.rpc.get_transaction_hex(tx.json())

        print("soll: %s" % self.cm[:-130])
        print("ist:  %s" % txWire[:-130])
        print(txWire[:-130] == self.cm[:-130])
        self.assertEqual(self.cm[:-130], txWire[:-130])
