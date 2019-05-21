# Hypothesis Integration for Ethereum Smart Conctracts
Tests are executed using pytest

https://hypothesis.works/articles/how-not-to-die-hard-with-hypothesis/
https://hypothesis.readthedocs.io/en/latest/stateful.html

## How this fuzzer works

This fuzzer engine takes a compiled contract, and leverages the ABI to figure out the "call space" of the contract.
The call space is basically the externally available contract methods that allow modifications to the underlying state.
Each method's call space is further parameterized by each method's input variables, so the total call space is
essentially all available state-modifying methods with all possible combinations of input variables.
With Ethereum contracts containing very large variables such as 256-bit integers, this can be really large!

A fuzzer usually randomly samples from the call space to reduce the amount of calls being made, which drastically
reduces the amount of time and resources used to explore the call space. This fuzzer engine in particular tries a
series of calls from the call space in an attempt to find exceptional scenarios that is of interest to the user.

This fuzzer engine checks for the following exceptional scenarios:
1. Out of Gas exception (using a configurable limit)
2. Unintended reversions, such as Invalid opcodes, Stack Overflow/Underflow, Invalid Jump Destination, or Insufficient Funds.
3. Custom invariants, as specified by the user using the contract's public read-only API

## Soundness vs. Completeness

This fuzzer is "sound" but not "complete".
If you are unfamiliar with these concepts, this basically means that fuzzer tests may not completely
identify all bugs (due to randomly exploring the contract's call space), but any bug it *does* find
is a "real" bug that exists in the application (the fact that it is a bug is soundly identified).

Future work will be done in shrinking the contract's call space through "grey box" techniques,
or in other words introspecting the contract to identify parts of the call space that might reveal a bug,
and focusing on those portions to identify bugs faster. In this way, we aim to make the fuzzer's techniques
*more* complete (identify more bugs faster), but without sacrificing soundness (all bugs are still real bugs).
