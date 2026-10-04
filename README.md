# Ambiguity Beacon

Two careful readers can follow the same rule and still reach different answers. This contract turns that hidden fork into an indexed, reviewable signal before the rule is relied upon.

## Beacon watch

**REGISTERED**  The author freezes a rule, numbered clauses, boundary examples, and two independent readers.

**READING**  Each reader submits a plain interpretation, the clause indexes they relied on, and an `ALLOW`, `DENY`, or `UNCLEAR` answer for every example.

**READY**  Both readings exist. Neither reader can edit the other's account.

**ALIGNED / AMBIGUOUS**  Permissionless comparison combines validator judgment with a deterministic backstop: any different example outcome is always included in the divergence set.

**CLARIFIED / UNRESOLVED**  The author may try a bounded clarification. Validators must confirm that it preserves the original boundary and resolves every recorded fork.

## What consensus may decide

Validators decide whether the interpretations materially diverge and identify clause and example indexes. They do not return an authoritative prose ruling. The contract independently normalizes indexes, enforces bounds, and adds every objective outcome difference that consensus omitted.

## What the contract decides

- Three wallets are distinct: author, reader A, reader B.
- Every example receives exactly one normalized outcome from each reader.
- Clause references are unique, sorted, and in range.
- Clarification attempts are capped at three.
- `CLARIFIED` requires both preservation and complete resolution.
- Validator output is accepted only by full structural equality.

## Files for reviewers

- [`contracts/contract.py`](contracts/contract.py): reusable primitive
- [`tests/direct/test_beacon.py`](tests/direct/test_beacon.py): six adversarial scenarios
- [`PROTOCOL.md`](PROTOCOL.md): state and trust model
- [`deployment.json`](deployment.json): exact StudioNet deployment
- [`evidence/live-record.json`](evidence/live-record.json): transaction-backed readback

There is deliberately no frontend. Ambiguity Beacon is submitted as an Intelligent Contract building block.

