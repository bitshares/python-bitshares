# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_parse_error(bitshares, default_account):
    await bitshares.transfer(
        "init1", 99999999999999999, "TEST", memo="xxx", account=default_account
    )


@pytest.mark.asyncio
async def test_assert_error(bitshares, default_account, assets):
    from bitshares.aio.market import Market

    m = await Market("TEST/GOLD")
    await m.buy(1, 1, account=default_account)
