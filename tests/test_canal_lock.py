import pytest
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

from web3 import Web3, EthereumTesterProvider
import vyper


code = """
gate1: public(bool) # False = Up (stopping water), True = Down (letting water through)
gate2: public(bool) # False = Up (stopping water), True = Down (letting water through)

@public
def raise_gate(pick_gate1: bool):
    if pick_gate1:
        self.gate1 = False # Raise up, stopping the flow of water
    else:
        self.gate2 = False # Raise up, stopping the flow of water

@public
def lower_gate(pick_gate1: bool):
    if pick_gate1: # Gate 2 cannot
        # Both gates can not be lowered at the same time
        assert not self.gate2
        self.gate1 = True # Lower down, allowing the flow of water
    else:
        # Both gates can not be lowered at the same time
        assert not self.gate1
        self.gate2 = True # Lower down, allowing the flow of water
"""
interface = vyper.compile_code(code, \
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
