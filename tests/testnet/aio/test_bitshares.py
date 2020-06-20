# -*- coding: utf-8 -*-
import asyncio
import pytest
import logging

from datetime import datetime
from bitshares.aio.asset import Asset
from bitshares.aio.amount import Amount
from bitshares.aio.account import Account
from bitshares.aio.price import Price
from bitshares.aio.proposal import Proposals
from bitshares.aio.worker import Workers
from bitshares.aio.dex import Dex
from bitshares.aio.market import Market

log = logging.getLogger("grapheneapi")
log.setLevel(logging.DEBUG)


@pytest.fixture(scope="module")
async def testworker(bitshares, default_account):
    amount = await Amount("1000 TEST")
    end = datetime(2099, 1, 1)
    await bitshares.create_worker("test", amount, end, account=default_account)


@pytest.fixture(scope="module")
async def gs_bitasset(bitshares, default_account, base_bitasset):
    """Create globally settled bitasset."""
    asset = await base_bitasset()

    price = await Price(10.0, base=asset, quote=await Asset("TEST"))
    await bitshares.publish_price_feed(asset.symbol, price, account=default_account)
    dex = Dex(blockchain_instance=bitshares)
    to_borrow = await Amount(1000, asset)
    await dex.borrow(to_borrow, collateral_ratio=2.1, account=default_account)
    price = await Price(1.0, base=asset, quote=await Asset("TEST"))
    # Trigger GS
    await bitshares.publish_price_feed(asset.symbol, price, account=default_account)
    return asset


@pytest.fixture(scope="module")
async def ltm_account(bitshares, default_account, unused_account):
    account = await unused_account()
    await bitshares.create_account(
        account, referrer=default_account, registrar=default_account, password="test"
    )
    await bitshares.transfer(
        account, 100000, "TEST", memo="xxx", account=default_account
    )
    await bitshares.upgrade_account(account=account)
    return account


@pytest.mark.asyncio
async def test_aio_chain_props(bitshares):
    """Test chain properties."""
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
async def test_upgrade_account(ltm_account):
    account = await Account(ltm_account)
    assert account.is_ltm


@pytest.mark.asyncio
async def test_allow_disallow(bitshares, default_account):
    await bitshares.allow("init1", account=default_account)
    await asyncio.sleep(1.1)
    await bitshares.disallow("init1", account=default_account)


@pytest.mark.asyncio
async def test_update_memo_key(bitshares, ltm_account, default_account):
    from bitsharesbase.account import PasswordKey

    account = ltm_account
    password = "test2"
    memo_key = PasswordKey(account, password, role="memo")
    pubkey = memo_key.get_public_key()
    await bitshares.update_memo_key(pubkey, account=account)


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
    # Set blocking to get "operation_results"
    bitshares.blocking = "head"
    proposal = bitshares.new_proposal()
    await bitshares.transfer(
        "init1", 1, "TEST", append_to=proposal, account=default_account
    )
    tx = await proposal.broadcast()
    proposal_id = tx["operation_results"][0][1]
    await bitshares.approveproposal(proposal_id, account=default_account)
    bitshares.blocking = None


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
    bitshares.blocking = "head"
    proposal = bitshares.new_proposal()
    await bitshares.transfer(
        "init1", 1, "TEST", append_to=proposal, account=default_account
    )
    tx = await proposal.broadcast()
    proposal_id = tx["operation_results"][0][1]

    # Approve proposal; 1/2 is not sufficient to completely approve, so proposal remains active
    await bitshares.approveproposal(proposal_id, account=account)
    # Revoke vote
    await bitshares.disapproveproposal(proposal_id, account=account)
    bitshares.blocking = None


@pytest.mark.asyncio
async def test_approve_disapprove_worker(bitshares, testworker, default_account):
    workers = await Workers(default_account)
    worker = workers[0]["id"]
    await bitshares.approveworker(worker)
    await bitshares.disapproveworker(worker)


@pytest.mark.asyncio
async def test_set_unset_proxy(bitshares, default_account):
    await bitshares.set_proxy("init1", account=default_account)
    await asyncio.sleep(1.1)
    await bitshares.unset_proxy()


@pytest.mark.skip(reason="cancel() tested indirectly in test_market.py")
@pytest.mark.asyncio
async def test_cancel():
    pass


@pytest.mark.skip(reason="need to provide a way to make non-empty vesting balance")
@pytest.mark.asyncio
async def test_vesting_balance_withdraw(bitshares, default_account):
    balances = await bitshares.rpc.get_vesting_balances(default_account)
    await bitshares.vesting_balance_withdraw(balances[0]["id"], account=default_account)


@pytest.mark.asyncio
async def test_publish_price_feed(bitshares, base_bitasset, default_account):
    asset = await base_bitasset()
    price = await Price(1.1, base=asset, quote=await Asset("TEST"))
    await bitshares.publish_price_feed(asset.symbol, price, account=default_account)


@pytest.mark.asyncio
async def test_update_cer(bitshares, base_bitasset, default_account):
    asset = await base_bitasset()
    price = await Price(1.2, base=asset, quote=await Asset("TEST"))
    await bitshares.update_cer(asset.symbol, price, account=default_account)


@pytest.mark.asyncio
async def test_update_witness(bitshares, default_account):
    await bitshares.update_witness(default_account, url="https://foo.bar/")


@pytest.mark.asyncio
async def test_reserve(bitshares, default_account):
    amount = await Amount("10 TEST")
    await bitshares.reserve(amount, account=default_account)


@pytest.mark.asyncio
async def test_create_asset(bitshares, default_account, bitasset):
    asset = bitasset
    assert asset.is_bitasset


@pytest.mark.asyncio
async def test_create_worker(testworker, default_account):
    w = await Workers(default_account)
    assert len(w) > 0


@pytest.mark.asyncio
async def test_fund_fee_pool(bitshares, default_account, bitasset):
    await bitshares.fund_fee_pool(bitasset.symbol, 100.0, account=default_account)


@pytest.mark.asyncio
async def test_create_committee_member(bitshares, ltm_account):
    await bitshares.create_committee_member(account=ltm_account)


@pytest.mark.asyncio
async def test_account_whitelist(bitshares, default_account):
    await bitshares.account_whitelist("init1", account=default_account)


@pytest.mark.asyncio
async def test_bid_collateral(bitshares, default_account, gs_bitasset):
    asset = gs_bitasset
    additional_collateral = await Amount("1000 TEST")
    debt_covered = await Amount(10, asset)
    await bitshares.bid_collateral(
        additional_collateral, debt_covered, account=default_account
    )


@pytest.mark.asyncio
async def test_asset_settle(bitshares, default_account, bitasset):
    asset = bitasset
    dex = Dex(blockchain_instance=bitshares)
    to_borrow = await Amount(1000, asset)
    await dex.borrow(to_borrow, collateral_ratio=2.1, account=default_account)
    to_settle = await Amount(100, asset)
    await bitshares.asset_settle(to_settle, account=default_account)


@pytest.mark.asyncio
async def test_htlc(bitshares, default_account):
    """Test both htlc_create and htlc_redeem."""
    amount = await Amount("10 TEST")
    bitshares.blocking = "head"
    tx = await bitshares.htlc_create(
        amount, default_account, "foobar", account=default_account
    )
    htlc_id = tx["operation_results"][0][1]
    await bitshares.htlc_redeem(htlc_id, "foobar", account=default_account)
    bitshares.blocking = None


@pytest.mark.asyncio
async def test_subscribe_to_pending_transactions(bitshares, default_account):
    await bitshares.cancel_subscriptions()
    await bitshares.subscribe_to_pending_transactions()

    # Generate an event
    await bitshares.transfer("init1", 10, "TEST", memo="xxx", account=default_account)

    event_correct = False
    for _ in range(0, 6):
        event = await bitshares.notifications.get()
        if event["params"][0] == 0:
            event_correct = True
            break
    assert event_correct


@pytest.mark.asyncio
async def test_subscribe_to_blocks(bitshares):
    await bitshares.cancel_subscriptions()
    await bitshares.subscribe_to_blocks()
    event_correct = False
    for _ in range(0, 6):
        event = await bitshares.notifications.get()
        if event["params"][0] == 2:
            event_correct = True
            break
    assert event_correct


@pytest.mark.asyncio
async def test_subscribe_to_accounts(bitshares, default_account):
    await bitshares.cancel_subscriptions()
    # Subscribe
    await bitshares.subscribe_to_accounts([default_account])

    # Generate an event
    await bitshares.transfer("init1", 10, "TEST", memo="xxx", account=default_account)

    # Check event
    event_correct = False
    for _ in range(0, 6):
        event = await bitshares.notifications.get()
        if event["params"][0] == 1:
            event_correct = True
            break
    assert event_correct


@pytest.mark.asyncio
async def test_subscribe_to_market(bitshares, assets, default_account):
    await bitshares.cancel_subscriptions()
    await asyncio.sleep(1.1)
    market = await Market("TEST/USD")
    await bitshares.subscribe_to_market(market, event_id=4)

    # Generate an event
    await market.sell(1, 1, account=default_account)

    # Check event
    event_correct = False
    for _ in range(0, 10):
        event = await bitshares.notifications.get()
        log.debug("getting event")
        if event["params"][0] == 4:
            event_correct = True
            break
    assert event_correct


@pytest.mark.asyncio
async def test_double_connect(bitshares_testnet):
    from bitshares.aio import BitShares

    bitshares = BitShares(
        node="ws://127.0.0.1:{}".format(bitshares_testnet.service_port), num_retries=-1
    )
    await bitshares.connect()
    await bitshares.connect()
