**********
Price Feed
**********
(advanced users only)
(active witnesses only)

Requirements
############

We first need to install numpy and prettytable (besides autobahn and requests
for the library).

.. code-block:: bash

    apt-get install python3 python3-pip python-autobahn
    pip3 install requests --upgrade
    pip3 install numpy prettytable autobahn crypto

Cli Wallet
##########

Make sure to launch your ``cli_wallet`` with the ``-H`` or
``--rpc-http-endpoint`` followed by ``127.0.0.1:8092`` (or any other ip:port). 

.. note:: Do not expose the cli_wallet API connection to the internet as this
          may lead to loss of your funds!

Since the cli_wallet has no P2P connection capabilities, you need to connect it
to either your own witness node or a publicly accessible node:

.. code-block:: bash

    programs/cli_wallet/cli_wallet --rpc-http-endpoint="127.0.0.1:8092" -s "<ip-of-full/witness-node:port>"

Hence, the overall network setting would look similar to:::

    P2P network   <->   Full/Witness Node   <->  Wallet  <- Feed script

.. note:: Do not interface with the witness/full node directly. This will not
   work!

Configuration
#############

This (rather basic) price feed script is located in ``scripts/pricefeeds``
together with an example configuration file:

.. code-block:: bash

    cd scripts/pricefeeds/
    cp config-example.py config.py
    # edit config.py

Editing the ``config.py`` and be sure to set the RPC-client connection settings:

* the host to ``"127.0.0.1"`` (with quotes)
* and the port to ``8092``
* you can either put your unlock password into ``unlock`` or manually unlock
  your wallet before starting the script
* unless you are an expert there is no need to put user/pw info
* change your name of your witness in delegate_list

Running
#######

1. unlock your wallet
2. ``python3 pricefeeds.py``
3. You will be asked to provide confirmation of the prices!

.. Cronjon
   #######

.. Since the script fetches its data from other exchanges that may throttle your
   polling frequency, and you may want to run the feed script regularily, we
   recommend to setup your ``cron``-job as follows:

..   .. code-block:: cron

..      */2 * * * * /home/<user>/<path>/scripts/pricefeed/pricefeeds.py >> /home/<user>/feed-update.log

..   This will execute the script twice per hour and append the log into
   ``feed-update.log`` in your home directory.

