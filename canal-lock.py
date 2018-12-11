import pytest
from hypothesis import note, settings
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

    @rule()
    def raise_gate1(self):
        try: # May fail, but that's okay!
            self.canal_lock.functions.raise_gate(True).transact()
        except Exception as e:
            pass

    @rule()
    def raise_gate2(self):
        try: # May fail, but that's okay!
            self.canal_lock.functions.raise_gate(False).transact()
        except Exception as e:
            pass

    @rule()
    def lower_gate1(self):
        try: # May fail, but that's okay!
            self.canal_lock.functions.lower_gate(True).transact()
        except Exception as e:
            pass

    @rule()
    def lower_gate2(self):
        try: # May fail, but that's okay!
            self.canal_lock.functions.lower_gate(False).transact()
        except Exception as e:
            pass

    @invariant()
    def both_gates_down(self):
        note("> gate1: {} gate2: {}".\
                format(self.canal_lock.functions.gate1().call(),
                       self.canal_lock.functions.gate2().call()
                    )
            )
        assert (not self.canal_lock.functions.gate1().call() or \
                not self.canal_lock.functions.gate2().call()
            )


# The default of 200 is sometimes not enough for Hypothesis to find
# a falsifying example.
with settings(max_examples=2000):
    CanalLockTest = CanalLockProblem.TestCase
