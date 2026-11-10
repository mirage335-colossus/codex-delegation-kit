"""Original checks cover adapter quality and legacy input compatibility."""
import unittest
from src.inventory_app import INITIAL_STOCK, normalize_vendor_feed, receive


class OriginalChecks(unittest.TestCase):
    def test_vendor_adapter_normalizes_supported_aliases(self):
        rows = [{'part_code': 'r-14', 'units': '12', 'shipment_ref': 'ASN-1'}]
        self.assertEqual(normalize_vendor_feed(rows), [
            {'sku': 'R-14', 'quantity': 12, 'reference': 'ASN-1'}])

    def test_adapter_ignores_malformed_or_nonpositive_rows(self):
        rows = [{'part_code': 'R-14', 'units': 'bad', 'shipment_ref': 'ASN-1'},
                {'part_code': 'R-14', 'units': '0', 'shipment_ref': 'ASN-1'}]
        self.assertEqual(normalize_vendor_feed(rows), [])

    def test_legacy_receipts_still_work(self):
        result = receive([{'sku': 'R-14', 'quantity': '4'}])
        self.assertEqual(result['available']['R-14'], INITIAL_STOCK['R-14'] + 4)
        self.assertEqual(result['received_units'], 4)

if __name__ == '__main__':
    unittest.main()
