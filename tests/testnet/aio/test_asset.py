# -*- coding: utf-8 -*-
import pytest
import logging

from bitshares.aio.asset import Asset

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_asset(bitshares):
    asset = await Asset("CNY", blockchain_instance=bitshares)
    assert asset["id"] == "1.3.113"
    copy = asset.copy()
    assert copy["id"] == asset["id"]
