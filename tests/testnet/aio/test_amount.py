# -*- coding: utf-8 -*-
import pytest
import logging

from bitshares.aio.amount import Amount

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_amount(bitshares):
    amount = await Amount("10 CNY", blockchain_instance=bitshares)
    assert amount["amount"] == 10
    copied = amount.copy()
    assert amount["amount"] == copied["amount"]
