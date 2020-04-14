# -*- coding: utf-8 -*-
import pytest
import logging

from bitshares.aio.asset import Asset
from bitshares.aio.account import Account

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_wallet_key(bitshares, default_account):
    """Check whether wallet contains key for default account."""
    a = await Account(default_account, blockchain_instance=bitshares)
    assert a["id"] in await bitshares.wallet.getAccounts()
