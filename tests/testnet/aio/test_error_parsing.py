# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from grapheneapi.exceptions import RPCError

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_parse_error(bitshares, default_account):
    with pytest.raises(RPCError, match="Invalid JSON message"):
        await bitshares.transfer(
            "init1", 99999999999999999, "TEST", memo="xxx", account=default_account
        )
    bitshares.txbuffer.clear()


@pytest.mark.asyncio
async def test_assert_error(bitshares, default_account, assets):
    from bitshares.aio.market import Market

    m = await Market("TEST/GOLD")
    with pytest.raises(RPCError, match="insufficient balance"):
        await m.buy(1, 1, account=default_account)
    bitshares.txbuffer.clear()
