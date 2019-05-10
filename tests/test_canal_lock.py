import pytest

import vyper

from hypothesis_ethereum import InstrumentedContract, invariant


interface = vyper.compile_code("""
gate1_down: public(bool) # False = Up (stopping water), True = Down (letting water through)
gate2_down: public(bool) # False = Up (stopping water), True = Down (letting water through)

@public
def raise_gate(pick_gate1: bool):
    if pick_gate1:
        self.gate1_down = False # Raise up, stopping the flow of water
    else:
        self.gate2_down = False # Raise up, stopping the flow of water

@public
def lower_gate(pick_gate1: bool):
    if pick_gate1: # Gate 2 cannot
        # Both gates can not be lowered at the same time
        assert not self.gate2_down
        self.gate1_down = True # Lower down, allowing the flow of water
    else:
        # Both gates can not be lowered at the same time
        assert not self.gate1_down
        self.gate2_down = True # Lower down, allowing the flow of water
""", output_formats=['abi', 'bytecode', 'bytecode_runtime'])


class CanalLockProblem(InstrumentedContract):
    interface = interface

    @invariant()
    def gates_both_down(self):
        assert not (self.gate1_down and self.gate2_down)

CanalLockTest = CanalLockProblem.TestCase
