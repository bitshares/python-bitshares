Notify
~~~~~~~

This modules allows yout to be notified of events taking place on the
blockchain.

.. code-block:: python

   from pprint import pprint
   from bitshares.notify import Notify
   from bitshares.market import Market

   import logging
   log = logging.getLogger(__name__)
   #logging.basicConfig(level=logging.DEBUG)

   def print2(x):
       print(type(x))
       pprint(x)

   notify = Notify(
       markets=["TEST:GOLD"],
       accounts=["xeroc"],
       on_market=print2,
       on_account=print2
   )
   notify.listen()

.. autoclass:: bitshares.notify.Notify
   :members:
