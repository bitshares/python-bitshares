.. python-bitshares documentation master file, created by
   sphinx-quickstart on Fri Jun  5 14:06:38 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. http://sphinx-doc.org/rest.html
   http://sphinx-doc.org/markup/index.html
   http://sphinx-doc.org/markup/para.html
   http://openalea.gforge.inria.fr/doc/openalea/doc/_build/html/source/sphinx/rest_syntax.html
   http://rest-sphinx-memo.readthedocs.org/en/latest/ReST.html

Welcome to pybitshares's documentation!
===============================================

BitShares is a **blockchain-based autonomous company** (i.e. a DAC) that
offers decentralized exchanging as well as sophisticated financial
instruments as *products*.

It is based on *Graphene* (tm), a blockchain technology stack (i.e.
software) that allows for fast transactions and ascalable blockchain
solution. In case of BitShares, it comes with decentralized trading of
assets as well as customized on-chain smart contracts.

About this Library
------------------

The purpose of *pybitshares* is to simplify development of products and
services that use the BitShares blockchain. It comes with

* it's own (bip32-encrypted) wallet
* RPC interface for the Blockchain backend
* JSON-based blockchain objects (accounts, blocks, prices, markets, etc)
* a simple to use yet powerful API
* transaction construction and signing
* push notification API
* *and more*

Quickstart
----------

.. note:: All methods that construct and sign a transaction can be given
          the ``account=`` parameter to identify the user that is going
          to affected by this transaction, e.g.:
          
          * the source account in a transfer
          * the accout that buys/sells an asset in the exchange
          * the account whos collateral will be modified

         **Important**, If no ``account`` is given, then the
         ``default_account`` according to the settings in ``config`` is
         used instead.

.. code-block:: python

   from bitshares import BitShares
   bitshares = BitShares()
   bitshares.wallet.unlock("wallet-passphrase")
   bitshares.transfer("<to>", "<amount>", "<asset>", "[<memo>]", account="<from>")

.. code-block:: python

   from bitshares.blockchain import Blockchain
   blockchain = Blockchain()
   for op in Blockchain.ops():
       print(op)

.. code-block:: python

   from bitshares.block import Block
   print(Block(1))

.. code-block:: python

   from bitshares.account import Account
   account = Account("init0")
   print(account.balances)
   print(account.openorders)
   for h in account.history():
       print(h)

.. code-block:: python

   from bitshares.market import Market
   market = Market("USD:BTS")
   print(market.ticker())
   market.bitshares.wallet.unlock("wallet-passphrase")
   print(market.sell(300, 100)  # sell 100 USD for 300 BTS/USD

.. code-block:: python

   from bitshares.dex import Dex
   dex = Dex()
   dex.bitshares.wallet.unlock("wallet-passphrase")
   dex.adjust_collateral_ratio("SILVER", 3.5)
   

General
-------------------------
.. toctree::
   :maxdepth: 1

   installation
   quickstart
   tutorials
   configuration
   contribute
   support

Python-BitShares Libraries
--------------------------

.. toctree::
   :maxdepth: 1

   bitshares
   instances
   account
   amount
   asset
   block
   blockchain
   exceptions
   dex
   market
   notify
   price
   vesting
   witness
   worker
   proposal

Low Level Classes
-----------------

.. toctree::
   :maxdepth: 1

   storage
   utils
   transactionbuilder
   wallet
   websocket
   websocketrpc
   transactions
   memo

Glossary
========

.. toctree::
   :maxdepth: 1

   mpa

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
