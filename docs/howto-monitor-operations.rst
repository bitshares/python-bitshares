***************************************************
Howto Monitor the blockchain for certain operations
***************************************************

Operations in blocks can be monitored relatively easy by using the
`block_stream` (for entire blocks) for `stream` (for specific
operations) generators.

The following example will only show ``transfer`` operations on the
blockchain:

.. code-block:: python

    from grapheneapi.grapheneclient import GrapheneClient
    from pprint import pprint

    class Config():
        witness_url           = "ws://testnet.bitshares.eu/ws"

    if __name__ == '__main__':
        client = GrapheneClient(Config)
        for b in client.ws.stream("transfer"):
            pprint(b)

Note that you can define a starting block and instead of waiting for
sufficient confirmations (irreversible blocks), you can also consider
the real *head* block with:

.. code-block:: python

        for b in client.ws.stream("transfer", start=199924, mode="head"):
