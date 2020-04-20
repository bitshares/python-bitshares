# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.dex import Dex
from bitshares.aio.amount import Amount

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.fixture
async def dex(bitshares):
    return Dex(blockchain_instance=bitshares)


@pytest.fixture
async def borrow_some(dex, bitasset, default_account):
    to_borrow = await Amount(1000, bitasset)
    await dex.borrow(to_borrow, collateral_ratio=2.1, account=default_account)
    await asyncio.sleep(1.1)
    return bitasset


@pytest.mark.asyncio
async def test_dex_init(bitshares):
    Dex(blockchain_instance=bitshares)


@pytest.mark.asyncio
async def test_return_fees(dex):
    fees = await dex.returnFees()
    assert isinstance(fees, dict)
    assert "account_create" in fees


@pytest.mark.asyncio
async def test_borrow(borrow_some):
    pass


@pytest.mark.asyncio
async def test_list_debt_positions(dex, borrow_some, default_account):
    asset = borrow_some
    debts = await dex.list_debt_positions(account=default_account)
    assert asset.symbol in debts


@pytest.mark.asyncio
async def test_close_debt_position(dex, borrow_some, default_account):
    asset = borrow_some
    await dex.close_debt_position(asset.symbol, account=default_account)


@pytest.mark.asyncio
async def test_adjust_debt(dex, borrow_some, default_account):
    asset = borrow_some
    delta = await Amount(10, asset)
    await dex.adjust_debt(delta, new_collateral_ratio=2.1, account=default_account)


@pytest.mark.asyncio
async def test_adjust_collateral_ratio(dex, borrow_some, default_account):
    asset = borrow_some
    await dex.adjust_collateral_ratio(asset.symbol, 2.5, account=default_account)
