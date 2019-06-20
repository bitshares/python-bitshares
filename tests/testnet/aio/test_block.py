# -*- coding: utf-8 -*-
import pytest
import logging

from bitshares.aio.block import Block

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_block(bitshares):
    block = await Block(333, blockchain_instance=bitshares)
    assert block["witness"] == "1.6.6"
    # Tests __contains__
    assert "witness" in block
