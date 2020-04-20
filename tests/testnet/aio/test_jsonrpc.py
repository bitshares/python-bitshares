# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.asset import Asset

logger = logging.getLogger("websockets")
logger.setLevel(logging.DEBUG)

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_parallel_queries(event_loop, bitshares, assets):
    """When performing multiple calls at once from different coroutines, responses
    should correctly match with queries."""

    async def get_asset(asset):
        a = await Asset(asset, blockchain_instance=bitshares)
        assert a["symbol"] == asset

    async def get_info():
        await bitshares.info()

    for _ in range(0, 40):
        tasks = []
        tasks.append(asyncio.ensure_future(get_asset("USD")))
        tasks.append(asyncio.ensure_future(get_asset("GOLD")))
        tasks.append(asyncio.ensure_future(get_info()))
        await asyncio.gather(*tasks)
