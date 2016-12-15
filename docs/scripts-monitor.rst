*******************
Monitoring Accounts
*******************

To monitor accounts, we recommend to either use the `get_full_accounts` call or
to enable notifications manually in order to fetch the current state of an
account and *automatically* subscribe to future account updates including
balance update.

Example Notifications
#####################

A notification after a transaction would take the form:::

    [[
        {
          "owner": "1.2.3184", 
          "balance": 1699918247, 
          "id": "2.5.3", 
          "asset_type": "1.3.0"
        }, 
        {
          "most_recent_op": "2.9.74", 
          "pending_vested_fees": 6269529, 
          "total_core_in_orders": 0, 
          "pending_fees": 0, 
          "owner": "1.2.3184", 
          "id": "2.6.3184", 
          "lifetime_fees_paid": 50156232
        }
    ]]

Please distinguish transactions from operations: Since a single transaction may
contain several (independent) operations, monitoring an account may only
require to investigate *operations* that change the account.

Implementation Details
######################

In order to access the websocket functionalities, we can extend the
`GrapheneWebsocketProtocol` class. 

.. code-block:: python

    import json
    from grapheneapi import GrapheneWebsocket, GrapheneWebsocketProtocol

    class GrapheneMonitor(GrapheneWebsocketProtocol) :
        def __init__(self) :
            super().__init__()

        def printJson(self,d) : print(json.dumps(d,indent=4))

        def getTxFromOp(self, op) :
            # print the most recent operation for our account!
            self.getObject(op[0]["operation_id"], self.printJson)

        def onAccountUpdate(self, data) :
            # most recent operation and callback getTxFromOp
            self.getObject(data["most_recent_op"], self.getTxFromOp)

We now have a set of 3 routines, `printJson` only dumps the available data.
The method `onAccountUpdate` will be trigged by the notification and will be
passed the notification's content. The type of the notification will be similar
to the object subscribed. Hence, if you subscribe to an object "2.6.12", you
will be notified about changes of "2.6.12" and the notification will carry the
id "2.6.12". In our case, 2.6.* represent operations that modify our account
balance and we get the id of the most recent operation that caused it.

The call `getObject` tries to resolve the id and hand out the corresponding
data from memory if available, or retrieve the object from the witness.
The `getObject` call accepts a callback as second parameter which will be
passed the ouptut of the query. In our case `self.getTxFromOp` performs another
object lookup before dumping the operations details in json format.

To register a notification and listen to the witness, we run:

.. code-block:: python

    if __name__ == '__main__':
         protocol = GrapheneMonitor
         monitor = GrapheneWebsocket("localhost", 8090, "", "", protocol)
         monitor.setObjectCallbacks({
                                "2.6.69491" : protocol.onAccountUpdate,
                               })
         monitor.connect()
         monitor.run_forever()

The protocol `GrapheneMonitor` has been defined above, the api connection is
established with `GrapheneWebsocket` and the callbacks are registered with
`monitor.setObjectCallbacks`. The websocket connection is initiated an listened
to with the last two lines.
