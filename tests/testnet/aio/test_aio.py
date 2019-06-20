# -*- coding: utf-8 -*-
import pytest
import asyncio
import logging

from bitshares.aio.bitshares import BitShares
from bitshares.aio.asset import Asset
from bitshares.aio.amount import Amount
from bitshares.aio.block import Block

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_chain_props(bitshares):
    """ Test chain properties
    """
    props = await bitshares.info()
    assert isinstance(props, dict)
    assert props["head_block_number"] > 0


@pytest.mark.asyncio
async def test_aio_asset(bitshares):
    asset = await Asset("CNY", blockchain_instance=bitshares)
    assert asset["id"] == "1.3.113"
    copy = asset.copy()
    assert copy["id"] == asset["id"]


@pytest.mark.asyncio
async def test_aio_amount(bitshares):
    amount = await Amount("10 CNY", blockchain_instance=bitshares)
    assert amount["amount"] == 10
    copied = amount.copy()
    assert amount["amount"] == copied["amount"]


@pytest.mark.asyncio
async def test_aio_block(bitshares):
    block = await Block(333, blockchain_instance=bitshares)
    assert block["witness"] == "1.6.6"
    # Tests __contains__
    assert "witness" in block
