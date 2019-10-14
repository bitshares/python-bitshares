# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.account import Account
from bitshares.aio.market import Market

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.fixture
async def market(bitshares, assets):
    return await Market("USD:TEST", blockchain_instance=bitshares)


@pytest.fixture
async def place_order(market, default_account):
    await asyncio.sleep(1.1)
    await market.buy(1, 1, account=default_account)


@pytest.fixture
async def account(default_account):
    return await Account(default_account)


@pytest.mark.skip
@pytest.mark.asyncio
async def test_callpositions(account):
    pass


@pytest.mark.asyncio
async def test_openorders(account, place_order):
    orders = await account.openorders
    assert len(orders) > 0
