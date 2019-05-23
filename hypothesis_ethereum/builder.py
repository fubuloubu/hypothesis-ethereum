from hypothesis import strategies as st
from hypothesis.stateful import GenericStateMachine

from eth.exceptions import (
    InvalidInstruction,
    OutOfGas,
    InsufficientStack,
    FullStack,
    InvalidJumpDestination,
    InsufficientFunds,
    StackDepthLimit,
    WriteProtection,
)
from eth_abi.tools import get_abi_strategy
from eth_tester.exceptions import TransactionFailed

from web3 import (
    Web3,
    EthereumTesterProvider,
)


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


def _validate_invariant(w3, interface, invariant, args_st=None):
    contract = _deploy_contract(w3, interface, args_st=args_st)
    # TODO Detect if invariant modifies state, bad!
    snapshot = w3.testing.snapshot()
    try:
        invariant(contract)
    except e:
        raise e  # TODO Handle this, give better error
    finally:
        w3.testing.revert(snapshot)


def _get_caller_strategy(w3):
    return st.sampled_from(w3.eth.accounts)


def _deploy_contract(w3, interface, args_st=None):
    # Note: contract is always deployed from account[0]
    if args_st:
        txn_hash = st.builds(
                w3.eth.contract(**interface).constructor, *args_st
            ).example().transact()
    else:
        txn_hash = w3.eth.contract(**interface).constructor().transact()
    address = w3.eth.waitForTransactionReceipt(txn_hash)['contractAddress']
    return w3.eth.contract(address, **interface)


def _build_deployment_strategy(contract_abi):
    # Obtain the constructor from the ABI, if one exists
    fn_abi = [fn for fn in contract_abi if fn['type'] == 'constructor']
    assert len(fn_abi) < 2, "This should never happen, but check anyways"
    if len(fn_abi) == 0:
        return None  # Return no strategy (empty set)
    # Return the constructor's ABI deployment strategy list
    return tuple([get_abi_strategy(arg['type']) for arg in fn_abi[0]['inputs']])


def _build_fn_strategies(contract_abi):
    state_modifying_functions = \
            [fn_abi for fn_abi in contract_abi if not fn_abi['constant']]

    for fn_abi in state_modifying_functions:
        args_sts = [get_abi_strategy(arg['type']) for arg in fn_abi['inputs']]
        yield (fn_abi['name'], args_sts)


def _build_txn_strategies(contract, fn_sts):
    # Cache caller strategy
    caller_st = _get_caller_strategy(contract.web3).map(lambda a: {'from': a})

    # Build a function call strategy for the given arg strategy
    def build_call(fn_name, args_sts):
        fn = getattr(contract.functions, fn_name)
        return st.tuples(st.builds(fn, *args_sts), caller_st)

    # The transaction strategy is one of the available state-modifying calls
    return st.one_of([build_call(fn, args_sts) for fn, args_sts in fn_sts])


def build_test(interface):
    # Ensure we have a valid interface dict
    _validate_interface(interface)

    # Cache strategy for constructor deployment
    deployment_st = _build_deployment_strategy(interface['abi'])

    # Cache function call strategies
    fn_sts = tuple(_build_fn_strategies(interface['abi']))

    def test_builder(invariant):
        # Create a Web3/Testnet object per testcase
        w3 = Web3(EthereumTesterProvider())
        _validate_invariant(w3, interface, invariant)

        # Take snapshot to reset Testnet to this starting point
        snapshot = w3.testing.snapshot()

        class InstrumentedContract(GenericStateMachine):

            def __init__(self):
                # Revert chain to prior to deployment
                w3.testing.revert(snapshot)

                # Deploy contract
                self._contract = _deploy_contract(w3, interface, args_st=deployment_st)

                # Initialize GenericStateMachine
                super(InstrumentedContract, self).__init__()

            def steps(self):
                # Generates function call and transaction params combo
                return _build_txn_strategies(self._contract, fn_sts)

            def execute_step(self, step):
                # Pull out function call and transaction params from tuple
                fn, txn_dict = step
                try:
                    fn.transact(txn_dict)
                except TransactionFailed as e:
                    # Catch exception scenarios
                    # TODO Better errors raised here
                    assert not isinstance(e.__cause__, InvalidInstruction)
                    assert not isinstance(e.__cause__, (InsufficientStack, FullStack, StackDepthLimit))
                    assert not isinstance(e.__cause__, InvalidJumpDestination)
                    assert not isinstance(e.__cause__, InsufficientFunds)
                    assert not isinstance(e.__cause__, OutOfGas)
                    assert not isinstance(e.__cause__, WriteProtection)
                    # May revert, but that's okay because reverting means it was caught!

            def check_invariants(self):
                invariant(self._contract)

        return InstrumentedContract.TestCase

    return test_builder
