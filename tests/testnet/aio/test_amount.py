# -*- coding: utf-8 -*-
import pytest
import logging

from bitshares.aio.amount import Amount

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_amount_init(bitshares, assets):
    amount = await Amount("10 USD", blockchain_instance=bitshares)
    assert amount["amount"] == 10
    copied = await amount.copy()
    assert amount["amount"] == copied["amount"]
