Witness
=======

A witness node represents a full node in the network that verifies all
transactions and blocks against its local state. Hence, we recommend all
service providers to run an maintain their own witness nodes for reliability
and security reasons.

It takes a `--data-dir` parameter to define a working and data directory to
store the configuration, blockchain and local databases. Those will be
automatically created with default settings if they don't exist locally set.

Launching a witness node
------------------------

The witness is launched according to:

.. code-block:: bash

    ./programs/witness_node/witness_node --data-dir="mydata"

Configuration
-------------

The configuration file `config.ini` in `mydata` is commented and contains the
following essential settings:

.. code-block:: ini

    # Endpoint for P2P node to listen on
    # p2p-endpoint = 

    # P2P nodes to connect to on startup (may specify multiple times)
    # seed-node = 

    # Pairs of [BLOCK_NUM,BLOCK_ID] that should be enforced as checkpoints.
    # checkpoint = 

    # Endpoint for websocket RPC to listen on
    # rpc-endpoint = 0.0.0.0:8090

    # Endpoint for TLS websocket RPC to listen on
    # rpc-tls-endpoint = 

    # The TLS certificate file for this server
    # server-pem = 

    # Password for this certificate
    # server-pem-password = 

    # File to read Genesis State from
    # genesis-json = sep-18-testnet-genesis.json

    # JSON file specifying API permissions
    # api-access = apiaccess.json

    # Enable block production, even if the chain is stale.
    enable-stale-production = false

    # Percent of witnesses (0-99) that must be participating in order to produce blocks
    required-participation = false

    # Allow block production, even if the last block was produced by the same witness.
    allow-consecutive = false

    # ID of witness controlled by this node (e.g. "1.6.5", quotes are required, may specify multiple times)
    # witness-id = 

    # Tuple of [PublicKey, WIF private key] (may specify multiple times)
    # private-key = ["pubkey","wif-key"]

    # Account ID to track history for (may specify multiple times)
    # track-account = 

    # Track market history by grouping orders into buckets of equal size measured in seconds specified as a JSON array of numbers
    # bucket-size = [15,60,300,3600,86400]

    # How far back in time to track history for each bucket size, measured in the number of buckets (default: 1000)
    # history-per-size = 1000

Enabling Remote Procedure Calls (RPC)
-------------------------------------

In order to allow RPC calls for blockchain operations you need to modify the
following entry in the configuration file:

.. code-block:: bash

    rpc-endpoint = 0.0.0.0:8090

This will open the port 8090 for global queries only. Since the witness node
only maintains the blockchain and (unless you are an actively block producing
witness) no private keys are involved, it is safe to expose your witness to the
internet.

Restarting the witness node
---------------------------

When restarting the witness node, it may be required to append the
`--replay-blockchain` parameter to regenerate the local (in-memory) blockchain
state.
