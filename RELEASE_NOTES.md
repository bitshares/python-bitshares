Release 0.2.0rc0
================

Storage:
--------

* internal storage now makes use of pygraphene 1.0.0 framework
* `bitshares.storage` now comes with the prebuilt inRam and SQLite stores from pygraphene
* `BitShares()` can be provided with a custom config store using key word `config_store=` and `wallet=` (wallet instance)
* `Wallet()` (internally used by `BitShares()`) can be provided with a custom config store using key word `key_store=`
* Interfaces for stores are defined in pygraphene
* The Interface for the wallet is defined in `wallet.py`
* Instead of using

  ```
  from bitshares.storage import configStorage as config
  ```

  use

  ```
  BitShares().config
  ```

  or

  ```
  from bitshares.storage import get_default_config_store
  config = get_default_config_store()
  ```

Testing:
--------

* pybitshares now contains a framework (fixtures) to simplify access to data provided by the blockchain/database
* Major improvements to coverage

Features:
---------

* Add custom operation to bitsharesbase

Fixes:
------

* 357aa63 Adjust "for_sale" when invert()-ing an Order
* 5924ac1 Allow to read more trading data #111
* 26a72fc Commenting #132
* f1b27d1 Set default expiration to 30 seconds #132
* bd69b2c Fix bitshares->blockchain attrribute #132
* a19b9ed Fix #136
* f616874 Revert "fix Vesting"
* b430d3b Set default order expiration to 1yr
* a949570 fix Vesting
* f70f20f Ensure we don't through in case 'secs=None'
* 0dabd9a Use PublicKey's internal sorting algorithm
* 8b7b134 Fix incompatibility with new graphene framework
* 9ce8068 Fix init of FilledOrder from history op
* 51c2277 Fix unittests for pygraphene@develop
* 803f828 further improvements
* 305efe2 Raise Exception in case the key has been included already
* 5b2736a fix store to deal with proper sqlite file etc
* 7e5ff23 unit tests now with fixtures
