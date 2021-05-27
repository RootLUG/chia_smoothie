import time
import ssl
import random
import json
import urllib.request
import logging
import itertools
import traceback

from dataclasses import dataclass
from typing import Optional, List


from . import rpc_api
from . import config


SSL_CONTEXT = ssl.create_default_context()
backoff_cache = {}
last_print = None
existing_nodes = {}
force_last_resync = None

logger = logging.getLogger(__name__)


@dataclass
class Node:
    address: str
    height: int = 0
    last_seen: float = 0
    backoff: Optional[float] = None

    @classmethod
    def from_connection(cls, connection: dict):
        return cls(
            address=f"{connection['peer_host']}:{connection['peer_port']}",
            height=connection.get("peak_height", 0),
            last_seen=time.monotonic()
        )

    def connect(self):
        now = time.monotonic()

        if self.backoff is None or (self.backoff + config.CFG["resync_backoff"] < now):
            logger.info(f"Attempting to connect to the '{self.address}' full node")
            rpc_api.ChiaAPI.open_connection(self.address)
            self.backoff = now


class Resync:
    def __init__(self):
        self.height = 0
        self.cfg_nodes = {}
        self.existing_nodes = {}
        self.currently_connected = {}
        self.last_print = None
        self.external_limit = None

        self.height_spread = config.CFG["max_height_spread"]

        self.load_configured_nodes()

    @property
    def minimum_height(self) -> int:
        return self.height - self.height_spread

    def load_configured_nodes(self):
        for node_addr in config.CFG.get("nodes", []):
            node = Node(address=node_addr)
            self.cfg_nodes[node_addr] = node

    def load_external_full_nodes(self) -> List[Node]:
        nodes = []
        try:
            payload = get_json("https://chia.powerlayout.com/nodes")

            for n in payload["nodes"]:
                try:
                    node = Node(
                        address=f"{n['ip']}:{n['port']}",
                        height=int(n["block_height"])
                    )
                    nodes.append(node)
                except ValueError:
                    pass

            print(f"Loaded {len(nodes)} external full nodes")
        except Exception:
            traceback.print_exc()
        finally:
            random.shuffle(nodes)
            return nodes

    def cleanup(self):
        for n in self.existing_nodes.values():
            if n.height < self.minimum_height and n.address not in self.cfg_nodes:
                self.existing_nodes.pop(n.address)

    def connect_to_known_nodes(self):
        now = time.monotonic()

        if self.external_limit is None or self.external_limit + 30 <= now:
            self.external_limit = now
            external = self.load_external_full_nodes()

            for n in external:
                if n.address not in self.existing_nodes:
                    self.existing_nodes[n.address] = n

        node_chain = itertools.chain(sorted(
            [n for n in self.existing_nodes.values() if n.address not in self.currently_connected],
            key=lambda x: x.last_seen,
            reverse=True
        ))

        remaining = int((config.CFG["min_connections"] - len(self.currently_connected))*0.5)
        if remaining > 0:
            for _ in range(remaining):
                node = next(node_chain)
                node.connect()

    def update_state(self):
        chia_state = rpc_api.ChiaAPI.get_blockchain_state()
        self.height = chia_state["blockchain_state"]["peak"]["height"]

    def force_resync(self):
        self.update_state()
        connections = rpc_api.ChiaAPI.get_connections()

        self.currently_connected = {}

        for c in connections["connections"]:
            if c["type"] != 1:
                continue

            node = Node.from_connection(c)
            self.currently_connected[node.address] = node
            self.existing_nodes[node.address] = node

        for node in self.cfg_nodes.values():
            if node.address not in self.currently_connected:
                node.connect()
                self.currently_connected[node.address] = node

        self.connect_to_known_nodes()
        self.cleanup()


def get_json(url: str) -> dict:
    req = urllib.request.Request(
        url=url,
        headers={"User-Agent": config.CFG["user-agent"]}
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


def main():
    r = Resync()

    while True:
        r.force_resync()
        time.sleep(0.5)


if __name__ == "__main__":
    main()
