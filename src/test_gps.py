#### for running in vscode (comment out when on Raspberry Pi)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
####

import unittest
from src.gps import GNSS

class TestGNSSCheckSats(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def test_fix_quality_zero(self):
        gnss_dict = {'fx': 0, 'nsat': 5}
        sat_available, nsat = self.gnss.check_sats(gnss_dict)
        self.assertFalse(sat_available)
        self.assertEqual(nsat, 5)

    def test_fix_quality_nonzero(self):
        gnss_dict = {'fx': 1, 'nsat': 7}
        sat_available, nsat = self.gnss.check_sats(gnss_dict)
        self.assertTrue(sat_available)
        self.assertEqual(nsat, 7)

    def test_missing_fx_key(self):
        gnss_dict = {'nsat': 4}
        sat_available, nsat = self.gnss.check_sats(gnss_dict)
        self.assertFalse(sat_available)
        self.assertEqual(nsat, 4)

    def test_missing_nsat_key(self):
        gnss_dict = {'fx': 2}
        sat_available, nsat = self.gnss.check_sats(gnss_dict)
        self.assertTrue(sat_available)
        self.assertIsNone(nsat)

    def test_missing_both_keys(self):
        gnss_dict = {}
        sat_available, nsat = self.gnss.check_sats(gnss_dict)
        self.assertFalse(sat_available)
        self.assertIsNone(nsat)

class TestGNSSGetGnssDict(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def test_get_gnss_dict_test_mode(self):
        # Should return a dict with expected keys and types when test_mode=True
        result = self.gnss.get_gnss_dict(test_mode=True)
        expected_keys = {'utc', 'lat', 'lon', 'alt', 'sog', 'cog', 'fx', 'hdop', 'nsat'}
        self.assertTrue(expected_keys.issubset(result.keys()))
        # Check types (allow None)
        self.assertTrue(isinstance(result['utc'], (int, type(None))))
        self.assertTrue(isinstance(result['lat'], (float, type(None))))
        self.assertTrue(isinstance(result['lon'], (float, type(None))))
        self.assertTrue(isinstance(result['alt'], (float, type(None))))
        self.assertTrue(isinstance(result['sog'], (float, type(None))))
        self.assertTrue(isinstance(result['cog'], (float, type(None))))
        self.assertTrue(isinstance(result['fx'], (int, type(None))))
        self.assertTrue(isinstance(result['hdop'], (float, type(None))))
        self.assertTrue(isinstance(result['nsat'], (int, type(None))))

    def test_get_gnss_dict_test_mode_values(self):
        # Check that values are as expected for the provided test data
        result = self.gnss.get_gnss_dict(test_mode=True)
        # These values are based on the last valid RMC and GGA sentences in the test data
        # The actual values may change if the test data changes
        self.assertIsNotNone(result['utc'])
        self.assertAlmostEqual(result['lat'], -34.139426, places=6)
        self.assertAlmostEqual(result['lon'], 18.39277, places=6)
        self.assertIsInstance(result['alt'], float)
        self.assertIsInstance(result['fx'], int)
        self.assertIsInstance(result['nsat'], int)

    def test_get_gnss_dict_no_data(self):
        # Patch gnss.get_all_gnss to return empty list
        class DummyGNSS:
            def get_all_gnss(self):
                return []
        self.gnss.gnss = DummyGNSS()
        result = self.gnss.get_gnss_dict(test_mode=False)
        # All values should be None or 0
        self.assertIsNone(result['utc'])
        self.assertIsNone(result['lat'])
        self.assertIsNone(result['lon'])
        self.assertIsNone(result['alt'])
        self.assertIsNone(result['sog'])
        self.assertIsNone(result['cog'])
        self.assertIsNone(result['fx'])
        self.assertIsNone(result['hdop'])
        self.assertIsNone(result['nsat'])

if __name__ == '__main__':
    unittest.main()