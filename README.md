# Hypothesis Integration for Ethereum Smart Conctracts
Tests are executed using pytest

https://hypothesis.works/articles/how-not-to-die-hard-with-hypothesis/
https://hypothesis.readthedocs.io/en/latest/stateful.html

## How this fuzzer works

This fuzzer engine checks for the following exceptional scenarios:
1. Out of Gas exception (using a configurable limit)
2. Unintended reversions, such as Invalid opcodes, Stack Overflow/Underflow, Invalid Jump Destination, or Insufficient Funds.
3. Custom invariants, as specified by the user using the contract's public read-only API
