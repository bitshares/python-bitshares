Instances
~~~~~~~~~

Default instance to be used when no ``bitshares_instance`` is given to
the Objects!

.. code-block:: python

   from bitshares.instance import shared_bitshares_instance

   account = Account("xeroc")
   # is equivalent with 
   account = Account("xeroc", bitshares_instance=shared_bitshares_instance())

.. automethod:: bitshares.instance.shared_bitshares_instance
.. automethod:: bitshares.instance.set_shared_bitshares_instance
