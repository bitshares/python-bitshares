# -*- coding: utf-8 -*-
import uuid
import docker
import os.path
import pytest
import socket
import random

from bitshares import BitShares
from bitshares.instance import set_shared_bitshares_instance
from bitshares.genesisbalance import GenesisBalance
from bitshares.asset import Asset

from bitsharesbase.chains import known_chains

# Note: chain_id is generated from genesis.json, every time it's changes you need to get
# new chain_id from `bitshares.rpc.get_chain_properties()`
known_chains["TEST"][
    "chain_id"
] = "569cba9a00ee6e807a62389ea67de7c6954835390be62371709ec804c6bfe1f2"


@pytest.fixture(scope="session")
def private_keys():
    return ["5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"]


@pytest.fixture(scope="session")
def default_account():
    return "init0"


@pytest.fixture(scope="session")
def session_id():
    """
    Generate unique session id.

    This is needed in case testsuite may run in parallel on the same server, for example
    if CI/CD is being used. CI/CD infrastructure may run tests for each commit, so these
    tests should not influence each other.
    """
    return str(uuid.uuid4())


@pytest.fixture(scope="session")
def unused_port():
    """Obtain unused port to bind some service."""

    def _unused_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    return _unused_port


@pytest.fixture(scope="session")
def docker_manager():
    """Initialize docker management client."""
    return docker.from_env(version="auto")


@pytest.fixture(scope="session")
def bitshares_testnet(session_id, unused_port, docker_manager):
    """
    Run bitshares-core inside local docker container.

    Manual run example: $ docker run --name bitshares -p
    0.0.0.0:8091:8091 -v `pwd`/cfg:/etc/bitshares/ bitshares/bitshares-
    core:testnet
    """
    port = unused_port()
    container = docker_manager.containers.run(
        image="bitshares/bitshares-core:testnet",
        name="bitshares-testnet-{}".format(session_id),
        ports={"8091": port},
        volumes={
            "{}/tests/testnet/node_config".format(os.path.abspath(".")): {
                "bind": "/etc/bitshares/",
                "mode": "ro",
            },
            "{}/tests/testnet/node_config/logging.ini".format(os.path.abspath(".")): {
                "bind": "/var/lib/bitshares/logging.ini",
                "mode": "ro",
            },
        },
        detach=True,
    )
    container.service_port = port
    yield container
    container.remove(v=True, force=True)


@pytest.fixture(scope="session")
def bitshares_instance(bitshares_testnet, private_keys):
    """Initialize BitShares instance connected to a local testnet."""
    bitshares = BitShares(
        node="ws://127.0.0.1:{}".format(bitshares_testnet.service_port),
        keys=private_keys,
        num_retries=-1,
    )
    # Shared instance allows to avoid any bugs when bitshares_instance is not passed
    # explicitly when instantiating objects. Todo: remove this
    set_shared_bitshares_instance(bitshares)

    return bitshares


@pytest.fixture(scope="session")
def claim_balance(bitshares_instance, default_account):
    """Transfer balance from genesis into actual account."""
    genesis_balance = GenesisBalance("1.15.0", bitshares_instance=bitshares_instance)
    genesis_balance.claim(account=default_account)


@pytest.fixture(scope="session")
def bitshares(bitshares_instance, claim_balance):
    """Prepare the testnet and return BitShares instance."""
    return bitshares_instance


@pytest.fixture(scope="session")
def create_asset(bitshares, default_account):
    """Create a new asset."""

    def _create_asset(asset, precision):
        max_supply = (
            1000000000000000 / 10 ** precision if precision > 0 else 1000000000000000
        )
        bitshares.create_asset(asset, precision, max_supply, account=default_account)

    return _create_asset


@pytest.fixture(scope="session")
def issue_asset(bitshares):
    """
    Issue asset shares to specified account.

    :param str asset: asset symbol to issue
    :param float amount: amount to issue
    :param str to: account name to receive new shares
    """

    def _issue_asset(asset, amount, to):
        asset = Asset(asset, bitshares_instance=bitshares)
        asset.issue(amount, to)

    return _issue_asset
