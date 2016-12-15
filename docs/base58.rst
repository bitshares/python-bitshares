************
Base58 Class
************

This class serves as an abstraction layer to deal with base58 encoded strings
and their corresponding hex and binary representation throughout the library.

Examples:
#########

.. code-block:: python

        format(Base58("02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"),"wif")
        repr(Base58("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd"))

Output:::

       "5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd"
       "02b52e04a0acfe611a4b6963462aca94b6ae02b24e321eda86507661901adb49"

Definitions
###########

.. autoclass:: graphenebase.base58.Base58
   :members:
