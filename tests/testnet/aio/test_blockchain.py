# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.blockchain import Blockchain

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)


@pytest.fixture(scope="module")
async def chain(bitshares):
    return await Blockchain(mode="head", blockchain_instance=bitshares)


@pytest.mark.asyncio
async def test_info(chain):
    await chain.info()


@pytest.mark.asyncio
async def test_chainParameters(chain):
    await chain.chainParameters()


@pytest.mark.asyncio
async def test_get_network(chain):
    chain.get_network()


@pytest.mark.asyncio
async def test_get_chain_properties(chain):
    await chain.get_chain_properties()


@pytest.mark.asyncio
async def test_config(chain):
    await chain.config()


@pytest.mark.asyncio
async def test_get_current_block_num(chain):
    await chain.get_current_block_num()


@pytest.mark.asyncio
async def test_get_current_block(chain):
    await chain.get_current_block()


@pytest.mark.asyncio
async def test_get_block_interval(chain):
    await chain.get_block_interval()


@pytest.mark.asyncio
async def test_block_time(chain):
    await chain.block_time(1)


@pytest.mark.asyncio
async def test_block_timestamp(chain):
    await chain.block_timestamp(1)


@pytest.mark.asyncio
async def test_blocks(chain):
    async for block in chain.blocks(start=1, stop=5):
        assert "transactions" in block


@pytest.mark.skip(reason="for internal use, depends on setting self.block_interval")
@pytest.mark.asyncio
async def test_wait_for_and_get_block(chain):
    pass


@pytest.mark.asyncio
async def test_ops(chain):
    async for op in chain.ops(start=1, stop=5):
        assert "op" in op


@pytest.mark.asyncio
async def test_stream(chain):
    async for op in chain.stream(start=1, stop=5):
        assert "type" in op


@pytest.mark.asyncio
async def test_awaitTxConfirmation(bitshares, chain, default_account):
    trx = await bitshares.transfer(
        "init1", 1, "TEST", memo="awaitTxConfirmation", account=default_account
    )
    await chain.awaitTxConfirmation(trx)


@pytest.mark.asyncio
async def test_get_all_accounts(chain):
    with pytest.raises(RuntimeError):
        async for account in chain.get_all_accounts():
            assert account


@pytest.mark.asyncio
async def test_participation_rate(chain):
    rate = await chain.participation_rate
    assert rate > 0
