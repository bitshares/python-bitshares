# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.message import Message

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_sign_message(bitshares, default_account):
    message = await Message("message foobar", blockchain_instance=bitshares)
    p = await message.sign(account=default_account)
    m = await Message(p, blockchain_instance=bitshares)
    await m.verify()
