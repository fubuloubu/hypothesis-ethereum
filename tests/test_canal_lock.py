from brownie.exceptions import VirtualMachineError

from hypothesis import strategies as st
from hypothesis import stateful as sf

def create_test(accounts, rpc, contract_type):
    class ContractTest(sf.RuleBasedStateMachine):
        def __init__(self):
            super(ContractTest, self).__init__()
            self._contract = contract_type.deploy({'from': accounts[0]})
            self._rpc = rpc
            self._rpc.snapshot()

        @sf.initialize()
        def reset_to_deployment(self):
            self._rpc.revert()

        @sf.rule(pick_gate1=st.booleans())
        def raise_gate(self, pick_gate1):
            try:
                self._contract.raise_gate(pick_gate1)
            except VirtualMachineError as e:
                self.reversion_check(e)

        @sf.rule(pick_gate1=st.booleans())
        def lower_gate(self, pick_gate1):
            try:
                self._contract.lower_gate(pick_gate1)
            except VirtualMachineError as e:
                self.reversion_check(e)

        def reversion_check(self, e):
            # Catch exceptional EVM behaviors
            # TODO Better errors raised here
            # NOTE These are errors from py-evm
            #assert not isinstance(e.__cause__, InvalidInstruction)
            #assert not isinstance(e.__cause__, (InsufficientStack, FullStack, StackDepthLimit))
            #assert not isinstance(e.__cause__, InvalidJumpDestination)
            #assert not isinstance(e.__cause__, InsufficientFunds)
            #assert not isinstance(e.__cause__, OutOfGas)
            #assert not isinstance(e.__cause__, WriteProtection)
            # May revert, but that's okay because reverting means preconditions caught it!
            assert e.revert_msg != "out of gas"  # TODO https://github.com/iamdefinitelyahuman/brownie/issues/330
            

        @sf.invariant()
        def my_custom_invariant(self):
            # Everything above and below this line can be automatically generated from the ABI
            assert not self._contract.gate1_down() or not self._contract.gate2_down()

    return ContractTest.TestCase


if __name__ == '__main__':
    from brownie import network
    from brownie.network import rpc, accounts
    network.connect('development')

    from brownie import project
    HypothesisBrownieProject = project.load()

    hack = create_test(accounts, rpc, HypothesisBrownieProject.CanalLock)
    import unittest
    unittest.main()
