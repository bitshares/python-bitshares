***
FAQ
***

How to get order info on filled order
-------------------------------------

On CEX exchanges full order info usually available for canceled / filled orders.
On BitShares such info is not available, because such info is stored in memory
of bitshares-core node, and keeping non-actual orders info would take
astonishing amounts of RAM.

Thus, such order info could be obtained in two ways:

* By querying account history from the node:

.. code-block:: python

   from bitshares.account import Account

   a = Account('dexbot')
   ops = a.history(only_ops=['fill_order'], limit=1)
   for op in ops:
       print(op)

Note: this way has limitation: public nodes doesn't store full account history,
only limited number of entries

* By querying `elasticsearch plugin
  <https://dev.bitshares.works/en/master/supports_dev/elastic_search_plugin.html>`_.
  In short, elasticsearch plugin export account history data into elasticsearch
  instance, from which it's can be obtained directly or via elasticsearch
  wrapper. See `<https://eswrapper.bitshares.eu/apidocs/>`_ to get info on how
  to query the wrapper. A real-world example of elasticsearch wrapper usage for
  obtaining filled orders history is `bitshares-tradehistory-analyzer
  <https://github.com/bitfag/bitshares-tradehistory-analyzer>`_


How to detect partially filled order
------------------------------------

An Order have the following fields:

* ``order['base']['amount']``: stores initial amount to sell
* ``order['for_sale']['amount']``: stores remaining amount to sell

So, if your order initially sells 100 BTS, and 50 BTS was sold, the
``order['for_sale']['amount']`` will contain remaining 50 BTS.
