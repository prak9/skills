<!-- (C) 2026 Intel Corporation, MIT license -->
# PTS execution and optimization

Use for a requested `pts/<name>` benchmark run or optimization. Interpretation of
supplied results does not require installation or a new run. Keep installation,
runtime and source edits within the existing authorization.

## Run a benchmark

1. Check `phoronix-test-suite` is available. A missing CLI is distinct from a
   missing benchmark profile: reuse an existing runtime or perform an authorized
   installation; otherwise report the concrete blocker and retain any results.
2. If the profile version is missing, refresh and resolve it via test profiles.
3. Use `batch-install` and `batch-run` for the selected benchmark.
4. Parse the summary (`Average:`), retaining score and units. Use
   `files/pts-results.json` when that result store exists and writing is in scope;
   otherwise deliver the requested result without inventing a new store.

## Optimize a benchmark

Use a matching baseline or run one, labeled `baseline`. Prepare source from the
test definition's `installed-tests/.../install.sh`, then choose the relevant perf
flow or recognized source/profile pattern. Rebuild, rerun the same benchmark with
the change label, and compare using its `hib` (higher-is-better) semantics and
correctness constraints. Do not compare changed workload/build conditions as if
they isolated the source optimization.

Paths and build contracts:

- Installed tests normally live under `/var/lib/phoronix-test-suite` (root) or
  `~/.phoronix-test-suite` (user).
- Metadata is in `installed-tests/pts/<test-name>-<version>/`; check compile flags
  in `generated.json` / `pts-install.json` when optimizing.
- Read `install.sh`; preserve its source layout and build order. Do not change
  upstream defaults unless explicitly testing those `-march`/`-O`/SIMD settings.
- A diagnostic symbol rebuild adds only `-g`, preserving optimization flags and
  defines. Re-record after rebuilding so annotation matches the actual binary.
