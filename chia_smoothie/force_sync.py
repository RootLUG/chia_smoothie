import time
import logging


from . import rpc_api
from . import config


backoff_cache = {}
last_print = None
logger = logging.getLogger(__name__)


def resync():
    global last_print

    backoff = config.CFG["resync_backoff"]
    now = time.monotonic()
    connections = rpc_api.ChiaAPI.get_connections()
    full_nodes = [f"{c['peer_host']}:{c['peer_port']}" for c in connections["connections"] if c["type"] == 1]

    for node in config.CFG.get("nodes", []):
        if node not in full_nodes:


            if node not in backoff_cache or backoff_cache[node] + backoff <= now:
                rpc_api.ChiaAPI.open_connection(node)
                logging.info(f"Node '{node}' is missing in connections, forcing connection")
                backoff_cache[node] = now

    if last_print is None or last_print + 60 <= now:
        logger.info(f"Chia is connected to {len(full_nodes)} nodes: {'; '.join(full_nodes)}")
        last_print = now


def main():
    while True:
        resync()
        time.sleep(0.5)


main()
