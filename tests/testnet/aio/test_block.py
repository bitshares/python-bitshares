# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.block import Block

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_block(bitshares):
    # Wait for block
    await asyncio.sleep(1)
    block = await Block(1, blockchain_instance=bitshares)
    assert block["witness"].startswith("1.6.")
    # Tests __contains__
    assert "witness" in block
