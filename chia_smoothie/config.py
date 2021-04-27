import json
import logging

import urllib3
urllib3.disable_warnings()

CFG = None

root_logger = logging.getLogger("chia_smoothie")
logging.basicConfig(level=logging.INFO)


def reload():
    global CFG

    with open("chia_smoothie.json", "r") as fd:
        CFG = json.loads(fd.read())


reload()
