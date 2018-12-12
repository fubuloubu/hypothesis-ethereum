import pytest
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

from web3 import Web3, EthereumTesterProvider
import vyper


with open('canal-lock.vy', 'r') as f:
    interface = vyper.compile_code(f.read(), \
            output_formats=['abi', 'bytecode', 'bytecode_runtime'])


class CanalLockProblem(RuleBasedStateMachine):
    def __init__(self, *args, **kwargs):
        w3 = Web3(EthereumTesterProvider())  # Clean chain
        txn_hash = w3.eth.contract(**interface).constructor().transact()
        address = w3.eth.waitForTransactionReceipt(txn_hash)['contractAddress']
        self.canal_lock = w3.eth.contract(address, **interface)
        super().__init__(*args, **kwargs)

    @rule(choose_gate1=st.booleans())
    def raise_gate(self, choose_gate1):
        try: # May fail, but that's okay!
            self.canal_lock.functions.raise_gate(choose_gate1).transact()
        except Exception as e:
            pass

    @rule(choose_gate1=st.booleans())
    def lower_gate1(self, choose_gate1):
        try: # May fail, but that's okay!
            self.canal_lock.functions.lower_gate(choose_gate1).transact()
        except Exception as e:
            pass

    @invariant()
    def both_gates_never_down(self):
        assert (not self.canal_lock.functions.gate1().call() or \
                not self.canal_lock.functions.gate2().call()
            )


CanalLockTest = CanalLockProblem.TestCase
