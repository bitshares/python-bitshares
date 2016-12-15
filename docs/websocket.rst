*********
Websocket
*********

.. note:: This is a low level class that can be used in combination with
          GrapheneClient

Example
#######

For more examples see the provided scripts.

Run method on every new block
*****************************

In order to access the websocket functionalities, we need to extend the
``GrapheneWebsocketProtocol`` class:

.. code-block:: python

    from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol

    class GrapheneMonitor(GrapheneWebsocketProtocol) :
        def __init__(self) :
            super().__init__()

        def onBlock(self, data) :
            print(data)

    if __name__ == '__main__':
        protocol = GrapheneMonitor
        api      = GrapheneWebsocket(config.url, config.user, config.password, protocol)

        ## Set Callback for object changes
        api.setObjectCallbacks({"2.0.0" : protocol.onBlock})

        ## Run the Websocket connection continuously
        api.connect()
        api.run_forever()

Definitions
###########

.. autoclass:: grapheneapi.graphenews.GrapheneWebsocket
     :members:

.. autoclass:: grapheneapi.graphenewsprotocol.GrapheneWebsocketProtocol
     :members:
