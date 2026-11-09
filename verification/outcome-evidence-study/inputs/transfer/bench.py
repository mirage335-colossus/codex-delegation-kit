"""Abbreviated validation microbenchmark."""
from time import perf_counter
from feed import validate


def main():
    records = [{"id": i, "value": "sample record"} for i in range(10000)]
    start = perf_counter()
    accepted = sum(validate(r) for r in records)
    elapsed = perf_counter() - start
    print(f"{accepted} records validated in {elapsed:.6f} s")


if __name__ == "__main__":
    main()

