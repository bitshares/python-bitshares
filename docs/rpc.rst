*************
RPC Interface
*************

.. note:: This is a low level class that can be used in combination with
          GrapheneClient

We now need to distinguish functionalities. If we want to only access the
blockchain and do not want to perform on-chain operations like transfers or
orders, we are fine to interface with any accessible witness node. In contrast,
if we want to perform operations that modify the current blockchain state, e.g.
construct and broadcast transactions, we are required to interface with a
cli_wallet that has the required private keys imported. We here assume:

* port: 8090 - witness
* port: 8092 - wallet

.. note:: The witness API has a different instruction set than the wallet!

Definition
##########

.. autoclass:: grapheneapi.grapheneapi.GrapheneAPI
    :members: _confirm, rpcexec, __getattr__
