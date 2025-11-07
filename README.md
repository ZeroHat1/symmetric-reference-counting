# Reference Counting without Cycles

This repository documents and explores a novel approach to reference counting that eliminates cyclic references without traditional tracing GC.

## Articles
- [Dev.to](https://dev.to/zerohat/symmetric-reference-counting-how-to-eliminate-cycles-without-a-garbage-collector-151f)

## Idea Summary
In traditional reference counting, cycles occur when two objects reference each other.  
This approach introduces a non-cascade reference ownership model that guarantees O(1) collection without traversal.

## Experiments
```bash
python prototype/test.py
