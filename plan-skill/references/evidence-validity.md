# Optional Evidence Validity Snapshot

Use this only when a durable plan must answer a later question: “Does the recorded verification still apply to the files and acceptance rule it covered?” It is useful for long-running, interrupted, handed-off, regulated, or high-risk work. It is not required for ordinary Lite/Full plans, and Inline work never initializes it.

The checker is read-only. It compares recorded SHA-256 fingerprints with the current project files and returns one status:

| Status | Meaning | Next move |
|---|---|---|
| `valid_in_recorded_scope` | Every recorded file and raw result exists and matches | No rerun is indicated by this snapshot |
| `stale` | A recorded source, test, config, data file, acceptance source, or result changed | Re-run the recorded verifier for the affected scope |
| `evidence_missing` | A recorded file or raw result no longer exists | Restore the evidence or regenerate it |
| `uncheckable` | The snapshot is malformed, unsafe, or points outside the project | Repair the contract before relying on it |

## Snapshot contract

Copy `assets/evidence-snapshot.template.json` only after explicitly enabling this feature. Keep the file in project-owned plan state or a referenced evidence directory; do not add it to every plan template.

```json
{
  "schema_version": 1,
  "acceptance": {
    "id": "A-001",
    "version": "v1",
    "condition": "observable acceptance condition",
    "source": {"path": "spec/acceptance.md", "sha256": "..."}
  },
  "inputs": [
    {"path": "src/app.py", "role": "source", "sha256": "..."},
    {"path": "tests/test_app.py", "role": "test", "sha256": "..."},
    {"path": "config/app.toml", "role": "config", "sha256": "..."},
    {"path": "fixtures/case.json", "role": "data", "sha256": "..."}
  ],
  "verification": {
    "method": "python -m pytest tests/test_app.py",
    "verified_at": "2026-09-05T10:00:00+08:00",
    "raw_result": {"path": "artifacts/test.log", "sha256": "..."}
  }
}
```

- Acceptance has an ID, explicit version, observable condition, and a project file that owns the current rule. If that file changes, the old evidence becomes stale.
- `inputs` lists only files that actually participated in the claim, classified as source, test, config, or data. It should be sufficient, not indiscriminately repository-wide.
- Verification records the exact method, timestamp with time zone, and immutable raw result location.
- All paths are relative to the project root. Parent traversal, absolute paths, directories, invalid hashes, and symlinks resolving outside the root are uncheckable.

Run:

```bash
python3 <plan-skill>/scripts/check_evidence_snapshot.py \
  evidence-snapshot.json --project-root <project-root>
```

On `stale`, rerun only the acceptance conditions touched by the changed records. A change to an unrecorded README does not invalidate the snapshot; a change to the recorded test, source, config, data, or acceptance definition does. If the affected scope is unclear, treat that uncertainty as an uncovered dependency and widen the next snapshot deliberately.

## Compatibility and limits

Old plans keep their existing evidence links and `validate_plan.py` behavior. Only a plan that explicitly opts into evidence validity needs this JSON contract. Do not infer opt-in merely because a plan has hashes or evidence links.

A matching fingerprint proves only that recorded bytes did not change. It cannot prove that the original test covered the behavior, that an external dependency stayed stable, or that the acceptance rule was correct. Preserve the original result and verification method; never refresh hashes merely to make a stale snapshot pass.
