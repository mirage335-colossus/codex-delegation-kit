# Feed importer

The importer consumes one JSON object per line. It validates each object and
stores it in a local SQLite database. `feed.import_lines` is the normal entry
point. `bench.py` is the abbreviated development benchmark. It uses only the
Python standard library and creates its input in memory.

Run `python3 -m unittest` and `python3 bench.py` from this directory.

