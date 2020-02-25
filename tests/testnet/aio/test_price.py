# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.asset import Asset
from bitshares.aio.amount import Amount
from bitshares.aio.account import Account
from bitshares.aio.price import Price, Order, FilledOrder
from bitshares.aio.market import Market

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.fixture
async def market(bitshares, assets):
    return await Market("USD:TEST", blockchain_instance=bitshares)


@pytest.fixture
async def do_trade(market, default_account):
    # Small sleep is needed to prevent trx dups when running multiple tests
    await asyncio.sleep(1.1)
    await market.buy(1, 1, account=default_account)
    await market.sell(0.99, 1, account=default_account)


@pytest.mark.asyncio
async def test_price_init(bitshares, assets):
    await Price("0.315 USD/TEST")
    await Price(1.0, "USD/GOLD")
    await Price(0.315, base="USD", quote="TEST")
    await Price(0.315, base=await Asset("USD"), quote=await Asset("TEST"))
    a = await Asset("USD")
    await Price(
        {
            "base": {"amount": 1, "asset_id": "1.3.0"},
            "quote": {"amount": 10, "asset_id": a["id"]},
        }
    )
    await Price(
        {
            "receives": {"amount": 1, "asset_id": "1.3.0"},
            "pays": {"amount": 10, "asset_id": a["id"]},
        },
        base_asset=await Asset("1.3.0"),
    )
    await Price(quote="10 GOLD", base="1 USD")
    await Price("10 GOLD", "1 USD")
    await Price(await Amount("10 GOLD"), await Amount("1 USD"))


@pytest.mark.asyncio
async def test_order_repr(bitshares, default_account, market):
    # Load from id
    await asyncio.sleep(1.1)
    tx = await market.buy(1, 1, account=default_account, returnOrderId="head")
    order = await Order(tx["orderid"])
    log.info("Order from id: {}".format(order))

    # Load from raw object 1.7.x
    result = await bitshares.rpc.get_objects([tx["orderid"]])
    order = await Order(result[0])
    log.info("Order from object 1.7.x: {}".format(order))

    # Load from an operation
    trx = await market.buy(1, 1, account=default_account)
    order = await Order(trx["operations"][0][1])
    log.info("Order from an operation: {}".format(order))


@pytest.mark.asyncio
async def test_filled_order(default_account, do_trade):
    # Sleep needed to wait for order appear in history
    await asyncio.sleep(5)
    a = await Account(default_account)
    history = a.history(only_ops=["fill_order"])
    trades = [entry async for entry in history]
    assert len(trades) > 0
    trade = trades[0]["op"][1]
    order = await FilledOrder(trade)
    # Test __repr__
    log.info("Order from history: {}".format(order))
    # Test copy()
    await order.copy()
