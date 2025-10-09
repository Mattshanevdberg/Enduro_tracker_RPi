#### for running in vscode (comment out when on Raspberry Pi)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
####

import unittest
from src.gps import GNSS, GNSS_lora
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import json
import time

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

class TestGNSSBoot(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def test_boot_no_device(self):
        class Dummy:
            def begin(self):
                return False
        self.gnss.gnss = Dummy()
        self.assertFalse(self.gnss.boot())

    def test_boot_success_loads_backlog(self):
        class Dummy:
            def begin(self):
                return True
            def enable_power(self):
                pass
            def set_gnss(self, *_):
                pass
            def rgb_on(self):
                pass
        self.gnss.gnss = Dummy()
        # Simulate presence of backlog file containing [1,2,3]
        with patch('os.path.isfile', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps([1, 2, 3]))):
            self.assertTrue(self.gnss.boot())
            self.assertEqual(self.gnss.transmit_backlog, [1, 2, 3])

class TestGNSSAppendDicts(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def test_append_gnss_dict_send_initializes(self):
        result = self.gnss.append_gnss_dict_send({}, {"utc": 1})
        self.assertIn("f", result)
        self.assertEqual(len(result["f"]), 1)

    def test_append_gnss_dict_send_appends(self):
        result = self.gnss.append_gnss_dict_send({"f": [{"utc": 1}]}, {"utc": 2})
        self.assertEqual([fix["utc"] for fix in result["f"]], [1, 2])

class TestGNSSWaitAndLog(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def test_wait_for_send_sleeps_expected_time(self):
        last = 100.0
        rate = 2
        with patch('src.gps.time.time', return_value=101.0), \
             patch('src.gps.time.sleep') as mock_sleep:
            self.gnss.wait_for_send(last, rate)
            mock_sleep.assert_called_once_with(1.0)

    def test_append_gnss_to_log_writes_line(self):
        payload = {"utc": 1, "lat": 0.0}
        with patch('builtins.open', mock_open()) as m:
            self.gnss.append_gnss_to_log(payload)
            handle = m()
            handle.write.assert_called_once_with(json.dumps(payload) + '\n')

class TestGNSSCompression(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def sample(self):
        return {"f": [{
            'utc': 1700000000,
            'lat': -34.123456,
            'lon': 18.654321,
            'alt': 12.3,
            'sog': 4.56,
            'cog': 123.4,
            'fx': 1,
            'hdop': 0.9,
            'nsat': 8
        }]}

    def test_compress_scaled(self):
        compact = self.gnss.compress_gnss_dict(self.sample(), scaled=True)
        self.assertIn('f', compact)
        row = compact['f'][0]
        self.assertEqual(len(row), 9)
        self.assertEqual(row[0], 1700000000)
        self.assertEqual(row[1], int(round(-34.123456 * 1e6)))
        self.assertEqual(row[2], int(round(18.654321 * 1e6)))
        self.assertEqual(row[3], int(round(12.3 * 10)))
        self.assertEqual(row[4], int(round(4.56 * 100)))
        self.assertEqual(row[5], int(round(123.4 * 10)))
        self.assertEqual(row[6], 1)
        self.assertEqual(row[7], int(round(0.9 * 10)))
        self.assertEqual(row[8], 8)

    def test_compress_unscaled(self):
        compact = self.gnss.compress_gnss_dict(self.sample(), scaled=False)
        self.assertEqual(compact['f'][0][0], 1700000000)
        self.assertAlmostEqual(compact['f'][0][1], -34.123456)
        self.assertAlmostEqual(compact['f'][0][2], 18.654321)

class TestGNSSCreateDecompress(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def test_create_gnss_json_calls_open_and_dump(self):
        data = {"f": [{"utc": 1}]}
        with patch('builtins.open', mock_open()) as m:
            path = self.gnss.create_gnss_json(data, unique_id='123', pi_id='pi-123', compact=False)
            self.assertTrue(path.endswith('logs/gnss_123.json'))
            m.assert_called_once()

    def test_create_gnss_json_compact_uses_compress(self):
        data = {"f": [{"utc": 1}]}
        with patch.object(GNSS, 'compress_gnss_dict', return_value={"f": [[1]]}) as mock_comp, \
             patch('builtins.open', mock_open()):
            _ = self.gnss.create_gnss_json(data, unique_id='xyz', pi_id='pi-xyz', compact=True)
            mock_comp.assert_called_once()

    def test_decompress_gnss_json_scaled_and_unscaled(self):
        # Prepare a compact scaled dict and write to temp file
        compact_scaled = {"f": [[170, int(1e6), int(2e6), 123, 456, 789, 1, 5, 7]]}
        with tempfile.NamedTemporaryFile('w+', delete=False) as tf:
            json.dump(compact_scaled, tf)
            tf.flush()
            path = tf.name
        try:
            out = self.gnss.decompress_gnss_json(path, scaled=True)
            self.assertEqual(out['f'][0]['utc'], 170)
            self.assertAlmostEqual(out['f'][0]['lat'], 1.0)
            self.assertAlmostEqual(out['f'][0]['lon'], 2.0)
            self.assertAlmostEqual(out['f'][0]['alt'], 12.3)
            self.assertAlmostEqual(out['f'][0]['sog'], 4.56)
            self.assertAlmostEqual(out['f'][0]['cog'], 78.9)
            self.assertEqual(out['f'][0]['fx'], 1)
            self.assertAlmostEqual(out['f'][0]['hdop'], 0.5)
            self.assertEqual(out['f'][0]['nsat'], 7)
        finally:
            try:
                os.remove(path)
            except Exception:
                pass

        # Unscaled
        compact_unscaled = {"f": [[170, 1.0, 2.0, 12.3, 4.56, 78.9, 1, 0.5, 7]]}
        with tempfile.NamedTemporaryFile('w+', delete=False) as tf:
            json.dump(compact_unscaled, tf)
            tf.flush()
            path = tf.name
        try:
            out = self.gnss.decompress_gnss_json(path, scaled=False)
            self.assertEqual(out['f'][0]['utc'], 170)
            self.assertEqual(out['f'][0]['fx'], 1)
            self.assertEqual(out['f'][0]['nsat'], 7)
            self.assertAlmostEqual(out['f'][0]['lat'], 1.0)
            self.assertAlmostEqual(out['f'][0]['lon'], 2.0)
        finally:
            try:
                os.remove(path)
            except Exception:
                pass

class TestGNSSJsonHelpers(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def test_json_file_exists_and_delete(self):
        with tempfile.TemporaryDirectory() as td:
            name = 'abc'
            p = os.path.join(td, f'{name}.json')
            with open(p, 'w') as f:
                f.write('{}')
            self.assertTrue(self.gnss.json_file_exists(name, td))
            self.assertTrue(self.gnss.delete_json_file(name, td))
            self.assertFalse(self.gnss.json_file_exists(name, td))
            self.assertFalse(self.gnss.delete_json_file(name, td))

class TestGNSSBacklogListOps(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def test_add_to_transmit_backlog(self):
        self.gnss.transmit_backlog = [1]
        self.gnss.add_to_transmit_backlog(2)
        self.assertEqual(self.gnss.transmit_backlog, [1, 2])
        # no duplicate
        self.gnss.add_to_transmit_backlog(2)
        self.assertEqual(self.gnss.transmit_backlog, [1, 2])

    def test_remove_from_transmit_backlog_calls_delete(self):
        self.gnss.transmit_backlog = [10, 20]
        with patch.object(GNSS, 'delete_json_file', return_value=True) as mock_del:
            self.gnss.remove_from_transmit_backlog(10)
            self.assertEqual(self.gnss.transmit_backlog, [20])
            logs_dir = os.path.join(os.path.dirname(__file__), '../logs/')
            mock_del.assert_called_once_with('gnss_10', logs_dir)

class TestGNSSTimeAndBacklogFile(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS()

    def test_check_enough_time_remaining_true_false(self):
        last = 100.0
        rate = 10
        with patch('src.gps.time.time', return_value=108.0):
            self.assertTrue(self.gnss.check_enough_time_remaining(last, rate))
        with patch('src.gps.time.time', return_value=110.0):
            self.assertFalse(self.gnss.check_enough_time_remaining(last, rate))

    def test_update_backlog_file_writes_json(self):
        data = [1, 2, 3]
        with patch('builtins.open', mock_open()) as m:
            self.gnss.update_backlog_file(data)
            m.assert_called_once()

class TestGNSSSendGnssJson(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS(search_rate=1)

    def test_send_no_backlog_adds_current_on_failure(self):
        cell = MagicMock()
        with patch.object(GNSS, 'json_file_exists', return_value=True), \
             patch.object(GNSS, 'update_backlog_file') as mock_upd, \
             patch.object(GNSS, 'check_enough_time_remaining', return_value=False):
            result = self.gnss.send_gnss_json(111, cell, last_gnss_time=time.time())
            self.assertFalse(result)
            self.assertIn(111, self.gnss.transmit_backlog)
            mock_upd.assert_called()

    def test_send_backlog_attempts_oldest_and_adds_current(self):
        cell = MagicMock()
        self.gnss.transmit_backlog = [222]
        with patch.object(GNSS, 'json_file_exists', return_value=True), \
             patch.object(GNSS, 'remove_from_transmit_backlog') as mock_rem, \
             patch.object(GNSS, 'update_backlog_file') as mock_upd, \
             patch.object(GNSS, 'check_enough_time_remaining', return_value=False):
            result = self.gnss.send_gnss_json(333, cell, last_gnss_time=time.time())
            self.assertFalse(result)
            # Current added; oldest not removed due to forced failure
            self.assertIn(333, self.gnss.transmit_backlog)
            mock_rem.assert_not_called()
            mock_upd.assert_called()

    def test_send_success_when_test_count_hits_threshold(self):
        cell = MagicMock()
        self.gnss.test_count = 29  # next call will simulate success
        with patch.object(GNSS, 'json_file_exists', return_value=True), \
             patch.object(GNSS, 'delete_json_file') as mock_del, \
             patch.object(GNSS, 'check_enough_time_remaining', return_value=False):
            result = self.gnss.send_gnss_json(444, cell, last_gnss_time=time.time())
            self.assertTrue(result)
            mock_del.assert_called_once()

    def test_send_backlog_success_removes_oldest_but_still_false(self):
        cell = MagicMock()
        self.gnss.transmit_backlog = [555]
        self.gnss.test_count = 29
        with patch.object(GNSS, 'json_file_exists', return_value=True), \
             patch.object(GNSS, 'remove_from_transmit_backlog') as mock_rem, \
             patch.object(GNSS, 'update_backlog_file') as mock_upd, \
             patch.object(GNSS, 'check_enough_time_remaining', return_value=False):
            result = self.gnss.send_gnss_json(666, cell, last_gnss_time=time.time())
            self.assertFalse(result)
            mock_rem.assert_called_once_with(555)
            mock_upd.assert_called()

class TestGNSSTempSendCurrentPosition(unittest.TestCase):
    def setUp(self):
        self.gnss = GNSS(search_rate=1)

    def test_send_current_position_failure_no_retry(self):
        cell = MagicMock()
        payload = {"utc": 1, "lat": 0.0}
        with patch('builtins.open', mock_open()), \
             patch.object(GNSS, 'check_enough_time_remaining', return_value=False):
            result = self.gnss.send_current_position(cell, payload, last_gnss_time=time.time())
            self.assertFalse(result)

    def test_send_current_position_compact_calls_compress(self):
        cell = MagicMock()
        payload = {"utc": 1, "lat": 0.0}
        with patch('builtins.open', mock_open()), \
             patch.object(GNSS, 'compress_gnss_dict', return_value={"f": [[1]]}) as mock_comp, \
             patch.object(GNSS, 'check_enough_time_remaining', return_value=False):
            _ = self.gnss.send_current_position(cell, payload, last_gnss_time=time.time(), compact=True)
            mock_comp.assert_called_once()

class TestNoopAndLora(unittest.TestCase):
    def test_start_stop_noop(self):
        g = GNSS()
        self.assertIsNone(g.start())
        self.assertIsNone(g.stop())

    def test_gnss_lora_init_and_method(self):
        l = GNSS_lora(search_rate=2, lora_config={"a": 1})
        self.assertEqual(l.search_rate, 2)
        self.assertEqual(l.lora_config, {"a": 1})
        self.assertIsNone(l.transmit_current_position())

if __name__ == '__main__':
    unittest.main()
