"""
    server.py

    by Luke Lee
"""

import argparse
import time

from utils import coap
from utils.contract_manager import ContractManager


class MoteServer:

    def __init__(self, contract_manager):
        self.contract_manager = contract_manager

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
            ret = int(coap.req_coap(ipaddr, 'PUT', 'end').payload)
            self.contract_manager.exec_participatingInGame(i, ret)
            print('- mote #{}: {}'.format(i, ret))
        for j in range(n_sim):
            choice = random.randint(0, 2)
            self.contract_manager.exec_participatingInGame(0, choice)
            print('- simulator: {}'.format(choice))

        # return the results
        winners = self.contract_manager.exec_gameStart().split()
        if self.debug:
            print('Winners:', *winners)
        for i, ipaddr in enumerate(self.motelist, start=1):
            if len(winners) > 0:
                if ipaddr in winners:  # win
                    result = 0
                else:  # lose
                    result = 1
            else:  # draw
                result = 2
            ret = coap.req_coap(
                    ipaddr, 'PUT', 'result {}'.format(result)).payload


def parse_args():
    """
    Parse arguments this program.

    :return: parsed arguments
    """

    parser = argparse.ArgumentParser(
            description='Server-side of the application')
    parser.add_argument(
            '--motelist', default='motelist.txt',
            help='The path of the file listing motes\' IPv6 address')
    parser.add_argument(
            '--rpc_url', default='http://localhost:8123',
            help='HTTP URL where the RPC server can be found')
    parser.add_argument(
            '--rpc_pw', default='heiler',
            help='Passphrase for the zeroth account')
    parser.add_argument(
            '--contract_code', default='game_contract.sol',
            help='The path of the contract\'s source code')
    parser.add_argument(
            '--contract_addr',
            help='Address at which the contract is placed')
    parser.add_argument(
            '--n_sim', type=int, default=2,
            help='Number of simulators participating in game')

    return parser.parse_args()


def main(args):
    print('Tetris', end='\n\n')

    contract_manager = ContractManager(
            args.rpc_url, args.rpc_pw, args.contract_code)
    contract_manager.load_contract(args.contract_addr)

    mote_server = MoteServer(contract_manager)
    mote_server.load_motelist(args.motelist)

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
