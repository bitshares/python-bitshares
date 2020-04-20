# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitsharesbase.operationids import getOperationNameForId

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_finalizeOps_proposal(bitshares):
    bitshares.clear()
    proposal = bitshares.proposal()
    await bitshares.transfer("init1", 1, "TEST", append_to=proposal)
    tx = await bitshares.tx().json()  # default tx buffer
    ops = tx["operations"]
    assert len(ops) == 1
    assert getOperationNameForId(ops[0][0]) == "proposal_create"
    prop = ops[0][1]
    assert len(prop["proposed_ops"]) == 1
    assert getOperationNameForId(prop["proposed_ops"][0]["op"][0]) == "transfer"


@pytest.mark.asyncio
async def test_finalizeOps_proposal2(bitshares):
    bitshares.clear()
    proposal = bitshares.new_proposal()
    await bitshares.transfer("init1", 2, "TEST", append_to=proposal)
    tx = await bitshares.tx().json()  # default tx buffer
    ops = tx["operations"]
    assert len(ops) == 1
    assert getOperationNameForId(ops[0][0]) == "proposal_create"
    prop = ops[0][1]
    assert len(prop["proposed_ops"]) == 1
    assert getOperationNameForId(prop["proposed_ops"][0]["op"][0]) == "transfer"


@pytest.mark.asyncio
async def test_finalizeOps_combined_proposal(bitshares):
    bitshares.clear()
    parent = bitshares.new_tx()
    proposal = bitshares.new_proposal(parent)
    await bitshares.transfer("init1", 3, "TEST", append_to=proposal)
    await bitshares.transfer("init1", 4, "TEST", append_to=parent)
    tx = await parent.json()
    ops = tx["operations"]
    assert len(ops) == 2
    assert getOperationNameForId(ops[0][0]) == "proposal_create"
    assert getOperationNameForId(ops[1][0]) == "transfer"
    prop = ops[0][1]
    assert len(prop["proposed_ops"]) == 1
    assert getOperationNameForId(prop["proposed_ops"][0]["op"][0]) == "transfer"


@pytest.mark.asyncio
async def test_finalizeOps_changeproposer_new(bitshares):
    bitshares.clear()
    proposal = bitshares.proposal(proposer="init5")
    await bitshares.transfer("init1", 5, "TEST", append_to=proposal)
    tx = await bitshares.tx().json()
    ops = tx["operations"]
    assert len(ops) == 1
    assert getOperationNameForId(ops[0][0]) == "proposal_create"
    prop = ops[0][1]
    assert len(prop["proposed_ops"]) == 1
    assert prop["fee_paying_account"] == "1.2.11"
    assert getOperationNameForId(prop["proposed_ops"][0]["op"][0]) == "transfer"


@pytest.mark.asyncio
async def test_new_proposals(bitshares):
    bitshares.clear()
    p1 = bitshares.new_proposal()
    p2 = bitshares.new_proposal()
    assert id(p1) is not None
    assert id(p2) is not None


@pytest.mark.asyncio
async def test_new_txs(bitshares):
    bitshares.clear()
    p1 = bitshares.new_tx()
    p2 = bitshares.new_tx()
    assert id(p1) is not None
    assert id(p2) is not None
