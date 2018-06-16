"""
    web3_server.py

    by Luke Lee
"""

import argparse
import socket

from utils.contract_manager import ContractManager


class Web3Server:

    def __init__(self, contract_manager, bufsize=4096, debug=True):
        self.contract_manager = contract_manager
        self.bufsize = bufsize
        self.debug = debug

    def init_server(self, host, port):
        """
        Start running the server

        :param port: Port number to be listened to
        """

        # initialize a socket
        server_sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server_sock.bind((host, port))
        server_sock.listen()
        if self.debug:
            print('Start listening to port', port)

        # accept the incoming connection
        while True:
            client_sock, client_addr = server_sock.accept()
            if self.debug:
                print('Connection from', client_addr)

            # communicate with the client
            while True:
                msg = str(client_sock.recv(self.bufsize), 'utf-8').split()
                oper, params = msg[0], msg[1:]
                if oper == 'exit':
                    break
                if oper == 'participatingInGame':
                    if len(params) != 2:
                        client_sock.send(
                                b'invalid number of parameters (need 2)')
                    else:
                        self.contract_manager.exec_participatingInGame(
                                int(params[0]), int(params[1]))
                        client_sock.send(b'Done')
                elif oper == 'gameStart':
                    if len(params) != 0:
                        client_sock.send(
                                b'invalid number of parameters (need 0)')
                    else:
                        self.contract_manager.exec_gameStart()
                        client_sock.send(b'Done')
                else:  # unrecognized operation
                    client_sock.send(b'unrecognized operation')

            client_sock.close()
            if self.debug:
                print('Communication finished', end='\n\n')

        # close the socket
        server_sock.shutdown()
        server_sock.close()


def parse_args():
    parser = argparse.ArgumentParser(
            description='Block chain part of the server')
    parser.add_argument(
            '--addr',
            help='Address of this host')
    parser.add_argument(
            '--port', type=int, default=20885,
            help='Listening port number to communicate with the mote part')
    parser.add_argument(
            '--motelist', default='motelist.txt',
            help='File listing motes\' IPv6 address and wallet address')
    parser.add_argument(
            '--rpc_url', default='http://localhost:8123',
            help='HTTP URL where the RPC server can be found')
    parser.add_argument(
            '--contract_code', default='game_contract.sol',
            help='The path of the contract\'s source code')
    parser.add_argument(
            '--contract_addr',
            help='Address at which the contract is placed')

    return parser.parse_args()


def main(args):
    print('Tetris')
    print('Block chain part of the server', end='\n\n')

    contract_manager = ContractManager(
            args.rpc_url, args.rpc_pw, args.contract_code)
    contract_manager.load_contract(args.contract_addr)
    # TODO: add accounts

    server = Web3Server(contract_manager)
    server.init_server(args.addr, args.port)


if __name__ == '__main__':
    args = parse_args()
    main(args)
