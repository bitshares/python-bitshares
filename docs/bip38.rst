****************************
Bip38 Encrypted Private Keys
****************************

BIP 38 allows to encrypt and decrypt private keys in the WIF format.

Examples
########

.. code-block:: python

     from graphenebase import PrivateKey
     from graphenebase.bip38 import encrypt 

     format(encrypt(PrivateKey("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd"),"SecretPassPhrase"), "encwif")
     
     >> "6PRN5mjUTtud6fUXbJXezfn6oABoSr6GSLjMbrGXRZxSUcxThxsUW8epQi",

.. code-block:: python

     from graphenebase import PrivateKey
     from graphenebase.bip38 import decrypt 

     format(decrypt("6PRN5mjUTtud6fUXbJXezfn6oABoSr6GSLjMbrGXRZxSUcxThxsUW8epQi","SecretPassPhrase"),"wif"),

     >> "5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd",

Definitions
###########

.. automodule:: graphenebase.bip38
   :members: encrypt, decrypt
