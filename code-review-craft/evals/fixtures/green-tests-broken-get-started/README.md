# catalog-export 0.2.0

Export item names as a JSON catalog. Requires Python 3 and no third-party packages.

## Get Started

From this release directory, run:

```sh
python3 catalog.py --input examples/items.json --output-file build/catalog.json
```

The command writes `build/catalog.json` containing
`{"count": 2, "names": ["Desk", "Lamp"]}`. The output directory is created if needed.

## Development checks

Run `python3 -m unittest -v test_catalog.py` from the same directory.
