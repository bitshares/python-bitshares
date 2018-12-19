# -*- coding: utf-8 -*-
import os
import yaml

from bitshares import BitShares, storage
from bitshares.instance import set_shared_blockchain_instance
from bitshares.blockchainobject import BlockchainObject, ObjectCache
from bitshares.asset import Asset
from bitshares.account import Account
from bitshares.proposal import Proposals

from bitsharesbase.operationids import operations

# Configuration for unit tests
config = storage.InRamConfigurationStore()
config["node"] = "wss://node.bitshares.eu"

# default wifs key for testing
wifs = [
    "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3",
    "5KCBDTcyDqzsqehcb52tW5nU6pXife6V2rX9Yf7c3saYSzbDZ5W",
]
wif = wifs[0]

# bitshares instance
bitshares = BitShares(
    keys=wifs,
    nobroadcast=True,
    num_retries=1,
    config_store=config,
    key_store=storage.InRamPlainKeyStore(),
)

# Set defaults
bitshares.set_default_account("init0")
set_shared_blockchain_instance(bitshares)

# Ensure we are not going to transaction anythin on chain!
assert bitshares.nobroadcast

# Setup custom Cache
BlockchainObject._cache = ObjectCache(default_expiration=60 * 60 * 1, no_overwrite=True)


def add_to_object_cache(objects, key="id"):
    if objects:
        for i in objects:
            if key in i and i[key]:
                BlockchainObject._cache[i[key]] = i


def fixture_data():
    # Clear tx buffer
    bitshares.clear()

    with open(os.path.join(os.path.dirname(__file__), "fixtures.yaml")) as fid:
        data = yaml.safe_load(fid)
    for ob in data.keys():
        add_to_object_cache(data[ob])

    for account in data.get("accounts"):
        Account._cache[account["id"]] = account
        Account._cache[account["name"]] = account

    for asset in data.get("assets"):
        Asset._cache[asset["symbol"]] = asset
        Asset._cache[asset["id"]] = asset

    for proposal in data.get("proposals", []):
        # id = proposal["required_active_approvals"][0]
        id = "1.2.1"
        ops = list()
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

        if id not in Proposals.cache or not Proposals.cache[id]:
            Proposals.cache[id] = []
        Proposals.cache[id].append(proposal_data)
        # Also define the actual object in the Object Cache
        BlockchainObject._cache[proposal_id] = proposal_data
