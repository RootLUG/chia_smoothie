import os

import requests


certs = (
    os.path.expanduser("~/.chia/mainnet/config/ssl/full_node/private_full_node.crt"),
    os.path.expanduser("~/.chia/mainnet/config/ssl/full_node/private_full_node.key")
)


SESSION = requests.Session()
SESSION.cert = certs
SESSION.verify = False
SESSION.headers["Content-Type"] = "application/json"


class ChiaAPI:
    BASE_URI = "https://localhost:8555"

    @classmethod
    def get_blockchain_state(cls):
        resp = SESSION.post(f"{cls.BASE_URI}/get_blockchain_state", json={"":""})
        return resp.json()

    @classmethod
    def get_connections(cls):
        resp = SESSION.post(f"{cls.BASE_URI}/get_connections", json={"": ""})
        return resp.json()

    @classmethod
    def open_connection(cls, addr):
        host, port = addr.rsplit(":", 1)

        payload = {
            "host": host,
            "port": port
        }

        resp = SESSION.post(f"{cls.BASE_URI}/open_connection", json=payload)
        return resp.json()


if __name__ == "__main__":
    import pprint

    pprint.pprint(ChiaAPI.get_connections())
