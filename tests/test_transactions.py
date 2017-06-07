from bitsharesbase import (
    transactions,
    memo,
    account,
    operations,
    objects
)
from bitsharesbase.objects import Operation
from bitsharesbase.signedtransactions import Signed_Transaction
from bitsharesbase.account import PrivateKey
import random
import unittest
from pprint import pprint
from binascii import hexlify

prefix = "BTS"
wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"
ref_block_num = 34294
ref_block_prefix = 3707022213
expiration = "2016-04-06T08:29:27"


class Testcases(unittest.TestCase):

    def test_call_update(self):
        op = operations.Call_order_update(**{
            'fee': {'amount': 100,
                    'asset_id': '1.3.0'},
            'delta_debt': {'amount': 10000,
                           'asset_id': '1.3.22'},
            'delta_collateral': {'amount': 100000000,
                                 'asset_id': '1.3.0'},
            'funding_account': '1.2.29',
            'extensions': []
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c8045701036400000000000000001d00e1f"
                   "50500000000001027000000000000160000011f2627efb5c5"
                   "144440e06ff567f1a09928d699ac6f5122653cd7173362a1a"
                   "e20205952c874ed14ccec050be1c86c1a300811763ef3b481"
                   "e562e0933c09b40e31fb")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_limit_order_create(self):
        op = operations.Limit_order_create(**{
            "fee": {"amount": 100,
                    "asset_id": "1.3.0"
                    },
            "seller": "1.2.29",
            "amount_to_sell": {"amount": 100000,
                               "asset_id": "1.3.0"
                               },
            "min_to_receive": {"amount": 10000,
                               "asset_id": "1.3.105"
                               },
            "expiration": "2016-05-18T09:22:05",
            "fill_or_kill": False,
            "extensions": []
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c8045701016400000000000000001da08601000"
                   "0000000001027000000000000693d343c57000000011f75cbfd49"
                   "ae8d9b04af76cc0a7de8b6e30b71167db7fe8e2197ef9d858df18"
                   "77043493bc24ffdaaffe592357831c978fd8a296b913979f106de"
                   "be940d60d77b50")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_limit_order_cancel(self):
        op = operations.Limit_order_cancel(**{
            "fee": {"amount": 0,
                    "asset_id": "1.3.0"
                    },
            "fee_paying_account": "1.2.104",
            "order": "1.7.51840",
            "extensions": []
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c8045701020000000000000000006880950300000"
                   "11f3fb754814f3910c1a8845486b86057d2b4588ae559b4c3810828"
                   "c0d4cbec0e5b23517937cd7e0cc5ee8999d0777af7fe56d3c4b2e58"
                   "7421bfb7400d4efdae97a")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_proposal_update(self):
        op = operations.Proposal_update(**{
            'fee_paying_account': "1.2.1",
            'proposal': "1.10.90",
            'active_approvals_to_add': ["1.2.5"],
            "fee": objects.Asset(amount=12512, asset_id="1.3.0"),
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c804570117e03000000000000000015a01050000000"
                   "000000001203255378db6dc19443e74421c954ad7fdcf23f4ea45fe4f"
                   "e5a1b078a0f94fb529594819c9799d68efa5cfb5b271a9333a2f516ca"
                   "4fb5093226275f48a42d9e8cf")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_Transfer(self):
        pub = format(account.PrivateKey(wif).pubkey, prefix)
        from_account_id = "1.2.0"
        to_account_id = "1.2.1"
        amount = 1000000
        asset_id = "1.3.4"
        message = "abcdefgABCDEFG0123456789"
        nonce = "5862723643998573708"

        fee = objects.Asset(amount=0, asset_id="1.3.0")
        amount = objects.Asset(amount=int(amount), asset_id=asset_id)
        encrypted_memo = memo.encode_memo(
            account.PrivateKey(wif),
            account.PublicKey(pub, prefix=prefix),
            nonce,
            message
        )
        memoStruct = {
            "from": pub,
            "to": pub,
            "nonce": nonce,
            "message": encrypted_memo,
            "chain": prefix
        }
        memoObj = objects.Memo(**memoStruct)
        op = operations.Transfer(**{
            "fee": fee,
            "from": from_account_id,
            "to": to_account_id,
            "amount": amount,
            "memo": memoObj
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")

        compare = ("f68585abf4dce7c804570100000000000000000000000140420"
                   "f0000000000040102c0ded2bc1f1305fb0faac5e6c03ee3a192"
                   "4234985427b6167ca569d13df435cf02c0ded2bc1f1305fb0fa"
                   "ac5e6c03ee3a1924234985427b6167ca569d13df435cf8c94d1"
                   "9817945c5120fa5b6e83079a878e499e2e52a76a7739e9de409"
                   "86a8e3bd8a68ce316cee50b210000011f39e3fa7071b795491e"
                   "3b6851d61e7c959be92cc7deb5d8491cf1c3c8c99a1eb44553c"
                   "348fb8f5001a78b18233ac66727e32fc776d48e92d9639d64f6"
                   "8e641948")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_pricefeed(self):
        feed = objects.PriceFeed(**{
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
        })

        op = operations.Asset_publish_feed(
            fee=objects.Asset(amount=100, asset_id="1.3.0"),
            publisher="1.2.0",
            asset_id="1.3.3",
            feed=feed
        )
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")

        compare = ("f68585abf4dce7c8045701136400000000000000000003c344030"
                   "00000000000d9040000000000000ed6064c04d904000000000000"
                   "0057180000000000000e0000012009e13f9066fedc3c8c1eb2ac3"
                   "3b15dc67ecebf708890d0f8ab62ec8283d1636002315a189f1f5a"
                   "a8497b41b8e6bb7c4dc66044510fae25d8f6aebb02c7cdef10")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_jsonLoading(self):
        data1 = {"expiration": expiration,
                 "ref_block_num": ref_block_num,
                 "ref_block_prefix": ref_block_prefix,
                 "extensions": [],
                 "operations": [[0,
                                 {"amount": {"amount": 1000000, "asset_id": "1.3.4"},
                                  "extensions": [],
                                  "fee": {"amount": 0, "asset_id": "1.3.0"},
                                  "from": "1.2.0",
                                  "memo": {"from": "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                                           "message": "fa5b6e83079a878e499e2e52a76a7739e9de40986a8e3bd8a68ce316cee50b21",
                                           "nonce": 5862723643998573708,
                                           "to": "BTS6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV"},
                                  "to": "1.2.1"}]],
                 "signatures": ["1f6c1e8df5faf18c3b057ce713ec92f9" +
                                "b487c1ba58138daabc0038741b402c93" +
                                "0d63d8d63861740215b4f65eb8ac9185" +
                                "a3987f8239b962181237f47189e21102" +
                                "af"]}
        a = Signed_Transaction(data1.copy())
        data2 = a.json()

        check1 = data1
        check2 = data2
        for key in ["expiration", "extensions", "ref_block_num", "ref_block_prefix", "signatures"]:
            self.assertEqual(check1[key], check2[key])

        check1 = data1["operations"][0][1]
        check2 = data2["operations"][0][1]
        for key in ["from", "to"]:
            self.assertEqual(check1[key], check2[key])

        check1 = data1["operations"][0][1]["memo"]
        check2 = data2["operations"][0][1]["memo"]
        for key in check1:
            self.assertEqual(check1[key], check2[key])

    def test_fee_pool(self):
        s = {"fee": {"amount": 10001,
                     "asset_id": "1.3.0"
                     },
             "from_account": "1.2.282",
             "asset_id": "1.3.32",
             "amount": 15557238,
             "extensions": []
             }
        op = operations.Asset_fund_fee_pool(**s)
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c8045701101127000000000000009a02207662"
                   "ed00000000000000011f39f7dc7745076c9c7e612d40c68ee92d"
                   "3f4b2696b1838037ce2a35ac259883ba6c6c49d91ad05a7e78d8"
                   "0bb83482c273dbbc911587487bf468b85fb4f537da3d")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_override_transfer(self):
        s = {"fee": {"amount": 0,
                     "asset_id": "1.3.0"},
             "issuer": "1.2.29",
             "from": "1.2.104",
             "to": "1.2.29",
             "amount": {"amount": 100000,
                        "asset_id": "1.3.105"},
             "extensions": []
             }
        op = operations.Override_transfer(**s)
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c8045701260000000000000000001d681da086"
                   "01000000000069000000012030cc81722c3e67442d2f59deba18"
                   "8f6079c8ba2d8318a642e6a70a125655515f20e2bd3adb2ea886"
                   "cdbc7f6590c7f8c80818d9176d9085c176c736686ab6c9fd")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_create_account(self):
        s = {"fee": {"amount": 1467634,
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
             "extensions": {}
             }
        op = operations.Account_create(**s)
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c804570105f26416000000000000211b03000b666f"
                   "6f6261722d6631323401000000000202fe8cc11cc8251de6977636b5"
                   "5c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c91"
                   "58990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e01"
                   "000001000000000303b453f46013fdbccb90b09ba169c388c34d8445"
                   "4a3b9fbec68d5a7819a734fca0010002fe8cc11cc8251de6977636b5"
                   "5c1ab8a9d12b0b26154ac78e56e7c4257d8bcf6901000314aa202c91"
                   "58990b3ec51a1aa49b2ab5d300c97b391df3beb34bb74f3c62699e01"
                   "0000024ab336b4b14ba6d881675d1c782912783c43dbbe31693aa710"
                   "ac1896bd7c3d61050000000000000000011f61ad276120bc3f189296"
                   "2bfff7db5e8ce04d5adec9309c80529e3a978a4fa1073225a6d56929"
                   "e34c9d2a563e67a8f4a227e4fadb4a3bb6ec91bfdf4e57b80efd")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_update_account(self):
        op = operations.Account_update(**{
            "fee": {"amount": 1467634,
                    "asset_id": "1.3.0"
                    },
            "account": "1.2.15",
            "owner": {"weight_threshold": 1,
                      "account_auths": [["1.2.96086", 1]],
                      'key_auths': [['BTS6pbVDAjRFiw6fkiKYCrkz7PFeL7XNAfefrsREwg8MKpJ9VYV9x',
                                    1]],
                      "address_auths": []
                      },
            "active": {"weight_threshold": 1,
                       "account_auths": [["1.2.96086", 1]],
                       'key_auths': [['BTS8CemMDjdUWSV5wKotEimhK6c4dY7p2PdzC2qM1HpAP8aLtZfE7',
                                     1]],
                       "address_auths": []
                       },
            "new_options": {"memo_key": "BTS5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
                            "voting_account": "1.2.5",
                            "num_witness": 0,
                            "num_committee": 0,
                            "votes": [],
                            "extensions": []
                            },
            "extensions": {}
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c804570106f264160000000000000"
                   "f010100000001d6ee0501000102fe8cc11cc8251de6"
                   "977636b55c1ab8a9d12b0b26154ac78e56e7c4257d8"
                   "bcf69010000010100000001d6ee0501000103b453f4"
                   "6013fdbccb90b09ba169c388c34d84454a3b9fbec68"
                   "d5a7819a734fca001000001024ab336b4b14ba6d881"
                   "675d1c782912783c43dbbe31693aa710ac1896bd7c3"
                   "d61050000000000000000011f78b989df5ab29697a3"
                   "311f8d7fa8599c548a93809e173ab550b7d8c5051fa"
                   "432699d8e24ea82399990c43528ddaf2b3cd8cd2500"
                   "1c91f8094d66ae2620effc25")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_create_proposal(self):
        op = operations.Proposal_create(**{
            "fee": {"amount": 0,
                    "asset_id": "1.3.0"
                    },
            "fee_paying_account": "1.2.0",
            "expiration_time": "1970-01-01T00:00:00",
            "proposed_ops": [{
                "op": [
                    0, {"fee": {"amount": 0,
                                "asset_id": "1.3.0"
                                },
                        "from": "1.2.0",
                        "to": "1.2.0",
                        "amount": {"amount": 0,
                                   "asset_id": "1.3.0"
                                   },
                        "extensions": []}]}],
            "extensions": []
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c80457011600000000000000000000000000"
                   "00010000000000000000000000000000000000000000000000"
                   "00000001204baf7f11a7ff12337fc097ac6e82e7b68f82f02c"
                   "c7e24231637c88a91ae5716674acec8a1a305073165c65e520"
                   "a64769f5f62c0301ce21ab4f7c67a6801b4266")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_asset_update(self):
        op = operations.Asset_update(**{
            "fee": {"amount": 0,
                    "asset_id": "1.3.0"},
            "issuer": "1.2.0",
            "asset_to_update": "1.3.0",
            "new_options": {
                "max_supply": "1000000000000000",
                "market_fee_percent": 0,
                "max_market_fee": "1000000000000000",
                "issuer_permissions": 79,
                "flags": 0,
                "core_exchange_rate": {
                    "base": {"amount": 0,
                             "asset_id": "1.3.0"},
                    "quote": {"amount": 0,
                              "asset_id": "1.3.0"}
                },
                "whitelist_authorities": ["1.2.12", "1.2.13"],
                "blacklist_authorities": ["1.2.10", "1.2.11"],
                "whitelist_markets": ["1.3.10", "1.3.11"],
                "blacklist_markets": ["1.3.12", "1.3.13"],
                "description": "Foobar",
                "extensions": []
            },
            "extensions": []
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c80457010b00000000000000000000000000"
                   "80c6a47e8d030000000080c6a47e8d03004f00000000000000"
                   "0000000000000000000000000000020c0d020a0b020a0b020c"
                   "0d06466f6f626172000000011f5bd6a206d210d1d78eb423e0"
                   "c2362013aa80830a8e61e5df2570eac05f1c57a4165c99099f"
                   "c2e97ecbf2b46014c96a6f99cff8d20f55a6042929136055e5"
                   "ad10")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_whitelist(self):
        op = operations.Account_whitelist(**{
            "fee": {"amount": 0,
                    "asset_id": "1.3.0"},
            "authorizing_account": "1.2.0",
            "account_to_list": "1.2.1",
            "new_listing": 0x1,
            "extensions": []
        })
        ops = [Operation(op)]
        tx = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                             ref_block_prefix=ref_block_prefix,
                                             expiration=expiration,
                                             operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c8045701070000000000000000000001010"
                   "000011f14eef2978e40b369273907072dddf4b4043d9f3a08"
                   "da125311c4e6b54b3e7c2a3606594fab7cf6ce381544eceda"
                   "9945c8c9fccebd587cfa2d2f6a146b1639f8c")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_vesting_withdraw(self):
        op = operations.Vesting_balance_withdraw(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "vesting_balance": "1.13.0",
            "owner": "1.2.0",
            "amount": {"amount": 0, "asset_id": "1.3.0"},
            "prefix": "TEST"
        })
        ops = [Operation(op)]
        tx = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                             ref_block_prefix=ref_block_prefix,
                                             expiration=expiration,
                                             operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c80457012100000000000000000000"
                   "0000000000000000000000011f07ae9b0d1cb494e248"
                   "6b99cccdf78ef8b785522af8f2233de364d4455c0626"
                   "935d2d32414a2f7a6b9cdf3451730062965adeec8aa2"
                   "03fca97f608411dce84309")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_upgrade_account(self):
        op = operations.Account_upgrade(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "account_to_upgrade": "1.2.0",
            "upgrade_to_lifetime_member": True,
            "prefix": prefix,
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c804570108000000000000000000000100000"
                   "11f4e42562ada1d3fed8f8eb51dd58117e3a4024959c46955a0"
                   "0d2a7e7e8b40ae7204f4617913aaaf028248d43e8c3463b8776"
                   "0ca569007dba99a2c49de75bd69b3")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_witness_update(self):
        op = operations.Witness_update(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "prefix": "TEST",
            "witness": "1.6.63",
            "witness_account": "1.2.212",
            "new_url": "https://example.com",
            "new_signing_key": "BTS5vfCLKyXYb44znYjbrJXCyvvx3SuifhmvemnQsdbf61EtoR36z"
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c8045701150000000000000000003fd401011"
                   "368747470733a2f2f6578616d706c652e636f6d0102889f66e3"
                   "584423e86b615e3b07593ebec4b1ac0e08ad4a3748f0726dae7"
                   "c874f0001205628a49ef823ab54f4b4c56304f5ac57bdc3768c"
                   "62ac630a92de9858f5d90fad01c43bdc406293edad734d53dca"
                   "a1c96546a50e3ec96d07cf1224ed329177af5")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_feed_producer_update(self):
        op = operations.Asset_update_feed_producers(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "issuer": "1.2.214",
            "asset_to_update": "1.3.132",
            "new_feed_producers": ["1.2.214", "1.2.341", "1.2.2414"],
            "extensions": []
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c80457010d000000000000000000d60184010"
                   "3d601d502ee120000011f34dc3aafe350f3f8608cc3d0db3b64"
                   "a8f40b60d3528c9fa9e88fc3185fc27f4922ef5612f657205ad"
                   "6fc6fed68ec78c4776e1fd125278ab03c8477b37e4c569a")
        self.assertEqual(compare[:-130], txWire[:-130])

    def test_asset_reserve(self):
        op = operations.Asset_reserve(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "payer": "1.2.0",
            "amount_to_reserve": {"amount": 1234567890, "asset_id": "1.3.0"},
            "extensions": []
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(ref_block_num=ref_block_num,
                                ref_block_prefix=ref_block_prefix,
                                expiration=expiration,
                                operations=ops)
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        compare = ("f68585abf4dce7c80457010f00000000000000000000d202964"
                   "900000000000000011f75065cb1155bfcaabaf55d3357d69679"
                   "c7c1fe589b6dc0919fe1dde1a305009c360823a40c28907299a"
                   "40c241db9cad86e27369d0e5a76b5832d585505ff177d")
        self.assertEqual(compare[:-130], txWire[:-130])

    def compareConstructedTX(self):
        #    def test_online(self):
        #        self.maxDiff = None
        op = operations.Asset_reserve(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "payer": "1.2.0",
            "amount_to_reserve": {"amount": 1234567890, "asset_id": "1.3.0"},
            "extensions": []
        })
        ops = [Operation(op)]
        tx = Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops
        )
        tx = tx.sign([wif], chain=prefix)
        tx.verify([PrivateKey(wif).pubkey], "BTS")
        txWire = hexlify(bytes(tx)).decode("ascii")
        print("=" * 80)
        pprint(tx.json())
        print("=" * 80)

        from grapheneapi.grapheneapi import GrapheneAPI
        rpc = GrapheneAPI("localhost", 8092)
        compare = rpc.serialize_transaction(tx.json())
        print(compare[:-130])
        print(txWire[:-130])
        print(txWire[:-130] == compare[:-130])
        self.assertEqual(compare[:-130], txWire[:-130])


if __name__ == '__main__':
    t = Testcases()
    t.compareConstructedTX()
