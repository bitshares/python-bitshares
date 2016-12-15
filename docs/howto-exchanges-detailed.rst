Howto Interface your Exchange with Graphene (Detailed)
======================================================

This Howto servers as an introduction for exchanges that want to interface with
BitShares to allow trading of assets from the BitShares network. It is
recommended that the developer reads and understands the content of the
following articles:

.. toctree::
   :maxdepth: 1

   graphene-objects
   graphene-api
   graphene-ws
   wallet
   rpc

.. note:: This tutorial explains the inner workings of the monitoring script
          provided as `monitor.py` in the `scripts/monitor-despoits` directory.

Network and Client Configuration
--------------------------------

Introduction
____________________

Similar to other crypto currencies, it is recommended to wait for several
confirmations of a transcation. Even though the consensus scheme of Graphene is
alot more secure than regular proof-of-work or other proof-of-stake schemes, we
still support exchanges that require more confirmations for deposits.

We provide a so called *delayed* full node which accepts two additional
parameters for the configuration besides those already available with the
standard daemon.

* `trusted-node` RPC endpoint of a trusted validating node (required)
* `delay-block-count` Number of blocks to delay before advancing chain state (required)

The trusted-node is a regular full node directly connected to the P2P
network that works as a proxy. The `delay-block-count` gives the number of
blocks that the delayed full node will be behind the real blockchain.

Overview of the Setup
-------------------------------

In the following, we will setup and use the following network:::

    P2P network <-> Trusted Full Node <-> Delayed Full Node <-> API

* P2P network:
  The BitShares client uses a peer-to-peer network to connect and broadcasts
  transactions there. A block producing full node will eventually catch your
  transcaction and validates it by adding it into a new block.
* Trusted Full Node:
  We will use a Full node to connect to the network directly. We call it
  *trusted* since it is supposed to be under our control.
* Delayed Full Node:
  The delayed full node node will provide us with a delayed and several times
  confirmed and verified blockchain. Even though DPOS is more resistant against
  forks than most other blockchain consensus schemes, we delay the blockchain
  here to reduces the risk of forks even more. In the end, the delayed full
  node is supposed to never enter an invalid fork.
* API:
  Since we have a delayed full node that we can fully trust, we will interface
  with this node to query the blockchain and receive notifications from it one
  balance changes.

The delayed full node should be in the same *local* network as the trusted full
node is in the same network and has internet access. Hence we will work with
the following IPs:

* Trusted Full Node:
   * extern: *internet access*
   * intern: `192.168.0.100`

* Delayed Full Node:
   * extern: *no* internet access required
   * intern: `192.168.0.101`

Let's go into more detail how to set these up.

Trusted Full Node
_________________

For the trusted full node, the default settings can be used.  For later, we
will need to open the RPC port and listen to an IP address to connect the
delayed full node to.::

    ./programs/witness_node/witness_node --rpc-endpoint="192.168.0.100:8090"

.. note:: A *witness* node is identical to a full node if no authorized
          block-signing private key is provided.

Delayed Full Node
_________________

The delayed full node will need the IP address and port of the p2p-endpoint
from the trusted full node and the number of blocks that should be delayed.  We
also need to open the RPC/Websocket port (to the local network!) so that we can
interface using RPC-JSON calls.

For our example and for 10 blocks delaye (i.e. 30 seconds for 3 second block
intervals), we need:::

    ./programs/delayed_node/delayed_node --trusted-node="192.168.0.100:8090" --delay-block-count=10 --rpc-endpoint="192.168.0.101:8090"

We could now connect via RPC:

* `192.168.0.100:8090` : The trusted full node exposed to the internet
* `192.168.0.101:8090` : The delayed full node not exposed to the internet

.. note:: For security reasons, an exchange should only interface with the delayed
          full node.

For obvious reasons, the trusted full node is should be running before
attempting to start the delayed full node.

Interfacing via RPC and Websockets
----------------------------------

Overview
________

In order to access the unrestricted API-0, we call make use of usual
*stateless* RPC-calls. To access the restricted API-1 we are required to use
the websocket connection with callbacks to access API-1:

* API-0: `api.info()`, `api.get_*()`, ...
* API-1: `api.ws_exec([api_identifier, call], callback)`

Accessing API-0
_______________

Now that we have your delayed full node running at `192.168.0.101:8090`, we can
interface with it using websockets. In order to access the websocket
functionalities, we can make use of `GrapheneWebSocket` which is provided by
`python-graphene` libraries (:doc:`installation`).

.. code-block:: python

    import json
    from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
    if __name__ == '__main__':
         api = GrapheneWebsocket("192.168.0.101", 8090, "", "")
         # get configuration
         chain_config = api.get_config()
         # get dynamic properties (e.g. block head num)
         dynam_proper = api.get_dynamic_global_properties()
         # dump data
         print(json.dumps(chain_config,indent=4))
         print(json.dumps(dynam_proper,indent=4))

This example opens up a Websocket connection with our delayed full node with
empty username and passwords. As can be seen, the `api` object takes any method
and translates them into a proper API call (see :doc:`graphene-api`).

Accessing API-1
_______________

Even though most basic interaction can be performed using API-0, we sometimes
need to sometimes hook into a running websocket connection. The difference
between API-0 and API-1 is that API-1 can be authorized against the full node
and be granted additional permissions. For instance, calling the transaction
history of an account requires access to `history_api` and needs an `api_id` to
access its associated calls.

.. note:: The `GrapheneWebsocketProtocol` automatically obtains access to the
          `database_api` aswell as the `history_api`.

To be able to interact with `history_api`, we extend the default
`GrapheneWebsocketProtocol` protocol with 

.. code-block:: python

    class GrapheneMonitor(GrapheneWebsocketProtocol) :
        def __init__(self) :
            super().__init__()
        def do_something(self, data) :
            pass
        def dump_api_ids(self) :
            print(self.api_ids)
            pass
        def call_history_api(self,method,params, callback) :
            self.wsexec([self.api_ids["history"], method, params], callback)
            pass

The variable `self.api_ids` is initiated when opening the websocket connection
automatically. 

.. note:: Since the websocket connection has a state and works asynchonously,
          we need to hand over a callback function that will be executed when
          the full node answers our request.

We make use of this class when connecting to the full node:

.. code-block:: python

        protocol = GrapheneMonitor
        api      = GrapheneWebsocket(host, port, user, password, protocol)

We can now either use API-0 by issuing calls via `api.*method*(*params*)` or
asynchronously interact with restricted APIs via the class `GrapheneMonitor`.

Subscribing to Object Changes
_____________________________

Besides polling for data, the full node is capable of sending notifications.
Let's subscribe to changes and have it printed out on screen. Todo so, we need
to know the object id (see :doc:`graphene-objects`) we are interested in.
For instance, if we want to get notified on changes of an account object, we
subscribe to `1.2.*` with `*` being the account identification numbers.
Alternatively, we can subscribe to changes of the corresponding balance (e.g.
modification of most recent operations that change the balance) by subscribing
to `2.6.*`.

We subscribe by issuing `setObjectCallbacks()` and handing over a structure of
the form `id: callback`. Hence, each object can be assigned only one callback.

In the following example, we print out modifications of the object only:

.. code-block:: python

     api.setObjectCallbacks({ "2.6.69491" : print })
     api.connect()
     api.run_forever()

The example subscribes to modifications of the object "2.6.69491" and will call
`print` with the notification as parameter.

A notification will be sent, whenever a value in the object `2.6.69491`
changes:::

    {
        "id": "2.6.69491",
        "total_core_in_orders": 0,
        "most_recent_op": "2.9.0",
        "pending_fees": 0,
        "pending_vested_fees": 0,
        "owner": "1.2.69491",
        "lifetime_fees_paid": 0
    }    

To monitor balance changes we are mostly interested in `most_recent_op`-changes
which will be described in the following.

To monitor accounts, we recommend to either use the `get_full_accounts` call or
to enable notifications manually in order to fetch the current state of an
account and *automatically* subscribe to future account updates including
balance update.

.. note:: Please distinguish transactions from operations: Since a single
          transaction may contain several (independent) operations, monitoring
          an account may only require to investigate *operations* that change
          the account.

Decoding the Memo
_________________

In Graphene, memos are usually encrypted using a distinct memo key. That way,
exposing the memo private key will only expose transaction memos (for that key)
and not compromise any funds. It is thus safe to store the memo private key in
3rd party services and scripts. The memo public key can be obtained from the
account settings or via command line:::

    get_account myaccount

in the cli wallet. The corresponding private key can be obtain from:::

    dump_private_keys

Note that the latter command exposes all private keys in clear-text wif.

The encrypted memo can be decoded with:

.. code-block:: python

    from graphenebase import Memo, PrivateKey, PublicKey
    memo_wif_key = "<wif-key>"
    """ PubKey Prefix
        Productive network: BTS
        Testnetwork: GPH """
    #prefix = "GPH"
    prefix = "BTS"

    memo    = {...} # take from the transfer operation
    privkey = PrivateKey(memo_wif_key)
    pubkey  = PublicKey(memo["from"], prefix=prefix)
    memomsg = Memo.decode_memo(privkey, pubkey, memo["nonce"], memo["message"])

Monitoring Example Script
--------------------------

As an example, we can have notifications for all incoming transactions for any
account. Let's discuss this example script in more details:

1) We first prepare our variables and import all required modules

   Define the `accountID` and the `memo_wif_key`.
   The accountID can be obtained from the GUI wallet, or by issuing:::

       get_account <accountname>

   If the script exists abnormally, you can continue operations by setting
   `last_op` to the last operation id that you have captured before the
   abnormal exit.

.. note:: The current implementation has a maxium history size of 100
          transaction. If you have missed more than 100 transaction with the
          current implementation, manual fixing is required.

.. code-block:: python

    import sys
    import json
    from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol
    from graphenebase import Memo, PrivateKey, PublicKey

    """ Account id to monitor """
    accountID = "2.6.69585"

    """ Memo Key of the receiving account """
    memo_wif_key = "<wif-key>"

    """ Last operation ID that you have registered in your backend """
    last_op = "1.11.0"

    """ PubKey Prefix
        Productive network: BTS
        Testnetwork: GPH """
    prefix = "GPH"
    #prefix = "BTS"

2) We then overwrite the basis class so that we can access the restricted API-1:

.. code-block:: python

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

3) We define an entry point for our notifications. Here notifications for
account balance changes will call `onAccountUpdate`. We will only get the
history of the account since the last operation (`last_op`) and call
`process_operations`.

.. code-block:: python

        def onAccountUpdate(self, data) :
            # Get Operation ID that modifies our balance
            opID         = api.getObject(data["most_recent_op"])["operation_id"]
            self.wsexec([self.api_ids["history"], "get_account_history", [self.account_id, self.last_op, 100, "1.11.0"]], self.process_operations)
            self.last_op = opID

4) The history returns an array of operations and we process each of them
   individually. To do so, we query the api to get more details about

   * the sender
   * the receiver
   * transfer amount and asset
   * fee amount and asset
   * the memo

.. code-block:: python

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

5) We then dump all of these information onto the screen. At this point an
   exchange may want to forward the transaction as well as the memo to some
   internal post processing and increase the customers balance.

   We here dump all of these information onto the screen.

.. code-block:: python

                # Print out
                print("last_op: %s | block:%s | from %s -> to: %s | fee: %f %s | amount: %f %s | memo: %s" % (
                          opID, block, 
                          from_account["name"], to_account["name"],
                          fee_amount, fee_asset["symbol"],
                          amount_amount, amount_asset["symbol"],
                          memomsg))

Now that we have extended our `GrapheneWebsocketProtocol` we make use of it as
follows. We first define our RPC connection settings and define our protocol to
be `GrapheneMonitor`.

.. code-block:: python

    if __name__ == '__main__':

        ## RPC connections
        host     = "localhost"
        port     = 8090
        user     = ""
        password = ""

        ## Monitor definitions
        protocol = GrapheneMonitor

Then we define some initial parameters for our monitor.

.. note:: The account id is derived from the given parameter whereas the first
          part is replace to access the account object to obtain its history later.

.. code-block:: python

        protocol.last_op = last_op ## last operation logged
        protocol.account_id = "1.2.%s" % accountID.split(".")[2]  ## account to monitor

We connect to the websocket protocol, define out subscription callback and let
the script run indefinitely to listen to websocket notifications:

.. code-block:: python

        ## Open Up Graphene Websocket API
        api      = GrapheneWebsocket(host, port, user, password, protocol)
        ## Set Callback for object changes
        api.setObjectCallbacks({accountID : protocol.onAccountUpdate})
        ## Run the Websocket connection continuously
        api.connect()
        api.run_forever()
