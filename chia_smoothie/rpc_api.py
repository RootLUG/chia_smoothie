import os
import platform
import ssl
import json
import urllib.request

from . import config


def create_ssl_context():
    ssl_context = ssl.create_default_context()

    if (cert_chain := config.CFG.get("cert_chain")):
        pass
    else:
        cert_chain = (
            "~/.chia/mainnet/config/ssl/full_node/private_full_node.crt",
            "~/.chia/mainnet/config/ssl/full_node/private_full_node.key"
        )

    cert_chain = tuple(map(os.path.expanduser, cert_chain))
    ssl_context.load_cert_chain(*cert_chain)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    return ssl_context


SSL_CONTEXT = create_ssl_context()


class ChiaAPI:
    BASE_URI = "https://localhost:8555"

    @classmethod
    def _send_request(cls, url, payload=None):
        payload = payload or {"": ""}

        req = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        resp = urllib.request.urlopen(req, context=SSL_CONTEXT)
        return json.loads(resp.read())

    @classmethod
    def get_blockchain_state(cls):
        return cls._send_request(f"{cls.BASE_URI}/get_blockchain_state")


    @classmethod
    def get_connections(cls):
        return cls._send_request(f"{cls.BASE_URI}/get_connections")


    @classmethod
    def open_connection(cls, addr):
        host, port = addr.rsplit(":", 1)

        payload = {
            "host": host,
            "port": port
        }

        return cls._send_request(f"{cls.BASE_URI}/open_connection", payload=payload)



if __name__ == "__main__":
    import pprint

    pprint.pprint(ChiaAPI.get_connections())
