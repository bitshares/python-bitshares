Blockchain
~~~~~~~~~~

Read blockchain related data-

.. code-block:: python

   from bitshares.blockchain import Blockchain
   chain = Blockchain()

Read current block and blockchain info

.. code-block:: python

   print(chain.get_current_block())
   print(chain.info())

Monitor for new blocks ..

.. code-block:: python

   for block in chain.blocks():
       print(block)

... or each operation individually:

.. code-block:: python

   for operations in chain.ops():
       print(operations)

.. autoclass:: bitshares.blockchain.Blockchain
   :members:
