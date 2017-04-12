*************
Configuration
*************

The pybitshares library comes with its own local configuration database
that stores information like

* API node URL
* default account name
* the encrypted master password

and potentially more.

You can access those variables like a regular dictionary by using

.. code-block:: python

    from bitshares import BitShares
    bitshares = BitShares()
    print(bitshares.config.items())

Keys can be added and changed like they are for regular dictionaries.

If you don't want to load the :class:`bitshares.BitShares` class, you
can load the configuration directly by using:

.. code-block:: python

    from bitshares.storage import configStorage as config

API
---
.. autoclass:: bitshares.storage.Configuration
   :members:
