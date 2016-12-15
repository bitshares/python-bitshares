from grapheneapi.grapheneclient import GrapheneClient
from datetime import datetime
import time

# from graphenebase.transactions import operations


class Proposal(GrapheneClient) :
    """ Manage Proposals

        :param grapheneapi.GrapheneClient grapheneClient: Grapehen
                    Client instance with connection details for RPC
                    *and* websocket connection

    """
    def __init__(self, *args, **kwargs) :
        super(Proposal, self).__init__(*args, **kwargs)

    def approve_available_proposals(self, from_account, approving_account) :
        """ Approve all proposals for a given account with given approver

            :param str from_account: account name to approve *all* proposals for
            :param str approving_account: approving account

        """
        fromAccount        = self.rpc.get_account(from_account)
        approving_account  = self.rpc.get_account(approving_account)
        proposals          = self.rpc.ws.get_proposed_transactions(fromAccount["id"])
        for proposal in proposals :
            if approving_account["id"] in proposal["available_active_approvals"] :
                print("%s: Proposal %s already approved. Expires on %s UTC"  %
                      (fromAccount["name"], proposal['id'], proposal["expiration_time"]))
            else :
                print("%s: Approving Proposal %s ..." %
                      (fromAccount["name"], proposal['id']))
                self.rpc.approve_proposal(approving_account["name"],
                                          proposal["id"],
                                          {"active_approvals_to_add" : [approving_account["name"]]},
                                          True)

    def propose_transfer(self, proposer_account, from_account, to_account,
                         amount, asset, expiration=3600, broadcast=True):
        """ Propose a Transfer Transaction (opid=0)

            :param str proposer_account: Account that proposed the transfer (and pays the proposal fee)
            :param str from_account: Account to transfer from (pays tx fee)
            :param str to_account: Account to transfer to
            :param init amount: Amount to transfer (*not* in satoshi, e.g. 100.112 BTS)
            :param str asset: Symbol or id of the asset to transfer
            :param expiration: Expiration of the proposal (default: 60min)
            :param bool broadcast: Broadcast signed transaction or not

            .. note:: This method requires
                        ``propose_builder_transaction2`` to be available in the
                        cli_wallet

        """
        proposer         = self.rpc.get_account(proposer_account)
        fromAccount      = self.rpc.get_account(from_account)
        toAccount        = self.rpc.get_account(to_account)
        asset            = self.rpc.get_asset(asset)
        op               = self.rpc.get_prototype_operation("transfer_operation")

        op[1]["amount"]["amount"]   = int(amount * 10 ** asset["precision"])
        op[1]["amount"]["asset_id"] = asset["id"]
        op[1]["from"]               = fromAccount["id"]
        op[1]["to"]                 = toAccount["id"]

        exp_time    = datetime.utcfromtimestamp(time.time() + int(expiration)).strftime('%Y-%m-%dT%H:%M:%S')
        buildHandle = self.rpc.begin_builder_transaction()
        self.rpc.add_operation_to_builder_transaction(buildHandle, op)
        self.rpc.set_fees_on_builder_transaction(buildHandle, asset["id"])
        self.rpc.propose_builder_transaction2(buildHandle, proposer["name"], exp_time, 0, False)
        self.rpc.set_fees_on_builder_transaction(buildHandle, asset["id"])
        return self.rpc.sign_builder_transaction(buildHandle, broadcast)

    def propose_operations(self, ops, expiration, proposer_account, preview=0, broadcast=False):
        """ Propose several operations

            :param Array ops: Array of operations
            :param time expiration: Expiration time in format '%Y-%m-%dT%H:%M:%S'
            :param proposer_account: Account name or id of the proposer (pays the proposal fee)
            :param number preview: Preview period (in seconds)
            :param bool broadcast: If true, broadcasts the transaction
            :return: Signed transaction
            :rtype: json

            Once a proposal has been signed, the corresponding
            transaction hash can be obtained via:

            .. code-block:: python

                print(rpc.get_transaction_id(tx))
        """

        proposer         = self.rpc.get_account(proposer_account)
        buildHandle = self.rpc.begin_builder_transaction()
        for op in ops:
            self.rpc.add_operation_to_builder_transaction(buildHandle, op)
        self.rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
        self.rpc.propose_builder_transaction2(buildHandle, proposer["name"], expiration, preview, False)
        self.rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
        return self.rpc.sign_builder_transaction(buildHandle, broadcast)

#         ## Alternative implementation building the transactions
#         ## manually. Not yet working though
#         op = self.rpc.get_prototype_operation("proposal_create_operation")
#         for o in ops :
#             op[1]["proposed_ops"].append(o)
#         op[1]["expiration_time"] = expiration
#         op[1]["fee_paying_account"] = payee_id
#         op[1]["fee"] = self.get_operations_fee(op, "1.3.0")
#         buildHandle = self.rpc.begin_builder_transaction()
#         from pprint import pprint
#         pprint(op)
#         self.rpc.add_operation_to_builder_transaction(buildHandle, op)
#         # print(self.rpc.preview_builder_transaction(buildHandle))
#         return self.rpc.sign_builder_transaction(buildHandle, broadcast)

#     def get_operations_fee(self, op, asset_id):
#         global_parameters = self.rpc.get_object("2.0.0")[0]["parameters"]["current_fees"]
#         parameters = global_parameters["parameters"]
#         scale = global_parameters["scale"] / 1e4
#         opID = op[0]
#         assert asset_id == "1.3.0", "asset_id has to be '1.3.0'"
#         # FIXME limition to "fee"-only! Need to evaluate every other as well
#         return {"amount": parameters[opID][1]["fee"],
#                 "asset_id": asset_id}
