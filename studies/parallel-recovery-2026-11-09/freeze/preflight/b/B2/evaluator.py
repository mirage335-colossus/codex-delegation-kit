"""Private deterministic acceptance checks; keep outside participant source."""
from pagination import paginate, DEFAULT_PAGE_SIZE


def main():
    rows = list(range(40))
    assert paginate(rows, limit=0) == [], "explicit zero must produce an empty page"
    assert paginate(rows) == rows[:DEFAULT_PAGE_SIZE], "omitted limit must retain the default"
    assert paginate(rows, offset=3, limit=2) == [3, 4], "positive limit/offset regressed"
    assert paginate(rows, offset=-2, limit=2) == [0, 1], "negative offset behavior regressed"
    print("PASS: explicit zero, default, positive limit, and offset boundaries")

if __name__ == "__main__":
    main()
