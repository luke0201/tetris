"""
    contract_manager.py

    by Luke Lee
"""

import time
import argparse
import json

import web3
import solc


class ContractManager:

    def __init__(self, rpc_url, rpc_acc_pw, contract_path, debug=False):
        self.debug = debug
        self.w3 = self._init_web3(rpc_url)
        self.contract_interface = self._compile_contract(contract_path)
        self.contract_addr = None

    def _init_web3(self, rpc_url):
        """
        Initialize Web3 and unlock the zeroth account.

        :param rpc_url: HTTP URL where the RPC server can be found
        :return: Web3 object
        """

        w3 = web3.Web3(web3.HTTPProvider(rpc_url))
        if self.debug:
            print('Initialized Web3')
        return w3

    def unlock(self, idx, passwd):
        """
        Unlock the idx'th account.

        :param idx: account index
        :param passwd: passphrase for the account
        :return: None
        """
        self.w3.personal.unlockAccount(self.w3.eth.accounts[idx], passwd, 0)

    def _compile_contract(self, contract_path):
        """
        Compile the contract source code.

        :param contract_path: path in which the contract source code resides
        :return: contract interface
        """

        with open(contract_path, 'r') as f:
            contract_code = f.read()
        compiled_sol = solc.compile_source(contract_code)
        if self.debug:
            print('Compiled the contract source code')

        return compiled_sol['<stdin>:RockScissorPaper']

    def get_abi(self):
        """
        Return the ABI of the compiled contract.

        :return: ABI
        """
        return self.contract_interface['abi']

    def deploy_contract(self):
        """
        Deploy the compiled contract to the block chain.
        The interface of the contract is stored in self.contract_interface.

        :return: None
        """

        contract = self.w3.eth.contract(
                abi=self.contract_interface['abi'],
                bytecode=self.contract_interface['bin'],
                bytecode_runtime=self.contract_interface['bin-runtime'])

        trans_hash = contract.deploy(
                transaction={'from': self.w3.eth.accounts[0]})
        self._mine_block()  # an Ethereum block needs to be mined to deploy

        trans_receipt = self.w3.eth.getTransactionReceipt(trans_hash)
        self.contract_addr = trans_receipt['contractAddress']
        if self.debug:
            print('Deployed the contract to the chain')
            print('  Hash:', trans_hash)
            print('  Address:', self.contract_addr)

    def load_contract(self, contract_addr):
        """
        Load the contract object to self.contract.
        Use this method if you have already deployed the contract.

        :param contract_addr: address of the contract in block chain
        :return: contract object
        """

        self.contract_addr = contract_addr
        if self.debug:
            print('Loaded contract from', contract_addr)

    def exec_participatingInGame(self, sender_idx, choice, betting_ether=10):
        """
        Execute participatingInGame from the deployed contract.

        :param sender_idx: index of the participant
        :param betting_ether: how much to bet in Ether
        :return: from the specified function (participatingInGame(choice))
        """

        # there should be a contract, either deployed or loaded
        if self.contract_addr is None:
            raise Exception('Contract not loaded!')
        contract = self.w3.eth.contract(
                self.contract_addr, abi=self.contract_interface['abi'])

        # execute participatingInGame
        func = contract.functions.participatingInGame(choice)
        trans = {
                'from': self.w3.eth.accounts[sender_idx],
                'to': self.contract_addr,
                'value': self.w3.toWei(betting_ether, 'ether')}
        func.transact(trans)  # make a transaction
        self._mine_block()
        if self.debug:
            print('Executed participaingInGame with {} ether'.format(
                    betting_ether))
        return func.call(trans)  # return the function's return value

    def exec_gameStart(self):
        """
        Execute gameStart from the deployed contract.

        :return: from the specified function (gameStart())
        """

        # there should be a contract, either deployed or loaded
        if self.contract_addr is None:
            raise Exception('Contract not loaded!')
        contract = self.w3.eth.contract(
                self.contract_addr, abi=self.contract_interface['abi'])

        # execute gameStart
        func = contract.functions.gameStart()
        trans = {
                'from': self.w3.eth.accounts[0],
                'to': self.contract_addr}
        func.transact(trans)  # make a transaction
        self._mine_block()
        if self.debug:
            print('Executed gameStart')
        return func.call(trans)  # return the function's return value

    def _mine_block(self, sec=8, n_threads=1):
        """
        Mine an Ethereum block.

        :param sec: how long to mine in seconds
        :param n_threads: how many threads to use for mining
        :return: None
        """

        if self.debug:
            print('Mining blocks..', end=' ')
        self.w3.miner.start(n_threads)
        time.sleep(sec)
        self.w3.miner.stop()
        if self.debug:
            print('Done')


def parse_args():
    """
    Argument parser for this program.

    :return: parsed arguments
    """

    parser = argparse.ArgumentParser(
            description='Deploy and execute the smart contract')
    parser.add_argument(
            '--deploy', action='store_true',
            help='Compile and deploy a new contract')
    parser.add_argument(
            '--load', default=None,
            help='Address at which the contract is deployed')
    parser.add_argument(
            '--print_abi', default=None,
            help='Print ABI to output file')
    parser.add_argument(
            '--execute', action='store_true',
            help='Execute the function participaingInGame from the contract')
    parser.add_argument(
            '--rpc_url', default='http://localhost:8123',
            help='HTTP URL where the RPC server can be found')
    parser.add_argument(
            '--rpc_pw', default='heiler',
            help='Passphrase for the zeroth account')
    parser.add_argument(
            '--contract_code', default='game_contract.sol',
            help='Path in which the contract source code resides')

    return parser.parse_args()


def main(args):
    contract_manager = ContractManager(
            args.rpc_url, args.rpc_pw, args.contract_code, debug=True)
    if args.deploy:
        print('<Deploy a contract>')
        contract_manager.deploy_contract()
        print()
    elif args.load:
        print('<Load an existing contract>')
        contract_manager.load_contract(args.load)
        print()
    if args.print_abi:
        with open(args.print_abi, 'w') as f:
            json.dump(contract_manager.get_abi(), f, indent=2)
    if args.execute:
        print('<Execute a function from the contract>')
        contract_manager.exec_participatingInGame(0, 1)  # bet 10 ether
        print()
    print('Goodbye')


if __name__ == '__main__':
    args = parse_args()
    main(args)
