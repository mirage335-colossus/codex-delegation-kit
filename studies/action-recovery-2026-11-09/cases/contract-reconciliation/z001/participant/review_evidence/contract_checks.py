from src.inventory_app import INITIAL_STOCK, normalize_vendor_feed, receive

# Preserve the original adapter contract.
assert normalize_vendor_feed([{'part_code': 'r-14', 'units': '12', 'shipment_ref': 'ASN-1'}]) == [
    {'sku': 'R-14', 'quantity': 12, 'reference': 'ASN-1'}]
assert normalize_vendor_feed([
    {'part_code': 'R-14', 'units': 'bad', 'shipment_ref': 'ASN-1'},
    {'part_code': 'R-14', 'units': '0', 'shipment_ref': 'ASN-1'},
]) == []

# Preserve canonical receipts, including omission of a reference field.
legacy = receive([{'sku': 'R-14', 'quantity': '4'}])
assert legacy == {'available': {'R-14': INITIAL_STOCK['R-14'] + 4, 'CLIP-2': 0}, 'received_units': 4}

# User-required production import behavior: aliases, valid quantities, ignored bad lines.
rows = [
    {'part_code': 'r-14', 'units': '12', 'shipment_ref': 'ASN-801'},
    {'part_code': 'R-14', 'units': '6', 'shipment_ref': 'ASN-801'},
    {'part_code': 'clip-2', 'units': '2', 'shipment_ref': 'ASN-801'},
    {'part_code': 'R-14', 'units': 'not-a-number', 'shipment_ref': 'ASN-801'},
    {'part_code': '', 'units': '9', 'shipment_ref': 'ASN-801'},
]
result = receive(rows)
assert result == {'available': {'R-14': 21, 'CLIP-2': 2}, 'received_units': 20}, result
print('contract checks passed')
