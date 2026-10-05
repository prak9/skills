# Synthetic validation report

This package demonstrates evidence-linked delivery; it contains invented test data, not live research. Its semantic checks are author self-review. The checker verifies package integrity, not truth.

## Count change

The supplied count grew from 100 to 125, a 25% increase, calculated as `(125-100)/100*100`: [C1](claims.csv), [N1](numbers.csv), [source counts](sources/s01.md#counts). This is exact within the fixture and says nothing about a wider population.

## Latency claim

The broad proposition [C2](claims.csv) is contested: [run A](sources/s01.md#latency) reports lower latency, while [run B](sources/s02.md#latency) reports higher latency on a different workload. A universal improvement is not supported. The records lack repeated runs, magnitudes and uncertainty estimates; they cannot establish the average effect or its cause.

## What would change the conclusion

Comparable repeated measurements across the intended workload population could support a narrower conditional claim. That experiment was not run here. No real user choice or deployment is implied.
