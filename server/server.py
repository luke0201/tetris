"""
    server.py

    by Luke Lee
"""

import sys
import time
import socket

from utils import coap


class MoteServer:

    def __init__(self):
        pass

    def load_motelist(self, motelist_path):
        """
        Load the IPv6 addresses of the motes to a list

        :param motelist_path: path of the text file that contains the IP addresses
        :return: None
        """

        with open(motelist_path, 'r') as f:
            self.motelist = [s.strip() for s in f.readlines()]

        for ipaddr in self.motelist:
            self._hello_mote(ipaddr)
        print()

    def _hello_mote(self, ipaddr):
        ret = coap.req_coap(ipaddr, 'GET', 'hello').payload
        print('{}: {}'.format(
                ipaddr, ret if ret is not None else 'Failed'))

    def start_game(self):
        """
        Start the game

        :return: None
        """

        # start the game
        for ipaddr in self.motelist:
            ret = coap.req_coap(ipaddr, 'GET', 'start').payload

        time.sleep(10)

        # finish the game
        for ipaddr in self.motelist:
            ret = coap.req_coap(ipaddr, 'GET', 'end').payload

        # return the results
        result = dict()
        for ipaddr in self.motelist:
            result[ipaddr] = '1'
            ret = coap.req_coap(ipaddr, 'GET', 'result {}'.format(result[ipaddr])).payload


def main(argv):
    # variables
    MOTELIST_PATH = 'motelist.txt'

    print('Tetris', end='\n\n')

    mote_server = MoteServer()
    mote_server.load_motelist(MOTELIST_PATH)

    # start the game
    while True:
        print('Game started')
        mote_server.start_game()

        print('Game ended')
        if input('Continue [Y/n]: ',).lower() == 'n':
            break

    print('Goodbye')
    

if __name__ == '__main__':
    main(sys.argv)
