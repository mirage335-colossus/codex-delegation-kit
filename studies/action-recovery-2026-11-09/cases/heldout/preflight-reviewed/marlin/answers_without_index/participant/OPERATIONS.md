# Reproducible local index

The cache is intentionally excluded from source distribution. Build it from the
checked-in CSV; the builder creates its output directory and atomically replaces
an old generated database. Run from this directory:

```
python3 -B tools/build_index.py --source data/products.csv --output cache/catalog.sqlite
```

The generator records the SHA-256 of the raw CSV in `meta` and stores products
and normalized aliases in separate SQLite tables. SKU is itself an alias.
`catalog/store.py` verifies schema version and source fingerprint on every open.
Regenerate if the CSV changes; reuse is safe while both checks pass. The cache
is expendable; the raw CSV is authoritative. This is the supported local route.
