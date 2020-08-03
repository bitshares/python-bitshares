# -*- coding: utf-8 -*-
from pprint import pprint
from getpass import getpass
from bitshares import BitShares
from bitshares.amount import Amount
from bitshares.account import Account
from bitsharesbase.operations import Vesting_balance_create

bts = BitShares(nobroadcast=False)
bts.unlock(getpass())

creator = Account("foundation")
owner = Account("init0")
amount = Amount("10000000 DNA")

op = Vesting_balance_create(
    **{
        "fee": {"amount": 0, "asset_id": "1.3.0"},
        "creator": creator["id"],
        "owner": owner["id"],
        "amount": amount.json(),
        "policy": [3, {"duration": 60 * 60 * 24 * 365}],
        "extensions": [],
    }
)

pprint(bts.finalizeOp(op, creator, "active"))
