# Iterate execution probes

## Frozen question and scope

Baseline: `7c86bf24bc3f5e397c4945e55d8875fd9a551a77`, unchanged `iterate/SKILL.md`.
Packet: [execution-cases.json](execution-cases.json), `iterate-execution-v1`.
Freeze fixture bytes and case prompts before forward runs. Finish baseline
executions before editing the live skill; then run the candidate in fresh
contexts against identical starting fixtures. Record instruction and fixture
SHA256 fingerprints. Evaluator repairs require a new protocol identity and
rerunning both affected arms.

Hypothesis: explicit next-experiment comparison, candidate promotion and scoped
search closure improve decisions without creating extra approval or paperwork.
Rival: the baseline already succeeds, or extra wording merely adds work.
The candidate must preserve correct output, authority boundaries and stop-on-target
behavior. Passing these probes supports the tested cases, not broad reliability.

The original `cases.json` remains a separate, visible prose-development suite.
This packet adds actual code execution (`pipeline-*`) and a labeled synthetic
measurement replay (`measurements`). Neither is an untouched holdout. Changing a
selection in the replay is observable behavior but is not real performance work.

## Prepare an executor workspace

From the repository root:

```sh
python3 iterate/evals/prepare_execution.py --case pipeline-search --output /tmp/iterate-probe-unique
```

Use a fresh destination for each case and arm; existing paths are rejected.
The script copies only the fixture, task prompt and instruction snapshot, never
the criteria or test solutions. It records starting hashes outside the workspace.
Give the executor the absolute `task.md` and `workspace/` paths. It may read the
applicable live skill and its necessary domain references, but no grading packet,
repository eval tests, other runs or earlier answers. The live skill must still
match that arm's recorded snapshot. These are instruction-isolated contexts, not
an OS security sandbox; report any detected cross-arm or rubric exposure.

Use the same available model, reasoning setting, tools and task-specific time
cap in both arms, with no cross-arm memory or nested delegation. The cap bounds
the evaluation task, not a new default for ordinary iterate use. Use two arm
contexts per case; when resources limit coverage, label omitted runs unrun.
Do not add a fabricated score threshold to an open optimization prompt.

## Observe and independently verify

Preserve task, skill snapshot, final response, execution notes, output files,
failed candidates and actual probe outputs. Prefer harness-captured actions;
executor-written command lists are self-reports and must be labeled as such.
Parent replay proves final artifact behavior, not an unobserved temporal sequence.
Keep exact model identity, token use and billing unknown if unavailable.

For pipeline cases, independently rerun the frozen probe on both input sets,
check final source hashes and frozen-file integrity, and inspect whether claimed
intermediate versions exist. Evaluate computational work counts separately from
wall-clock performance. For replay cases, recompute means from every confirmation
row and check scope, selection and raw-file integrity. Read final responses to
judge closure and uncertainty claims; keywords alone are insufficient.

Compare the same case/arm pairs on final artifact correctness and quality,
actual continuation/rerouting where observable, honest promotion/closure,
unauthorized effects and recovery. Record elapsed time and observed operations
where available; no quota of experiments or agents earns points. An executor
may solve both bottlenecks in one good change. A single paired run cannot establish
statistical uplift or attribute changes to a particular paragraph.

Keep a per-case result table and raw evidence links in `execution-observed.md`.
Accept the scoped instruction revision when implemented distinctions are exercised
and regressions pass; report ties and untested cases rather than inventing gains.
If a failure leads to another edit, preserve that failed candidate and label the
next run as development retesting, not untouched confirmation.

Independent artifact replay (use a new result path, not an existing file):

```sh
python3 iterate/evals/replay_execution.py /tmp/iterate-probe-unique --output /tmp/iterate-probe-unique/replay.json
python3 -B -m unittest discover -s iterate/tests -v
```

Replay uses the repository's frozen probe rather than trusting the executor's
copy, checks frozen-file integrity and instruction/fixture fingerprints, and
recomputes final metrics. Its `artifact_checks_passed` deliberately excludes
unobserved action order and narrative judgment. Grading those still requires
the response and available trace. Inspect implementation diffs for metric bypass
and contract gaps even when replay passes; these fixtures are not a security
sandbox or exhaustive correctness proof.

`prepare_execution.py` prepares cases; unit tests verify fixtures. Neither launches
a model or grades behavior. The repository's `tests/evaluate_behavior_cases.py`
does not load this packet. Use the protocol above instead of reporting its
generic green status as iterate validation.

## Post-run counterexample and portable replay

After the frozen comparison, inspection found that both resume implementations
reject an unhashable `str` subclass even though the input contract accepts strings.
The original v1 probe remains unchanged, preserving its results. The separate
`check_contract_edges.py` was then run on all four final implementations and on
the reference. It exposes two shared failures; it is post-hoc diagnostic evidence,
not an untouched holdout or a new win for either arm. A v1 artifact pass therefore
does not establish the full input contract.

```sh
python3 -B iterate/evals/check_contract_edges.py /path/to/workspace/pipeline.py
```

The portable [execution-evidence.json](execution-evidence.json) preserves all ten
run directories as relative file-to-SHA256 maps with deduplicated text blobs,
including both instruction snapshots, manifests, final artifacts, retained
alternatives, execution notes and replay results. Bytecode caches are omitted.
Verbatim final chat responses and full action logs are unavailable in this
archive; do not treat the notes as their substitute. Claimed intermediate versions
not saved by an executor remain unavailable, even if a hash was reported.

`test_execution_archive.py` checks every blob hash, reconstructs each run in a
temporary directory, repeats final artifact replay, and confirms the known
counterexamples remain recorded as failures:

```sh
python3 -B -m unittest discover -s iterate/tests -p test_execution_archive.py -v
```

This command replays artifacts, not models. Its green result means archived
outcomes are reproducible, including failures; it does not mean every executor
satisfied the whole contract. The generated candidate programs are evaluation
artifacts, not production implementations.
