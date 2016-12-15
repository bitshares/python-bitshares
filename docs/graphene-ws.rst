Websocket subscriptions
=======================

Before we can subscribe to any changes, we first need to ask for access to the
`database`-api with::

    > {"id":2,"method":"call","params":[0,"database",[]]}
    < {"id":2,"result":1}

The `result` will be our `DATABASE_API_ID`!

In Graphene, we have the following subscriptions available:

* `set_subscribe_callback( cb, bool clear_filter )`:
     To simplify development a global subscription callback can be registered.
* `set_pending_transaction_callback(  cb )`:
     Notifications for incoming *unconfirmed* transactions.
* `set_block_applied_callback( blockid )`:
     Gives a notification whenever the block `blockid` is applied to the
     blockchain.

Let's first get a global scubscription callback to disctinguish our
notifications from regular RPC calls:::

    > {"id":4,"method":"call","params":[DATABASE_API_ID,"set_subscribe_callback",[SUBSCRIPTION_ID]]}

This call above will register `SUBSCRIPTION_ID` as id for notifications.

Now, whenever you get an object from the witness (e.g. via `get_objects`) you
will automatically subscribe to any future changes of that object.

After calling `set_subscribe_callback` the witness will start to send notices
every time the object changes:::

    < {
        "method": "notice"
        "params": [
            SUBSCRIPTION_ID, 
            [[
                { "id": "2.1.0", ...  },
                { "id": ...  },
                { "id": ...  },
                { "id": ...  }
            ]]
        ], 
    }

Here is an example of a full session:::

    > {"id":1,"method":"call","params":[0,"login",["",""]]}
    < {"id":1,"result":true}
    > {"id":2,"method":"call","params":[0,"database",[]]}
    < {"id":2,"result":1}
    > {"id":3,"method":"call","params":[1,"set_subscribe_callback",[200]]}
    < {"id":3,"result":true}
    < {"method":"notice","params":[200,[[{"id":"2.1.0","random":"2033120557c36e278db2eaad818494f791ff4d7b0418858a7ab9b5a8","head_block_number":5,"head_block_id":"00000005171f82f1b6bd948e7d58d95e572001fd","time":"2015-05-01T13:05:50","current_witness":"1.7.5","next_maintenance_time":"2015-05-02T00:00:00"}]]]}
    < {"method":"notice","params":[200,[[{"id":"2.1.0","random":"9d5ff7e453db4815005eb42ddd040e3afb459950f75f4440deb3dec0","head_block_number":6,"head_block_id":"000000060e3369d6feaf330ea9114cd855c93aab","time":"2015-05-01T13:05:55","current_witness":"1.7.3","next_maintenance_time":"2015-05-02T00:00:00"}]]]}
    < {"method":"notice","params":[200,[[{"id":"2.1.0","random":"cb8686582c40634a0c0834d0f2c4ad19f8ca80598cc3eee2b93c124d","head_block_number":7,"head_block_id":"000000071d0bc8db55d7da75d1d880818d1930fd","time":"2015-05-01T13:06:00","current_witness":"1.7.0","next_maintenance_time":"2015-05-02T00:00:00"}]]]}
