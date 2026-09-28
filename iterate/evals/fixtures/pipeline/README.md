# Batch normalization

Only `pipeline.py` may be changed. Use the Python standard library and preserve
`process(records, categories)`. Do not modify or bypass the probe's instrumentation.

`records` is a list of JSON strings mixed with invalid values. `categories` is a
list of distinct, nonempty strings already stripped and case-folded. Return a
list of dictionaries containing `id`, `amount`, and `category`, preserving input
order and duplicates. Do not mutate inputs or retain input-dependent state
between calls. Both inputs may change on every call.

Ignore non-string inputs, malformed JSON, non-object JSON, and objects whose
`id` is not a string. Missing `amount` defaults to zero; it must be an integer,
excluding booleans. Missing `category` defaults to an empty string; other
non-string categories invalidate the record. Strip and case-fold each category;
return its zero-based position in `categories`, or `-1` if absent. Ignore extra
object fields. An empty batch returns an empty list.

Run `python3 probe.py --dataset small` and `python3 probe.py --dataset wide`.
Use `--candidate /path/to/pipeline.py` to check another file. Each JSON report
binds the candidate SHA256 and versioned dataset ID to correctness and work
counts. A correctness failure exits with status 1.

Reduce both work counts while preserving behavior: `decode` counts actual
`JSONDecoder.decode` calls; `lookup` counts actual equality and hash operations
on supplied category strings. The probe instruments those strings with a `str`
subclass. Counts cover two calls with changed input order and category order;
they are deterministic work measurements, not elapsed or CPU time.
