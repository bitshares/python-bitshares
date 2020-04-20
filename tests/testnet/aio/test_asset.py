# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.asset import Asset
from bitshares.aio.account import Account
from bitshares.aio.amount import Amount
from bitshares.aio.price import Price, PriceFeed
from bitshares.aio.dex import Dex

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.fixture
async def asset(bitshares):
    return await Asset("TEST", blockchain_instance=bitshares)


@pytest.fixture
async def testasset(bitshares, create_asset, unused_asset):
    asset = await unused_asset()
    log.info("Creating asset {}".format(asset))
    await create_asset(asset, 4)
    return await Asset(asset, blockchain_instance=bitshares)


@pytest.fixture(scope="session")
async def bitasset_local(bitshares, base_bitasset, default_account):
    asset = await base_bitasset()
    dex = Dex(blockchain_instance=bitshares)

    # Set initial price feed
    price = await Price(10.0, base=asset, quote=await Asset("TEST"))
    await bitshares.publish_price_feed(asset.symbol, price, account=default_account)

    # Borrow some amount
    to_borrow = await Amount(100, asset)
    await dex.borrow(to_borrow, collateral_ratio=2.1, account=default_account)

    # Drop pricefeed to cause margin call
    price = await Price(7.0, base=asset, quote=await Asset("TEST"))
    await bitshares.publish_price_feed(asset.symbol, price, account=default_account)

    # Settle some
    to_settle = await Amount(5, asset)
    await bitshares.asset_settle(to_settle, account=default_account)

    return asset


@pytest.mark.asyncio
async def test_asset_init(asset):
    assert asset["id"] == "1.3.0"
    copy = asset.copy()
    assert copy["id"] == asset["id"]


@pytest.mark.asyncio
async def test_asset_refresh(asset):
    await asset.ensure_full()
    assert "dynamic_asset_data" in asset
    assert "flags" in asset
    assert "permissions" in asset
    assert isinstance(asset["flags"], dict)
    assert isinstance(asset["permissions"], dict)


@pytest.mark.asyncio
async def test_asset_properties(asset):
    assert isinstance(asset.symbol, str)
    assert isinstance(asset.precision, int)
    assert isinstance(asset.is_bitasset, bool)
    assert isinstance(asset.permissions, dict)
    assert asset.permissions == asset["permissions"]
    assert isinstance(asset.flags, dict)
    assert asset.flags == asset["flags"]


@pytest.mark.asyncio
async def test_max_market_fee(asset):
    await asset.max_market_fee


@pytest.mark.asyncio
async def test_feeds(bitasset):
    asset = bitasset
    feeds = await asset.feeds
    assert isinstance(feeds, list)
    assert len(feeds) > 0
    assert isinstance(feeds[0], PriceFeed)


@pytest.mark.asyncio
async def test_feed(bitasset):
    asset = bitasset
    feed = await asset.feed
    assert isinstance(feed, PriceFeed)


@pytest.mark.asyncio
async def test_get_call_orders(bitasset_local):
    asset = bitasset_local
    call_orders = await asset.get_call_orders()
    assert len(call_orders) > 0
    assert "collateral" in call_orders[0]


@pytest.mark.asyncio
async def test_get_settle_orders(bitasset_local):
    asset = bitasset_local
    settle_orders = await asset.get_settle_orders()
    assert len(settle_orders) > 0
    assert "amount" in settle_orders[0]


@pytest.mark.asyncio
async def test_halt(testasset):
    await testasset.halt()


@pytest.mark.asyncio
async def test_release(testasset, assets):
    await testasset.release(
        whitelist_authorities=["init1"],
        blacklist_authorities=["init2"],
        whitelist_markets=["GOLD"],
        blacklist_markets=["USD"],
    )


@pytest.mark.asyncio
async def test_setoptions(testasset):
    await asyncio.sleep(1.1)
    await testasset.setoptions({"charge_market_fee": True})


@pytest.mark.asyncio
async def test_enableflag(testasset):
    await asyncio.sleep(1.1)
    await testasset.enableflag("charge_market_fee")


@pytest.mark.asyncio
async def test_disableflag(testasset):
    await asyncio.sleep(1.1)
    await testasset.disableflag("charge_market_fee")


@pytest.mark.asyncio
async def test_seize(testasset, issue_asset):
    await asyncio.sleep(1.1)
    await testasset.enableflag("override_authority")
    await issue_asset(testasset.symbol, 1000, "init3")
    a1 = await Account("init3")
    a2 = await Account("init1")
    amount = await Amount("1000", testasset)
    await testasset.seize(a1, a2, amount)


@pytest.mark.asyncio
async def test_add_remove_authorities(testasset):
    await testasset.add_authorities("blacklist", authorities=["init1"])
    await testasset.add_authorities("whitelist", authorities=["init2"])
    await testasset.remove_authorities("blacklist", authorities=["init1"])
    await asyncio.sleep(1.1)
    await testasset.remove_authorities("whitelist", authorities=["init2"])


@pytest.mark.asyncio
async def test_add_remove_markets(testasset, assets):
    await testasset.add_markets("whitelist", ["USD"])
    await asyncio.sleep(1.1)
    await testasset.remove_markets("whitelist", ["USD"])
    await asyncio.sleep(1.1)
    await testasset.add_markets("blacklist", ["GOLD"])
    await asyncio.sleep(1.1)
    await testasset.remove_markets("blacklist", ["GOLD"])


@pytest.mark.asyncio
async def test_set_market_fee(testasset):
    await testasset.set_market_fee(1, 1000)


@pytest.mark.asyncio
async def test_update_feed_producers(base_bitasset, default_account):
    asset = await base_bitasset()
    await asset.update_feed_producers([default_account, "init1", "init2"])


@pytest.mark.asyncio
async def test_change_issuer(testasset):
    await testasset.change_issuer("init1")


@pytest.mark.asyncio
async def test_issue(testasset):
    # Normal invokation
    await testasset.issue(100, "init1")
    # Amount as str
    await testasset.issue("1", "init1")
    # Amount < 1
    await testasset.issue(0.01, "init1")
