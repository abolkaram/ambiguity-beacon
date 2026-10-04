# Verification ledger

| Gate | Result |
|---|---|
| GenVM lint | PASS |
| Contract schema | PASS, 7 methods |
| Role separation scenarios | authored |
| Forged-equivalence validator scenario | authored |
| Objective-divergence backstop scenario | authored |
| StudioNet lifecycle | pending deployment record |

The installed Windows direct-test runner currently raises `genlayer.py.calldata.DecodingError: unexpected end of memory` before importing both new and previously deployed contracts. This repository does not mislabel that infrastructure failure as a passing test. Network proof is recorded only after finalization and readback.

