from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant

from web3 import Web3, EthereumTesterProvider


class InstrumentedContract(RuleBasedStateMachine):
    interface = None
    """
    This class injects @rule decorators for calling
    state-modifying functions with hypothesis strategies
    for the relevant data types from the contract's ABI
    """

    def __init__(self, *args, **kwargs):
        assert self.interface is not None
        w3 = Web3(EthereumTesterProvider())
        txn_hash = w3.eth.contract(**self.interface).constructor().transact()
        address = w3.eth.waitForTransactionReceipt(txn_hash)['contractAddress']
        contract = w3.eth.contract(address, **self.interface)
        self._contract = contract
        super().__init__(*args, **kwargs)

    @property
    def gate1_down(self):
        return self._contract.functions.gate1_down().call()

    @property
    def gate2_down(self):
        return self._contract.functions.gate2_down().call()

    @rule(choose_gate1=st.booleans())
    def raise_gate(self, choose_gate1):
        try: # May fail, but that's okay because failure means it was caught!
            self._contract.functions.raise_gate(choose_gate1).transact()
        except Exception as e:
            pass

    @rule(choose_gate1=st.booleans())
    def lower_gate(self, choose_gate1):
        try: # May fail, but that's okay because failure means it was caught!
            self._contract.functions.lower_gate(choose_gate1).transact()
        except Exception as e:
            pass
