*********
Tutorials
*********

Bundle Many Operations
----------------------

With BitShares, you can bundle multiple operations into a single
transactions. This can be used to do a multi-send (one sender, multiple
receivers), but it also allows to use any other kind of operation. The
advantage here is that the user can be sure that the operations are
executed in the same order as they are added to the transaction.

.. code-block:: python

  from pprint import pprint
  from bitshares import BitShares

  testnet = BitShares(
      "wss://node.testnet.bitshares.eu",
      nobroadcast=True,
      bundle=True,
  )

  testnet.wallet.unlock("supersecret")

  testnet.transfer("init0", 1, "TEST", account="xeroc")
  testnet.transfer("init1", 1, "TEST", account="xeroc")
  testnet.transfer("init2", 1, "TEST", account="xeroc")
  testnet.transfer("init3", 1, "TEST", account="xeroc")

  pprint(testnet.broadcast())


Proposing a Transaction
-----------------------

In BitShares, you can propose a transactions to any account. This is
used to facilitate on-chain multisig transactions. With
python-bitshares, you can do this simply by using the ``proposer``
attribute:

.. code-block:: python

  from pprint import pprint
  from bitshares import BitShares

  testnet = BitShares(
      "wss://node.testnet.bitshares.eu",
      proposer="xeroc"
  )
  testnet.wallet.unlock("supersecret")
  pprint(testnet.transfer("init0", 1, "TEST", account="xeroc"))
