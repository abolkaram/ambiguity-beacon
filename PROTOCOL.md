# Protocol notes

## Participants

The author supplies the rule boundary. Two named readers supply independent readings. GenLayer validators compare those readings. Any wallet may trigger comparison after both readings are present.

## Fork signal

The consensus result contains a material-divergence boolean plus clause and example indexes. Example outcome disagreement is objective, so the contract unions every differing outcome index into the validator result before storing it.

## Repair signal

A clarification is not accepted merely because it sounds clearer. Validators must independently confirm two separate properties: it preserves the original boundary and it resolves all stored divergences. Attempts remain visible and are capped.

## Why indexes matter

The contract stores bounded source arrays once, then refers to them by validated indexes. Reviewers can reconstruct every result without trusting an unbounded narrative produced by a model.

