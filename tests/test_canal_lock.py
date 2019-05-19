import vyper

with open('tests/CanalLock.vy', 'r') as f:
    code = f.read()
    good_interface = vyper.compile_code(code,
            output_formats=['abi', 'bytecode', 'bytecode_runtime'])
    code = code.replace(
            'assert not self.gate2_down  # CHANGE ME',
            'assert self.gate2_down  # CHANGED!',
        )
    bad_interface = vyper.compile_code(code,
            output_formats=['abi', 'bytecode', 'bytecode_runtime'])


# This is how the public API should be used
from hypothesis_ethereum import build_test


def check_gates_both_down(contract):
    assert not (
            contract.functions.gate1_down().call() and \
            contract.functions.gate2_down().call()
        )


PassCanalLockTest = build_test(good_interface, [check_gates_both_down])
FailCanalLockTest = build_test(bad_interface, [check_gates_both_down])
