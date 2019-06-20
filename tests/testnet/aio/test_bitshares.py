# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_chain_props(bitshares):
    """ Test chain properties
    """
    # Wait for several blcocks
    await asyncio.sleep(3)
    props = await bitshares.info()
    assert isinstance(props, dict)
    assert props["head_block_number"] > 0
