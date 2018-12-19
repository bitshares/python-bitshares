*************
Configuration
*************

The pybitshares library comes with its own local configuration database
that stores information like

* API node URL
* default account name
* the encrypted master password

and potentially more, **persistently**.

You can access those variables like a regular dictionary by using

.. code-block:: python

    from bitshares import BitShares
    bitshares = BitShares()
    print(bitshares.config.items())

Keys can be added and changed like they are for regular dictionaries.

.. code-block:: python

    bitshares.config["my-new-variable"] = "important-content"
    print(bitshares.config["my-new-variable"])
