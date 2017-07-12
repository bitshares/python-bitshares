from .account import PublicKey
from .chains import known_chains
from .signedtransactions import Signed_Transaction
from .operations import (
    Transfer,
    Asset_publish_feed,
    Asset_update,
    Op_wrapper,
    Proposal_create,
    Proposal_update,
    Limit_order_create,
    Limit_order_cancel,
    Call_order_update,
    Asset_fund_fee_pool,
    Override_transfer,
    Account_create,
)
from .objects import Asset
from graphenebase.transactions import getBlockParams, formatTimeFromNow, timeformat


def addRequiredFees(ws, ops, asset_id="1.3.0"):
    """ Auxiliary method to obtain the required fees for a set of
        operations. Requires a websocket connection to a witness node!
    """
    fees = ws.get_required_fees([i.json() for i in ops], asset_id)
    for i, d in enumerate(ops):
        if isinstance(fees[i], list):
            # Operation is a proposal
            ops[i].op.data["fee"] = Asset(
                amount=fees[i][0]["amount"],
                asset_id=fees[i][0]["asset_id"]
            )
            for j, _ in enumerate(ops[i].op.data["proposed_ops"].data):
                ops[i].op.data["proposed_ops"].data[j].data["op"].op.data["fee"] = (
                    Asset(
                        amount=fees[i][1][j]["amount"],
                        asset_id=fees[i][1][j]["asset_id"]))
        else:
            # Operation is a regular operation
            ops[i].op.data["fee"] = Asset(
                amount=fees[i]["amount"],
                asset_id=fees[i]["asset_id"]
            )
    return ops
