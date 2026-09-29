# Structural optimization: justify the work omitted

Use when an algorithm change removes part of the search or state space, rather
than merely making the same operations cheaper. Explore alternative formulations
freely; establish their relevant obligations before promoting an exact replacement.
This is not a requirement to mechanize every proof or build a new test platform.

## Preserve the requested answer

Fix the input domain, objective and output contract. Returning an optimum value,
one feasible optimal witness, a particular tie-breaking order, or all optima can
require different information. A transformation may preserve the value while
losing the requested witness. Keep original hard constraints as acceptance gates.

Identify which kind of claim the change supports: exact equivalence, a bound,
an approximation with stated error, or an empirical heuristic. A useful bound or
heuristic does not become an exact solver because it passed sampled tests.

| Change | Obligation carrying correctness | Discriminating check |
| --- | --- | --- |
| Reformulate the problem | Transformed answers map back with valid objectives and constraints; a restricted search retains at least one original optimum, or all requested optima when required | Check the mapping, units, endpoints and witnesses; preserving every feasible solution is unnecessary for an any-optimum task, and a valid mapping does not prove the solver correct |
| Permanently prune candidates | Retained candidates cover the required optimum under every allowed future update, including any required tie behavior | Try a currently inferior candidate that wins later; name the domain or update rule that rules out such a reversal |
| Merge states or share updates | States have compatible future transitions, feasibility and output behavior; any relative offsets remain valid | Give equal current summaries different histories or future inputs; equal current costs, keys or remainders alone do not establish equivalence |
| Replace a hard constraint with a penalty | The target constrained optimum is recoverable at a supported penalty, with the required solution reconstruction | Look for skipped target counts and tied optima; monotonic resource use alone does not prove recovery or absence of a relaxation gap |

Apply only the relevant row. For example, minimizing `V(m) + lambda*m` makes an
optimal count monotone in the penalty under consistent tie handling, yet a
target count may never be optimal. State the additional structure needed for
exact recovery (such as an appropriate discrete-convexity/no-gap argument),
handle ties consistently, and separately check construction of the exact-count
witness when requested. Otherwise retain the original solver or label the result
as the supported bound or approximation; changing the target count changes the task.

## Verify reasoning and implementation separately

Use the simplest trustworthy reference on small inputs, exhaustive or differential
tests where feasible, and counterexamples aimed at the changed premise. Include
only relevant degeneracies: ties, empty candidate sets, zero parameters, endpoint
conventions, numeric range and reconstruction. An oracle built on the same
unproved pruning rule can hide the same bug.

Keep the logical argument and executable evidence distinct. No found counterexample
is evidence from the searched domain, not a general proof; a sound argument does
not establish that the implementation handles boundaries correctly. Preserve the
reasoning and regression that justify the omission, with a guard or valid fallback
when the premise covers only part of the supported input domain.

## Account for what actually got cheaper

Name the removed dimension, scan or update and count the remaining work. Include
preprocessing, parameter-search range, witness recovery and memory lifetime when
material. An amortized bound needs a bound on total insertions, deletions or merges;
“each candidate is removed once” does not bound other repeated work by itself.

Compare with the competitive baseline across workload parameters that could
reverse the result, such as a small removed dimension or a large value-search
range. A better asymptotic bound may lose on the target workload. Report measured
speedup only for tested conditions; beating one implementation does not establish
a best-known algorithm or a theoretical breakthrough.
