Chia smoothie
=============

A collection of tools for the chia blockchain


Installation, no dependencies required:

    python setup.py install


Configuration:
--------------

All API connections requires SSL certificates including client to be able to connect to the chia daemon. On Linux and Mac the default cert paths are used:

```
~/.chia/mainnet/config/ssl/full_node/private_full_node.crt
~/.chia/mainnet/config/ssl/full_node/private_full_node.key
```

Windows appears to have different paths depending on the installed chia version so we advise to configure manually paths in the chia_smoothie.json config. If the `cert_chain` variable in config is empty or non-existing default (linux&mac) paths are used otherwise paths configured in config are used.

Please note that both `crt` and `key` files are required.


Force resync with full nodes:
-----------------------------

    python -m chia_smoothie.force_sync


This command will periodically (every half second) check what full nodes connections are open in chia to ensure that the local node is fully synchronized. It will check against a list of nodes as specified in the `chia_smoothie.json` config file. If chia is not connected to a node from the config, it will force the daemon to open a new connection to the node for syncing. There is a configurable delay `resync_backoff` in the config between attempts for establishing the connection to each node.



Donate
------

- GitHub Sponsors: https://github.com/sponsors/RootLUG
- Liberapay: https://liberapay.com/SourceCode.AI
- BuyMeACoffee: https://www.buymeacoffee.com/SourceCodeAI
- BTC: 3FVTaLsLwTDinmDjPh3BjS1qv3bYHbkcYc
- XMR: 46xvWZGCexo1NbvjLMMpLB1GhRd819AQr8eFPJT1q6kKMuuDy43JLiESh9XUM3asjk4SVUYqGakFVQZRY1adx8cS6ka4EXr
- ETH/ERC20: 0x708F1A08E3ee4922f037673E720c405518C0Ec85
- Chia: xch1tvtslx90huhsl84atfd5j86f2e0xxm3rvvv8hc2se9xt0mw6n62snekjt3
