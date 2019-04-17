import pytest

import vyper

from hypothesis_ethereum import InstrumentedContract, invariant


interface = vyper.compile_code("""
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
""", output_formats=['abi', 'bytecode', 'bytecode_runtime'])


class CanalLockProblem(InstrumentedContract):
    def __init__(self):
        super().__init__(interface)

    @invariant()
    def gates_both_down(self):
        gate1_down = self._contract.functions.gate1().call()
        gate2_down = self._contract.functions.gate2().call()
        assert not (gate1_down and gate2_down)

CanalLockTest = CanalLockProblem.TestCase
