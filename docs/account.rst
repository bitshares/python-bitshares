**************
Account Module
**************

Address Class
#############

.. autoclass:: graphenebase.account.Address
    :members: __repr__, __str__, __format__, __bytes__

PublicKey Class
###############

.. autoclass:: graphenebase.account.PublicKey
    :members: __repr__, __str__, __format__, __bytes__

PrivateKey Class
################

.. autoclass:: graphenebase.account.PrivateKey
    :members: 

Brainkey
########

.. autoclass:: graphenebase.account.BrainKey
    :members: 

Remarks
#######
  
Format vs. Repr
***************

.. code-block:: python

    print("Private Key             : " + format(private_key,"WIF"))
    print("Secret Exponent (hex)   : " + repr(private_key))
    print("BTS PubKey (hex)        : " + repr(private_key.pubkey))
    print("BTS PubKey              : " + format(private_key.pubkey, "BTS"))
    print("BTS Address             : " + format(private_key.address,"BTS"))

Output::

    Private Key             : 5Jdv8JHh4r2tUPtmLq8hp8DkW5vCp9y4UGgj6udjJQjG747FCMc
    Secret Exponent (hex)   : 6c2662a6ac41bd9132a9f846847761ab4f80c82d519cdf92f40dfcd5e97ec5b5
    BTS PubKey (hex)        : 021760b78d93878af16f8c11d22f0784c54782a12a88bbd36be847ab0c8b2994de
    BTS PubKey              : BTS54nWRnewkASXXTwpn3q4q8noadzXmw4y1KpED3grup7VrDDRmx
    BTS Address             : BTSCmUwH8G1t3VSZRH5kwxx31tiYDNrzWvyW

Compressed vs. Uncompressed
***************************

.. code-block:: python

    print("BTC uncomp. Pubkey (hex): " + repr(private_key.uncompressed.pubkey))
    print("BTC Address (uncompr)   : " + format(private_key.uncompressed.address,"BTC"))
    print("BTC comp. Pubkey (hex)  : " + repr(private_key.pubkey))
    print("BTC Address (compr)     : " + format(private_key.address,"BTC"))

Output::

    BTC uncomp. Pubkey (hex): 041760b78d93878af16f8c11d22f0784c54782a12a88bbd36be847ab0c8b2994de4d5abd46cabab34222023cd9034e1e6c0377fac5579a9c01e46b9498529aaf46
    BTC Address (uncompr)   : 1JidAV2npbyLn77jGYQtkpJDjx6Yt5eJSh
    BTC comp. Pubkey (hex)  : 021760b78d93878af16f8c11d22f0784c54782a12a88bbd36be847ab0c8b2994de
    BTC Address (compr)     : 1GZ1JCW3kdL4LoCWbzHK4oV6V8JcUGG8HF
