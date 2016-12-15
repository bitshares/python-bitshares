Howto Interface your Exchange with Graphene (Quick-Guide)
=========================================================

.. note:: This tutorial gives a very quick introduction on how to interface
          your exchange with graphene. For a more detailed explanation please see 
          :doc:`howto-exchanges-detailed`
          

Network and Client Configuration
--------------------------------

Overview of the Setup
-------------------------------

In the following, we will setup and use the following network:::

    P2P network <-> Trusted Full Node <-> Delayed Full Node <-> API

* Trusted Full Node:
  We will use a Full node to connect to the network directly. We call it
  *trusted* since it is supposed to be under our control.
* Delayed Full Node:
  The delayed full node node will provide us with a delayed and several times
  confirmed and verified blockchain.

Trusted Full Node
_________________

For the trusted full node, the default settings can be used.  For later, we
will need to open the RPC port and listen to an IP address to connect the
delayed full node to.::

    ./programs/witness_node/witness_node --rpc-endpoint="<internal-trusted-node-ip>:8090"

.. note:: A *witness* node is identical to a full node if no authorized
          block-signing private key is provided.

Delayed Full Node
_________________

Setup a delayed node with `10` blocks delay (number of confirmations) and
connect to the trusted node:::

    ./programs/delayed_node/delayed_node --trusted-node="<internal-trusted-node-ip>:8090" --delay-block-count=10 --rpc-endpoint="<local-ip>:8090"

Hence,

* `<internal-trusted-node-ip>:8090` : The trusted full node exposed to the internet
* `<local-ip>:8090` : The delayed full node not exposed to the internet

.. note:: For security reasons, an exchange should only interface with the delayed
          full node.

Monitoring Example Script
--------------------------

As an example, we can have notifications for all incoming transactions for any
account. The monitoring script located in `examples/monitor.py` is discussed in
more details in :doc:`howto-exchanges-detailed`.

All we need to define are the `accountID` and the `memo_wif_key`. The
accountID can be obtained from the GUI wallet, or by issuing:::

    get_account <accountname>

This command also exposes the memo *public key*. The corresponding *private key* can be extracted from:::

   dump_private_keys

If the monitoring script exists abnormally, you can continue operations by
setting `last_op` to the last operation id that you have captured before the
abnormal exit.

.. note:: The current implementation has a maxium history size of 100
          transaction. If you have missed more than 100 transaction with the
          current implementation, manual fixing is required.

.. code-block:: python

    import sys
    import json
    from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
    from graphenebase import Memo, PrivateKey, PublicKey

    """ RPC connection settings """
    host     = "localhost"
    port     = 8090
    user     = ""
    password = ""

    """ Account id to monitor """
    accountID = "2.6.69585"

    """ Memo Key of the receiving account """
    memo_wif_key = "<wif-key>"

    """ Last operation ID that you have registered in your backend """
    last_op = "1.11.0"

    """ PubKey Prefix
        Productive network: BTS
        Testnetwork: GPH """
    #prefix = "GPH"
    prefix = "BTS"

    """ Callback on event
        This function will be triggered on a notification of the witness.
        If you subsribe (see below) to 2.6.*, the witness node will notify you of
        any chances regarding your account_balance """
    class GrapheneMonitor(GrapheneWebsocketProtocol) :
        last_op      = "1.11.0"
        account_id   = "1"
        def __init__(self) :
            super().__init__()

        def printJson(self,d) : print(json.dumps(d,indent=4))

        def onAccountUpdate(self, data) :
            # Get Operation ID that modifies our balance
            opID         = api.getObject(data["most_recent_op"])["operation_id"]
            self.wsexec([self.api_ids["history"], "get_account_history", [self.account_id, self.last_op, 100, "1.11.0"]], self.process_operations)
            self.last_op = opID

        def process_operations(self, operations) :
            for operation in operations[::-1] :
                opID         = operation["id"]
                block        = operation["block_num"]
                op           = operation["op"][1]

                if operation["op"][0] != 0 : continue ## skip non-transfer operations

                # Get assets involved in Fee and Transfer
                fee_asset    = api.getObject(op["fee"]["asset_id"])
                amount_asset = api.getObject(op["amount"]["asset_id"])

                # Amounts for fee and transfer
                fee_amount   =    op["fee"]["amount"] / float(10**int(fee_asset["precision"]))
                amount_amount= op["amount"]["amount"] / float(10**int(amount_asset["precision"]))

                # Get accounts involved
                from_account = api.getObject(op["from"])
                to_account   = api.getObject(op["to"])

                # Decode the memo
                memo         = op["memo"]
                try : # if possible
                    privkey = PrivateKey(memo_wif_key)
                    pubkey  = PublicKey(memo["from"], prefix=prefix)
                    memomsg = Memo.decode_memo(privkey, pubkey, memo["nonce"], memo["message"])
                except Exception as e: # if not possible
                    memomsg = "--cannot decode-- (%s)" % str(e)

                # Print out
                print("last_op: %s | block:%s | from %s -> to: %s | fee: %f %s | amount: %f %s | memo: %s" % (
                          opID, block, 
                          from_account["name"], to_account["name"],
                          fee_amount, fee_asset["symbol"],
                          amount_amount, amount_asset["symbol"],
                          memomsg))

    if __name__ == '__main__':
        ## Monitor definitions
        protocol = GrapheneMonitor
        protocol.last_op = last_op ## last operation logged
        protocol.account_id = "1.2.%s" % accountID.split(".")[2]  ## account to monitor
        ## Open Up Graphene Websocket API
        api      = GrapheneWebsocket(host, port, user, password, protocol)
        ## Set Callback for object changes
        api.setObjectCallbacks({accountID : protocol.onAccountUpdate})
        ## Run the Websocket connection continuously
        api.connect()
        api.run_forever()
