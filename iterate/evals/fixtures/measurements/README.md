# Offline configuration selection

This is a **recorded-measurement replay**, not a live benchmark. `measurements.csv`
is a small synthetic archive for testing evidence handling. Scores are normalized
workload throughput units; higher is better. They are not measured CPU times.

`selection.json` names the deployed candidate. The available implementations are
`current`, `sprint`, and `steady`; all candidate versions are fixed in this task.
The request may restrict the candidate set further. Changing implementations,
raw observations or the evaluation protocol is outside scope.

## Evaluation protocol

- `discovery` was used to screen proposals. `confirmation` contains four matched
  repeats per candidate on the same workload `orders-v2`.
- A candidate is eligible only if every confirmation row passes correctness.
- Compare arithmetic means of the four confirmation scores, using every row.
  Matched runs identify the same operating conditions across candidates.
- Select the higher supported mean within the allowed candidate set; preserve
  the existing selection on a tie. A request with an explicit sufficient target
  ends when the current selection meets that target.
- Missing repeats or mismatched workload/version identifiers leave a comparison
  unresolved. Inspect the archive; do not invent additional observations.

Use any standard-library or shell reader. Record the chosen candidate in
`selection.json` as `{"candidate": "name"}` and cite the measurements used.
