# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.dex import Dex

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.fixture
async def dex(bitshares):
    return Dex(blockchain_instance=bitshares)


@pytest.mark.asyncio
async def test_dex_init(bitshares):
    Dex(blockchain_instance=bitshares)


@pytest.mark.asyncio
async def test_return_fees(dex):
    fees = await dex.returnFees()
    assert isinstance(fees, dict)
    assert "account_create" in fees


@pytest.mark.skip
@pytest.mark.asyncio
async def test_list_debt_positions(dex):
    # TODO
    pass


@pytest.mark.skip
@pytest.mark.asyncio
async def test_close_debt_position(dex):
    pass


@pytest.mark.skip
@pytest.mark.asyncio
async def test_adjust_debt(dex):
    pass


@pytest.mark.skip
@pytest.mark.asyncio
async def test_adjust_collateral_ratio(dex):
    pass


@pytest.mark.skip
@pytest.mark.asyncio
async def test_borrow(dex):
    pass
