# -*- coding: utf-8 -*-
import pytest
import logging

from bitshares.aio.asset import Asset

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_asset_init(bitshares):
    asset = await Asset("TEST", blockchain_instance=bitshares)
    assert asset["id"] == "1.3.0"
    copy = asset.copy()
    assert copy["id"] == asset["id"]
