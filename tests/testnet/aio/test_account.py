# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.account import Account
from bitshares.aio.market import Market
from bitshares.aio.dex import Dex
from bitshares.aio.amount import Amount

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


@pytest.mark.asyncio
async def test_callpositions(bitshares, bitasset, account, default_account):
    asset = bitasset
    dex = Dex(blockchain_instance=bitshares)
    to_borrow = await Amount(1000, asset)
    await dex.borrow(to_borrow, collateral_ratio=2.1, account=default_account)
    res = await account.callpositions
    assert asset.symbol in res


@pytest.mark.asyncio
async def test_openorders(account, place_order):
    orders = await account.openorders
    assert len(orders) > 0
