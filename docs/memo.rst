****
Memo
****

Memo Keys
#########

In Graphene, memos are AES-256 encrypted with a shared secret between sender and
receiver. It is derived from the memo private key of the sender and the memo
publick key of the receiver. 

In order for the receiver to decode the memo, the shared secret has to be
derived from the receiver's private key and the senders public key.

The memo public key is part of the account and can be retreived with the
`get_account` call:

.. code-block:: js

    get_account <accountname>
    {
      [...]
      "options": {
        "memo_key": "GPH5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
        [...]
      },
      [...]
    }

while the memo private key can be dumped with `dump_private_keys`

Memo Message
############

The take the following form:

.. code-block:: js

        {
          "from": "GPH5mgup8evDqMnT86L7scVebRYDC2fwAWmygPEUL43LjstQegYCC",
          "to": "GPH5Ar4j53kFWuEZQ9XhxbAja4YXMPJ2EnUg5QcrdeMFYUNMMNJbe",
          "nonce": "13043867485137706821",
          "message": "d55524c37320920844ca83bb20c8d008"
        }

The fields `from` and `to` contain the memo public key of sender and receiver.
The `nonce` is a random integer that is used for the seed of the AES encryption
of the message.

Example
#######

.. code-block:: python

    from graphenebase import Memo, PrivateKey, PublicKey

    wifkey = "5....<wif>"
    memo         = {
          "from": "GPH5mgup8evDqMnT86L7scVebRYDC2fwAWmygPEUL43LjstQegYCC",
          "to": "GPH5Ar4j53kFWuEZQ9XhxbAja4YXMPJ2EnUg5QcrdeMFYUNMMNJbe",
          "nonce": "13043867485137706821",
          "message": "d55524c37320920844ca83bb20c8d008"
        }
    try :
        privkey = PrivateKey(wifkey)
        pubkey  = PublicKey(memo["from"], prefix=prefix)
        memomsg = Memo.decode_memo(privkey, pubkey, memo["nonce"], memo["message"])
    except Exception as e:
        memomsg = "--cannot decode-- %s" % str(e)

Definitions
###########

.. automodule:: graphenebase.memo
    :members:
