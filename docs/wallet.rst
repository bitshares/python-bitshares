Wallet
~~~~~~

Create a new wallet
-------------------

A new wallet can be created by using:

.. code-block:: python

   from bitshares import BitShares
   bitshares = BitShares()
   bitshares.wallet.create("supersecret-passphrase")

This will raise an exception if you already have a wallet installed.

Unlocking the wallet for signing
--------------------------------

The wallet can be unlocked for signing using

.. code-block:: python

   from bitshares import BitShares
   bitshares = BitShares()
   bitshares.wallet.unlock("supersecret-passphrase")

API
---

.. autoclass:: bitshares.wallet.Wallet
   :members:
