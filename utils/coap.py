"""
    utils/coap.py

    by Luke Lee
"""

from coapthon.client.helperclient import HelperClient


def req_coap(host, op, payload):
    port = 5683  # CoAP uses this port
    path = 'game'

    client = HelperClient(server=(host, port))

    if op == 'GET':
        resp = client.get(path)
    elif op == 'POST':
        resp = client.post(path, payload)
    elif op == 'PUT':
        resp = client.put(path, payload)
    else:
        raise Exception('Invalid option')

    client.stop()
    return resp
