"""Small receiving application; reads CSV, updates inventory, emits JSON."""
import csv
import json
import sys

INITIAL_STOCK = {'R-14': 3, 'CLIP-2': 0}


def normalize_vendor_feed(rows):
    """Existing vendor adapter: convert alternate supplier fields to line items."""
    normalized = []
    for row in rows:
        sku = (row.get('part_code') or row.get('sku') or '').strip().upper()
        raw_units = row.get('units') if row.get('units') is not None else row.get('quantity')
        ref = (row.get('shipment_ref') or row.get('reference') or '').strip()
        try:
            units = int(raw_units)
        except (TypeError, ValueError):
            continue
        if sku and ref and units > 0:
            normalized.append({'sku': sku, 'quantity': units, 'reference': ref})
    return normalized


def _legacy_rows(rows):
    """Original import path, which only handles canonical supplier headers."""
    items = []
    for row in rows:
        if 'sku' not in row or 'quantity' not in row:
            continue
        try:
            units = int(row['quantity'])
        except (TypeError, ValueError):
            continue
        sku = row['sku'].strip().upper()
        if sku and units > 0:
            items.append({'sku': sku, 'quantity': units})
    return items


def receive(rows, stock=None):
    """Receive rows using the current application import route."""
    inventory = dict(INITIAL_STOCK if stock is None else stock)
    received_units = 0
    for row in rows:
        # Supplier feeds use alternate columns and require a shipment reference.
        # Keep malformed vendor rows out of the permissive legacy path.
        supplier_values = (row.get(key) for key in ('part_code', 'units', 'shipment_ref'))
        if any(value is not None and str(value).strip() for value in supplier_values):
            items = normalize_vendor_feed([row])
        else:
            items = _legacy_rows([row])
        for item in items:
            inventory[item['sku']] = inventory.get(item['sku'], 0) + item['quantity']
            received_units += item['quantity']
    return {'available': inventory, 'received_units': received_units}


def import_file(path):
    with open(path, newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    return receive(rows)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        raise SystemExit('usage: python3 -m src.inventory_app FEED.csv')
    print(json.dumps(import_file(argv[0]), sort_keys=True))


if __name__ == '__main__':
    main()
