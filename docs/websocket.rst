******************
TransnetWebsocket
******************

This class allows subscribe to push notifications from the Transnet
node.

.. code-block:: python

    from pprint import pprint
    from bitsharesapi.websocket import TransnetWebsocket

    ws = TransnetWebsocket(
        "wss://node.testnet.bitshares.eu",
        markets=[["1.3.0", "1.3.172"]],
        accounts=["xeroc"],
        objects=["2.0.x", "2.1.x"],
        on_market=pprint,
        on_account=print,
    )

    ws.run_forever()

Defintion
=========
.. autoclass:: bitsharesapi.websocket.TransnetWebsocket
    :members:
    :undoc-members:
    :private-members:
    :special-members:
