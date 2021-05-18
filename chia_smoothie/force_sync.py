import time
import ssl
import json
import urllib.request
import logging
import itertools
import traceback
import random


from . import rpc_api
from . import config


SSL_CONTEXT = ssl.create_default_context()
backoff_cache = {}
last_print = None
existing_nodes = {}
force_last_resync = None

logger = logging.getLogger(__name__)



def get_json(url: str) -> dict:
    req = urllib.request.Request(
        url=url,
        headers={"User-Agent": config.CFG["user-agent"]}
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def load_external_full_nodes() -> list:
    try:
        payload = get_json("https://chia.powerlayout.com/nodes")
        return [f"{v['ip']}:{v['port']}" for v in payload["nodes"]]
    except Exception:
        traceback.print_exc()
        return []



def force_connections(num=10):
    nodes = load_external_full_nodes()
    for n in nodes:
        existing_nodes[n] = 0

    logger.info(f"Retrieved {len(nodes)} full nodes from external api")
    node_chain = itertools.chain(sorted([(k, v) for k, v in existing_nodes.items()], key=lambda x:x[1], reverse=True))

    for _ in range(num):
        node, timing = next(node_chain)
        logger.info(f"Attempting to establish connection to {node}")
        rpc_api.ChiaAPI.open_connection(node)


def resync():
    global last_print, force_last_resync

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

    for n in full_nodes:
        if n not in existing_nodes:
            existing_nodes[n] = now

    if last_print is None or last_print + 60 <= now:
        logger.info(f"Chia is connected to {len(full_nodes)} nodes: {'; '.join(full_nodes)}")
        last_print = now

    if force_last_resync is None or force_last_resync + 60 <= now:
        remaining = config.CFG["min_connections"] - len(full_nodes)
        if remaining:
            logger.info("Not enough full node connections, attempting to discover the full nodes for connections")
            force_connections(remaining)
            force_last_resync = now


def main():
    while True:
        resync()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
