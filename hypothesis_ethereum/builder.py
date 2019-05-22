from hypothesis import strategies as st
from hypothesis.stateful import GenericStateMachine

from eth_abi.tools import get_abi_strategy
from eth_tester.exceptions import TransactionFailed

from web3 import Web3, EthereumTesterProvider


def _deploy_contract(w3, interface):
    txn_hash = w3.eth.contract(**interface).constructor().transact()
    address = w3.eth.waitForTransactionReceipt(txn_hash)['contractAddress']
    return w3.eth.contract(address, **interface)


def _validate_invariant(w3, interface, invariant):
    contract = _deploy_contract(w3, interface)
    # TODO Detect if invariant modifies state, bad!
    snapshot = w3.testing.snapshot()
    try:
        invariant(contract)
    except e:
        raise e  # TODO Handle this, give better error
    finally:
        w3.testing.revert(snapshot)


def _validate_interface(interface):
    interface_members = interface.keys()
    if len(interface_members) != 3:
        raise ValueError("Interface must have 3 members!")
    if 'abi' not in interface_members:
        raise ValueError("Interface does not have ABI!")
    if 'bytecode' not in interface_members:
        raise ValueError("Interface does not have Binary!")
    if 'bytecode_runtime' not in interface_members:
        raise ValueError("Interface does not have Runtime!")


def build_call_strategies(contract):
    state_modifying_functions = \
            [f for f in contract.all_functions() if not f.abi['constant']]
    for fn in state_modifying_functions:
        args_strategy = [get_abi_strategy(arg['type']) for arg in fn.abi['inputs']]
        yield st.builds(fn, *args_strategy)


def build_test(interface):
    # Ensure we have a valid interface dict
    _validate_interface(interface)

    def test_builder(invariant):
        """
        """
        # Create a Web3/Testnet object per testcase
        w3 = Web3(EthereumTesterProvider())
        _validate_invariant(w3, interface, invariant)

        class InstrumentedContract(GenericStateMachine):

            def __init__(self):
                # Deploy contract
                # TODO Handle deploying contracts w/ constructor args
                self._contract = _deploy_contract(w3, interface)

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
                invariant(self._contract)

        return InstrumentedContract.TestCase

    return test_builder
