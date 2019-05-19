import vyper

with open('tests/CanalLock.vy', 'r') as f:
    code = f.read()
    interface = vyper.compile_code(code,
            output_formats=['abi', 'bytecode', 'bytecode_runtime'])


# This is how the public API should be used
from hypothesis_ethereum import build_test


def check_gates_both_down(contract):
    assert not (
            contract.functions.gate1_down().call() and \
            contract.functions.gate2_down().call()
        )


CanalLockTest = build_test(interface, [check_gates_both_down])
