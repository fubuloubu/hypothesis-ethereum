from hypothesis import strategies as st
from hypothesis.stateful import GenericStateMachine

from eth_abi.tools import get_abi_strategy
from eth_tester.exceptions import TransactionFailed

from web3 import Web3, EthereumTesterProvider


def deploy_contract(interface):
    w3 = Web3(EthereumTesterProvider())
    txn_hash = w3.eth.contract(**interface).constructor().transact()
    address = w3.eth.waitForTransactionReceipt(txn_hash)['contractAddress']
    return w3.eth.contract(address, **interface)


def build_call_strategies(contract):
    state_modifying_functions = \
            [f for f in contract.all_functions() if not f.abi['constant']]
    for fn in state_modifying_functions:
        args_strategy = [get_abi_strategy(arg['type']) for arg in fn.abi['inputs']]
        yield st.builds(fn, *args_strategy)


def build_test(interface, invariants):
    """
    """
    # TODO Validate interface
    # TODO Validate invariant functions

    class InstrumentedContract(GenericStateMachine):

        def __init__(self):
            # Deploy contract
            # TODO Handle deploying contracts w/ constructor args
            self._contract = deploy_contract(interface)

            # Initialize GenericStateMachine
            super(InstrumentedContract, self).__init__()

        def steps(self):
            # Generate call strategies
            # TODO Maybe cache this?
            return st.one_of(*build_call_strategies(self._contract))

        def execute_step(self, step):
            try:
                step.transact()
            except TransactionFailed:
                # May fail, but that's okay because failure means it was caught!
                pass
            # TODO Handle OutOfGas
            # TODO Handle InvalidOpcode
            # TODO Handle other exceptional scenarios

        def check_invariants(self):
            [inv(self._contract) for inv in invariants]

    return InstrumentedContract.TestCase
