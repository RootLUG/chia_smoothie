import os
import ssl
import json
import urllib.request


certs = (
    os.path.expanduser("~/.chia/mainnet/config/ssl/full_node/private_full_node.crt"),
    os.path.expanduser("~/.chia/mainnet/config/ssl/full_node/private_full_node.key")
)


ssl_context = ssl.create_default_context()
ssl_context.load_cert_chain(certs[0], certs[1])
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


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

        resp = urllib.request.urlopen(req, context=ssl_context)
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
