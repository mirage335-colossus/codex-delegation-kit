from src.inventory_app import _legacy_rows, normalize_vendor_feed, INITIAL_STOCK
rows = [{'part_code':'r-14','units':'12','shipment_ref':'A'}, {'part_code':'R-14','units':'6','shipment_ref':'A'}, {'part_code':'clip-2','units':'2','shipment_ref':'A'}, {'part_code':'R-14','units':'bad','shipment_ref':'A'}, {'part_code':'','units':'9','shipment_ref':'A'}, {'sku':'CLIP-2','quantity':'4'}]
replace = normalize_vendor_feed(rows)
routed = [*_legacy_rows([r for r in rows if 'sku' in r and 'quantity' in r]), *normalize_vendor_feed([r for r in rows if not ('sku' in r and 'quantity' in r)])]
def outcome(items):
    stock=dict(INITIAL_STOCK); total=0
    for item in items:
        stock[item['sku']]=stock.get(item['sku'],0)+item['quantity']; total+=item['quantity']
    return stock,total
print('replace_with_normalizer=', outcome(replace))
print('schema_routed=', outcome(routed))
