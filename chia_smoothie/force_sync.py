import time
import logging


from . import rpc_api
from . import config


backoff_cache = {}
logger = logging.getLogger(__name__)


def resync():
    backoff = config.CFG["resync_backoff"]

    connections = rpc_api.ChiaAPI.get_connections()

    full_nodes = [f"{c['peer_host']}:{c['peer_port']}" for c in connections["connections"] if c["type"] == 1]

    if len(full_nodes) > 1:
        out_level = lambda x: logger.debug(x)
    else:
        out_level = lambda x: logger.warning(x)

    out_level(f"Chia is connected to {len(full_nodes)} full nodes")

    for node in config.CFG.get("nodes", []):
        if node not in full_nodes:
            now = time.monotonic()

            if node not in backoff_cache or backoff_cache[node] + backoff <= now:
                rpc_api.ChiaAPI.open_connection(node)
                logging.info(f"Node '{node}' is missing in connections, forcing connection")
                backoff_cache[node] = now



def main():
    while True:
        resync()
        time.sleep(0.5)


main()
