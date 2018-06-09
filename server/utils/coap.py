"""
    utils/coap.py
    
    by Luke Lee
"""

import sys
import socket

from coapthon.client.helperclient import HelperClient


def req_coap(host, op, payload):
    port = PORT
    path = 'red'

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
