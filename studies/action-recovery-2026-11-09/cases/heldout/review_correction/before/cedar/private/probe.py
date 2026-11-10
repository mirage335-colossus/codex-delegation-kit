"""Independent contract checks over real dispatcher and materializers."""
import csv
import itertools
import json
from pathlib import Path
import sys
import tempfile

participant = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(participant))
from pipeline.dispatcher import run


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def events(state):
    path = state / "events.jsonl"
    return [json.loads(line)["job"] for line in path.read_text().splitlines()] if path.exists() else []


checks = 0
with tempfile.TemporaryDirectory() as temporary:
    root = Path(temporary)
    (root / "stock.csv").write_text("sku,units\nX,4\nY,2\nX,3\n")
    (root / "prices.csv").write_text("sku,cents\nX,19\nY,23\n")
    (root / "orders.csv").write_text("order,sku,requested\nM,X,8\nN,Y,1\n")
    stock = {"id": "s", "kind": "stock", "inputs": ["stock.csv"], "deps": []}
    prices = {"id": "p", "kind": "prices", "inputs": ["prices.csv"], "deps": ["s"]}
    quotes = {"id": "q", "kind": "quotes", "inputs": ["orders.csv"], "deps": ["p"]}
    waiting = {"id": "w", "kind": "settlements", "inputs": ["absent.csv"], "deps": []}
    for number, permutation in enumerate(itertools.permutations([stock, prices, quotes, waiting])):
        plan = {"jobs": list(permutation)}
        state = root / ("state_" + str(number))
        result = run(plan, root, state)
        assert result == {"completed": [job["id"] for job in permutation if job is not waiting], "pending": ["w"], "status": "ok"}, result
        assert events(state) == ["s", "p", "q"], events(state)
        assert read_csv(state / "q.csv") == [{"order": "M", "sku": "X", "units": "7", "total_cents": "133"}, {"order": "N", "sku": "Y", "units": "1", "total_cents": "23"}]
        before = {path.name: path.read_bytes() for path in state.iterdir()}
        run(plan, root, state)
        assert before == {path.name: path.read_bytes() for path in state.iterdir()}
        assert not (root / "absent.csv").exists()
        checks += 5
    (root / "absent.csv").write_text("vendor,cents\nV,700\n")
    resumed = run(plan, root, state)
    assert resumed["pending"] == []
    assert events(state) == ["s", "p", "q", "w"]
    assert read_csv(state / "w.csv") == [{"vendor": "V", "cents": "700"}]
    checks += 3

    left = {"id": "left", "kind": "stock", "inputs": ["stock.csv"], "deps": []}
    right = {"id": "right", "kind": "stock", "inputs": ["stock.csv"], "deps": []}
    for number, ordered in enumerate(([left, right], [right, left])):
        state = root / ("ready_" + str(number))
        run({"jobs": ordered}, root, state)
        assert events(state) == [job["id"] for job in ordered]
        checks += 1

    cycle = [{**left, "deps": ["right"]}, {**right, "deps": ["left"]}]
    state = root / "cycle"
    assert run({"jobs": cycle}, root, state) == {"completed": [], "pending": ["left", "right"], "status": "ok"}
    assert events(state) == []
    checks += 2
print(json.dumps({"assertions": checks, "plans": 28}))
