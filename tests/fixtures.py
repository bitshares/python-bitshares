# -*- coding: utf-8 -*-
import os
import yaml

from pprint import pprint

from bitshares import BitShares, storage
from bitshares.instance import set_shared_blockchain_instance
from bitshares.blockchainobject import BlockchainObject, ObjectCache
from bitshares.asset import Asset
from bitshares.account import Account
from bitshares.proposal import Proposals, Proposal

from bitsharesbase.operationids import operations

# default wifs key for testing
wifs = [
    "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3",
    "5KCBDTcyDqzsqehcb52tW5nU6pXife6V2rX9Yf7c3saYSzbDZ5W",
]
wif = wifs[0]

# bitshares instance
bitshares = BitShares("ws://localhost:8090", keys=wifs, nobroadcast=True, num_retries=1)
config = bitshares.config

# Set defaults
bitshares.set_default_account("init0")
set_shared_blockchain_instance(bitshares)

# Ensure we are not going to transaction anythin on chain!
assert bitshares.nobroadcast


def fixture_data():
    # Clear tx buffer
    bitshares.clear()

    Account.clear_cache()

    with open(os.path.join(os.path.dirname(__file__), "fixtures.yaml")) as fid:
        data = yaml.safe_load(fid)

    for account in data.get("accounts"):
        Account.cache_object(account, account["id"])
        Account.cache_object(account, account["name"])

    for asset in data.get("assets"):
        Asset.cache_object(asset, asset["symbol"])
        Asset.cache_object(asset, asset["id"])

    proposals = []
    for proposal in data.get("proposals", []):
        ops = []
        for _op in proposal["operations"]:
            for opName, op in _op.items():
                ops.append([operations[opName], op])
        # Proposal!
        proposal_id = proposal["proposal_id"]
        proposal_data = {
            "available_active_approvals": [],
            "available_key_approvals": [],
            "available_owner_approvals": [],
            "expiration_time": "2018-05-29T10:23:13",
            "id": proposal_id,
            "proposed_transaction": {
                "expiration": "2018-05-29T10:23:13",
                "extensions": [],
                "operations": ops,
                "ref_block_num": 0,
                "ref_block_prefix": 0,
            },
            "proposer": "1.2.7",
            "required_active_approvals": ["1.2.1"],
            "required_owner_approvals": [],
        }
        proposals.append(Proposal(proposal_data))

    Proposals.cache_objects(proposals, "1.2.1")
    Proposals.cache_objects(proposals, "witness-account")
