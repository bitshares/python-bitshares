# -*- coding: utf-8 -*-
import pytest
import logging
import asyncio

from bitshares.aio.asset import Asset
from bitshares.aio.amount import Amount
from bitshares.aio.account import Account
from bitshares.aio.price import Price, Order
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


@pytest.fixture
async def cancel_all_orders(market):
    async def func(account):
        a = await Account(account)
        orders = [order["id"] for order in await a.openorders if "id" in order]
        await market.cancel(orders, account=account)
        await asyncio.sleep(1.1)

    return func


@pytest.fixture
async def place_order(market, default_account, cancel_all_orders):
    await asyncio.sleep(1.1)
    await market.buy(1, 1, account=default_account)
    await market.sell(10, 1, account=default_account)
    yield
    await cancel_all_orders(default_account)


@pytest.mark.asyncio
async def test_market_init(market):
    assert market.get("base")
    assert market.get("quote")


@pytest.mark.asyncio
async def test_market_ticker(market):
    t = await market.ticker()
    assert "lowestAsk" in t
    assert "highestBid" in t


@pytest.mark.asyncio
async def test_volume24h(market, do_trade):
    await asyncio.sleep(5)
    volume = await market.volume24h()
    assert market["base"]["symbol"] in volume
    assert market["quote"]["symbol"] in volume
    assert volume[market["base"]["symbol"]] > 0
    assert volume[market["quote"]["symbol"]] > 0


@pytest.mark.asyncio
async def test_orderbook(market, place_order):
    orderbook = await market.orderbook()
    assert "bids" in orderbook
    assert "asks" in orderbook
    assert len(orderbook["bids"]) > 0


@pytest.mark.asyncio
async def test_get_limit_orders(market, place_order):
    orderbook = await market.get_limit_orders()
    assert len(orderbook) > 0
    assert isinstance(orderbook[0], Order)


@pytest.mark.asyncio
async def test_trades(market, do_trade):
    trades = [trade async for trade in market.trades()]
    assert len(trades) > 0


@pytest.mark.asyncio
async def test_accounttrades(market, do_trade, default_account):
    trades = await market.accounttrades(account=default_account)
    assert len(trades) > 0


@pytest.mark.asyncio
async def test_accountopenorders(market, default_account, place_order):
    orders = await market.accountopenorders(account=default_account)
    assert len(orders) > 0


@pytest.mark.asyncio
async def test_buy(market, default_account, cancel_all_orders):
    await asyncio.sleep(1.1)
    await market.buy(1, 1, account=default_account)
    await cancel_all_orders(default_account)


@pytest.mark.asyncio
async def test_sell(market, default_account, cancel_all_orders):
    await asyncio.sleep(1.1)
    await market.sell(1, 1, account=default_account)
    await cancel_all_orders(default_account)


@pytest.mark.asyncio
async def test_cancel(market, default_account):
    orders = await market.accountopenorders(account=default_account)
    num_orders_before = len(orders)
    await asyncio.sleep(1.1)
    tx = await market.buy(1, 1, account=default_account, returnOrderId="head")
    await market.cancel(tx["orderid"], account=default_account)
    orders = await market.accountopenorders(account=default_account)
    num_orders_after = len(orders)
    assert num_orders_before == num_orders_after


@pytest.mark.asyncio
async def test_core_quote_market(bitshares, assets, bitasset):
    market = await Market(
        "{}:USD".format(bitasset.symbol), blockchain_instance=bitshares
    )
    await market.core_quote_market()


@pytest.mark.asyncio
async def test_core_base_market(bitshares, assets, bitasset):
    market = await Market(
        "USD:{}".format(bitasset.symbol), blockchain_instance=bitshares
    )
    await market.core_base_market()
