"""Metered raw-reading leases, released explicitly by the consumer."""
import csv


class RowBudgetExceeded(RuntimeError):
    pass


class Meter:
    def __init__(self, limit):
        self.limit, self.live, self.peak, self.seen = limit, 0, 0, 0

    def lease(self, row):
        if self.live >= self.limit:
            raise RowBudgetExceeded("raw row limit exceeded: " + str(self.limit))
        self.live += 1
        self.seen += 1
        self.peak = max(self.peak, self.live)
        return Lease(self, row)


class Lease:
    def __init__(self, meter, row):
        self.meter, self.row = meter, row

    def __enter__(self):
        if self.row is None:
            raise RuntimeError("released reading")
        return self.row

    def __exit__(self, *args):
        self.release()

    def release(self):
        if self.row is not None:
            self.row = None
            self.meter.live -= 1


def leased_rows(path, meter):
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            yield meter.lease(row)
