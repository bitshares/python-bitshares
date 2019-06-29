# -*- coding: utf-8 -*-
import pytest
import logging

from bitshares.aio.asset import Asset
from bitshares.aio.amount import Amount
from bitshares.aio.price import Price

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.fixture(scope="session")
async def assets(create_asset):
    await create_asset("USD", 3)
    await create_asset("GOLD", 3)


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
async def test_order_repr(bitshares, assets):
    pass
    # Test from object 1.7.x

    # place order
    # get order op from history
    # init Price
    # test repr
