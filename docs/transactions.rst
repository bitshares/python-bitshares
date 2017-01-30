***********************************************
Manual Constructing and Signing of Transactions
***********************************************

.. warning:: This is a low level class. Do not use this class unless you
             know what you are doing!

.. note:: This class is under development and meant for people that are
          looking into the low level construction and signing of various
          transactions.

Loading Transactions Class
##########################

We load the class for manual transaction construction via:

.. code-block:: python

    from bitsharesbase import transactions, operations

Construction
############

Now we can use the predefined transaction formats, e.g. ``Transfer`` or
``limit_order_create`` as follows:

1. define the expiration time
2. define a JSON object that contains all data for that transaction
3. load that data into the corresponding **operations** class
4. collect multiple operations
5. get some blockchain parameters to prevent replay attack
6. Construct the actual **transaction** from the list of operations
7. sign the transaction with the corresponding private key(s)

**Example A: Transfer**

.. code-block:: python

        expiration = transactions.formatTimeFromNow(60)
        op = operations.Transfer(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},  # will be filled in automatically
            "from": "1.2.124",
            "to": "1.2.1241",
            "amount": {"amount": 10000, "asset_id": "1.3.0"},
        })
        ops    = [transactions.Operation(op)]
        ref_block_num, ref_block_prefix = transactions.getBlockParams(rpc)
        tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                                 ref_block_prefix=ref_block_prefix,
                                                 expiration=expiration,
                                                 operations=ops)
        tx = tx.sign([wif])

**Example A: Limit-order-create**

.. code-block:: python

    # Expiration time 60 seconds in the future
    expiration = transactions.formatTimeFromNow(60)
    op = operations.Limit_order_create(**{
        "fee": {"amount": 100,
                "asset_id": "1.3.0"
                },
        "seller": "1.2.29",
        "amount_to_sell": {"amount": 100000,
                           "asset_id": "1.3.0"
                           },
        "min_to_receive": {"amount": 10000,
                           "asset_id": "1.3.105"
                           },
        "expiration": "2016-05-18T09:22:05",
        "fill_or_kill": False,
        "extensions": []
    })
    ops    = [transactions.Operation(op)]
    ref_block_num, ref_block_prefix = transactions.getBlockParams(rpc)
    tx     = transactions.Signed_Transaction(ref_block_num=ref_block_num,
                                             ref_block_prefix=ref_block_prefix,
                                             expiration=expiration,
                                             operations=ops)
    tx = tx.sign([wif])

Broadcasting
############

For broadcasting, we first need to convert the transactions class into a
JSON object. After that, we can broadcast this to the network:

.. code-block:: python

    # Broadcast JSON to network
    rpc.broadcast_transaction(tx.json(), api="network_broadcast"):
