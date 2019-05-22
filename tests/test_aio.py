# -*- coding: utf-8 -*-
import pytest
import asyncio
import logging

from bitshares.aio.bitshares import BitShares
from bitshares.aio.asset import Asset
from bitshares.aio.block import Block

NODE_WS = "wss://eu.nodes.bitshares.ws"


@pytest.mark.asyncio
async def test_aio_chain(event_loop):
    chain = BitShares(node=NODE_WS, loop=event_loop)
    props = await chain.info()
    await chain.rpc.disconnect()
    assert isinstance(props, dict)
    assert props["head_block_number"] > 0


@pytest.mark.asyncio
async def test_aio_asset(event_loop):
    asset = await Asset("CNY", lazy=False, loop=event_loop)
    assert asset["id"] == "1.3.113"


@pytest.mark.asyncio
async def test_aio_block(event_loop):
    block = await Block(333, loop=event_loop)
    assert block["witness"] == "1.6.6"
    # Tests __contains__
    assert "witness" in block
