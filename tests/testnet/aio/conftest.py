# -*- coding: utf-8 -*-
import pytest

from bitshares.aio import BitShares
from bitshares.aio.instance import set_shared_bitshares_instance


@pytest.fixture
async def bitshares(bitshares_testnet, private_keys, event_loop):
    """ Initialize BitShares instance connected to a local testnet
    """
    bitshares = BitShares(
        node="ws://127.0.0.1:{}".format(bitshares_testnet.service_port),
        keys=private_keys,
        num_retries=-1,
        loop=event_loop,
    )
    await bitshares.connect()
    # Shared instance allows to avoid any bugs when bitshares_instance is not passed explicitly when instantiating
    # objects
    set_shared_bitshares_instance(bitshares)
    # Todo: show chain params when connectiong to unknown network
    # https://github.com/bitshares/python-bitshares/issues/221

    yield bitshares
    # TODO: is this needed?
    await bitshares.rpc.disconnect()
