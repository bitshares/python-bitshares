# -*- coding: utf-8 -*-
import asyncio
import pytest

from bitshares.aio import BitShares
from bitshares.aio.instance import set_shared_bitshares_instance
from bitshares.aio.genesisbalance import GenesisBalance
from bitshares.aio.asset import Asset


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def bitshares_instance(bitshares_testnet, private_keys, event_loop):
    """ Initialize BitShares instance connected to a local testnet
    """
    bitshares = BitShares(
        node="ws://127.0.0.1:{}".format(bitshares_testnet.service_port),
        keys=private_keys,
        num_retries=-1,
        loop=event_loop,
    )
    await bitshares.connect()
    # Shared instance allows to avoid any bugs when bitshares_instance is not passed explicitly when instantiating
    # objects
    set_shared_bitshares_instance(bitshares)
    # Todo: show chain params when connectiong to unknown network
    # https://github.com/bitshares/python-bitshares/issues/221

    yield bitshares


@pytest.fixture(scope="session")
async def claim_balance(bitshares_instance, default_account):
    """ Transfer balance from genesis into actual account
    """
    genesis_balance = await GenesisBalance(
        "1.15.0", bitshares_instance=bitshares_instance
    )
    await genesis_balance.claim(account=default_account)


@pytest.fixture(scope="session")
def bitshares(bitshares_instance, claim_balance):
    """ Prepare the testnet and return BitShares instance
    """
    return bitshares_instance


@pytest.fixture(scope="session")
async def create_asset(bitshares, default_account):
    """ Create a new asset
    """

    async def _create_asset(asset, precision):
        max_supply = (
            1000000000000000 / 10 ** precision if precision > 0 else 1000000000000000
        )
        await bitshares.create_asset(
            asset, precision, max_supply, account=default_account
        )

    return _create_asset


@pytest.fixture(scope="session")
async def issue_asset(bitshares):
    """ Issue asset shares to specified account

        :param str asset: asset symbol to issue
        :param float amount: amount to issue
        :param str to: account name to receive new shares
    """

    async def _issue_asset(asset, amount, to):
        asset = await Asset(asset, bitshares_instance=bitshares)
        await asset.issue(amount, to)

    return _issue_asset


@pytest.fixture(scope="session")
async def assets(create_asset, issue_asset, default_account):
    await create_asset("USD", 3)
    await create_asset("GOLD", 3)
    await issue_asset("USD", 1000, default_account)
