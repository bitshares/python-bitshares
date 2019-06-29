# -*- coding: utf-8 -*-
import pytest
import logging

from bitshares.aio.asset import Asset
from bitshares.aio.amount import Amount
from bitshares.aio.price import Price
from bitshares.aio.market import Market

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.fixture
async def market(bitshares, assets):
    return await Market("USD:TEST", blockchain_instance=bitshares)


@pytest.mark.asyncio
async def test_market_init(market):
    assert market.get("base")
    assert market.get("quote")


@pytest.mark.asyncio
async def test_market_ticker(market):
    t = await market.ticker()
    assert "lowestAsk" in t
    assert "highestBid" in t
