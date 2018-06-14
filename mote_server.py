"""
    mote_server.py

    by Luke Lee
"""

import argparse
import time
import socket
import random

from utils import coap


class MoteServer:

    def __init__(self, bufsize=4096, debug=True):
        self.bufsize = bufsize
        self.debug = debug

    def load_motelist(self, motelist_path):
        """
        Load the IPv6 addresses of the motes to a list.

        :param motelist_path: path of the text file that contains the IP
            addresses
        :return: None
        """

        with open(motelist_path, 'r') as f:
            self.motelist = [s.strip() for s in f.readlines()]

        # check if the listed motes are alive
        for ipaddr in self.motelist:
            self._hello_mote(ipaddr)
        print()

    def _hello_mote(self, ipaddr):
        """
        Check if the mote is reachable.

        :param ipaddr: IPv6 address of the mote
        :return: None
        """

        ret = coap.req_coap(ipaddr, 'PUT', 'hello').payload
        print('{}: {}'.format(
                ipaddr, ret if ret is not None else 'Failed'))

    def create_connection(self, addr, port):
        self.server_sock = socket.create_connection((addr, port))
        if self.debug:
            print('Connected to {}:{}'.format(addr, port))

    def start_game(self, n_sim=2):
        """
        Start the game.

        :param n_sim: number of simulators participaing in game
        :return: None
        """

        # start the game
        for ipaddr in self.motelist:
            ret = coap.req_coap(ipaddr, 'PUT', 'start').payload

        time.sleep(10)

        # finish the game
        if self.debug:
            print('Submitted results')
        for i, ipaddr in enumerate(self.motelist, start=1):
            choice = 'RGB'.index(coap.req_coap(ipaddr, 'PUT', 'end').payload)
            self.server_sock.send(bytes(
                    'participatingInGame {} {}'.format(i, choice), 'utf-8'))
            ret = self.server_sock.recv(self.bufsize)
            if self.debug:
                print('- mote #{}: {}'.format(i, choice))
                print('  =>', str(ret, 'utf-8'))
        for j in range(n_sim):
            choice = random.randint(0, 2)
            self.server_sock.send(bytes(
                    'participatingInGame {} {}'.format(0, choice), 'utf-8'))
            ret = self.server_sock.recv(self.bufsize)
            if self.debug:
                print('- simulator: {}'.format(choice))
                print('  =>', str(ret, 'utf-8'))

        # return the results
        self.server_sock.send(b'gameStart')
        ret = self.server_sock.recv(self.bufsize)
        print('=>', str(ret, 'utf-8'))
        self.server_sock.send(b'exit')


def parse_args():
    """
    Parse arguments this program.

    :return: parsed arguments
    """

    parser = argparse.ArgumentParser(
            description='Mote part of the server')
    parser.add_argument(
            '--addr',
            help='Address of the web3 part')
    parser.add_argument(
            '--port', type=int, default=20885,
            help='Accepting port number of the web3 part')
    parser.add_argument(
            '--motelist', default='motelist.txt',
            help='File listing motes\' IPv6 address and wallet address')
    parser.add_argument(
            '--n_sim', type=int, default=2,
            help='Number of simulators participating in game')

    return parser.parse_args()


def main(args):
    print('Tetris')
    print('Mote part of the server', end='\n\n')

    mote_server = MoteServer()
    mote_server.load_motelist(args.motelist)
    mote_server.create_connection(args.addr, args.port)

    # start the game
    while True:
        print('Game started')
        mote_server.start_game(n_sim=args.n_sim)

        print('Game ended')
        if input('Continue [Y/n]: ').upper() != 'Y':
            break

    print('Goodbye')


if __name__ == '__main__':
    args = parse_args()
    main(args)
