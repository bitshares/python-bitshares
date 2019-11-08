# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from bitshares.aio.proposal import Proposals

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_aio_chain_props(bitshares):
    """ Test chain properties
    """
    # Wait for several blcocks
    await asyncio.sleep(3)
    props = await bitshares.info()
    assert isinstance(props, dict)
    assert props["head_block_number"] > 0


@pytest.mark.asyncio
async def test_transfer(bitshares, default_account):
    await bitshares.transfer("init1", 10, "TEST", memo="xxx", account=default_account)


@pytest.mark.asyncio
async def test_create_account(bitshares, default_account):
    await bitshares.create_account(
        "foobar", referrer=default_account, registrar=default_account, password="test"
    )


@pytest.mark.asyncio
async def test_upgrade_account(bitshares, default_account, unused_account):
    account = await unused_account()
    await bitshares.create_account(
        account, referrer=default_account, registrar=default_account, password="test"
    )
    await bitshares.transfer(
        account, 10000, "TEST", memo="xxx", account=default_account
    )
    await bitshares.upgrade_account(account=account)


@pytest.mark.asyncio
async def test_allow_disallow(bitshares, default_account):
    await bitshares.allow("init1", account=default_account)
    await asyncio.sleep(1.1)
    await bitshares.disallow("init1", account=default_account)


@pytest.mark.asyncio
async def test_update_memo_key(bitshares, default_account):
    from bitsharesbase.account import PasswordKey

    password = "test"
    memo_key = PasswordKey(default_account, password, role="memo")
    pubkey = memo_key.get_public_key()
    await bitshares.update_memo_key(pubkey, account=default_account)


@pytest.mark.asyncio
async def test_approve_disapprove_witness(bitshares, default_account):
    witnesses = ["init1", "init2"]
    await bitshares.approvewitness(witnesses, account=default_account)
    await asyncio.sleep(1.1)
    await bitshares.disapprovewitness(witnesses, account=default_account)


@pytest.mark.asyncio
async def test_approve_disapprove_committee(bitshares, default_account):
    cm = ["init5", "init6"]
    await bitshares.approvecommittee(cm, account=default_account)
    await asyncio.sleep(1.1)
    await bitshares.disapprovecommittee(cm, account=default_account)


@pytest.mark.asyncio
async def test_approve_proposal(bitshares, default_account):
    parent = bitshares.new_tx()
    proposal = bitshares.new_proposal(parent=parent)
    await bitshares.transfer(
        "init1", 1, "TEST", append_to=proposal, account=default_account
    )
    await proposal.broadcast()
    proposals = await Proposals(default_account)
    assert len(proposals) == 1
    await bitshares.approveproposal(proposals[0]["id"], account=default_account)


@pytest.mark.asyncio
async def test_disapprove_proposal(bitshares, default_account, unused_account):
    # Create child account
    account = await unused_account()
    await bitshares.create_account(
        account, referrer=default_account, registrar=default_account, password="test"
    )
    await bitshares.transfer(account, 100, "TEST", account=default_account)

    # Grant child account access with 1/2 threshold
    await bitshares.allow(account, weight=1, threshold=2, account=default_account)

    # Create proposal
    parent = bitshares.new_tx()
    proposal = bitshares.new_proposal(parent=parent)
    await bitshares.transfer(
        "init1", 1, "TEST", append_to=proposal, account=default_account
    )
    await proposal.broadcast()
    proposals = await Proposals(default_account)
    assert len(proposals) == 1

    # Approve proposal; 1/2 is not sufficient to completely approve, so proposal remains active
    await bitshares.approveproposal(proposals[0]["id"], account=account)
    # Revoke vote
    await bitshares.disapproveproposal(proposals[0]["id"], account=account)
