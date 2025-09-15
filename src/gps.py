# imports
import time  
from src.DFRobot_GNSS import DFRobot_GNSS_UART, GPS_BeiDou_GLONASS
import pynmea2
from datetime import datetime, timezone
import os
import json
from src.cellular import Cellular
# TEST imports 
import random # for TEST mode

class GNSS:
    def __init__(self, search_rate=2 ):
        try:
            self.search_rate = search_rate
            # Initialize GNSS in UART mode at 9600 baud  
            # TEST comment line below when not on pi
            self.gnss = DFRobot_GNSS_UART(9600)
            print(f"GNSS initialized with search rate: {self.search_rate} seconds")
            self.transmit_backlog = []#[]  # Initialize transmit backlog
            self.tmp_transmit_backlog_empty = False # Temporary variable to track if backlog is empty after sending
            # TEST
            self.test_count = 0
        except Exception as e:
            print(f"Error in __init__: {e}")

    def boot(self):
        """
        Initializes and boots up the GNSS (Global Navigation Satellite System) module.

        This function attempts to start communication with the GNSS module, enables its power,
        sets the GNSS mode to use GPS, BeiDou, and GLONASS systems, and turns on the onboard RGB LED.
        If the GNSS module is not detected, it prints an error message and returns False.
        On successful initialization, it prints a confirmation message and returns True.

        Returns:
            bool: True if the GNSS module was initialized successfully, False otherwise.
        """
        try:
            #TEST
            # Boot up GNSS module
            if not self.gnss.begin():  
                print("No Devices! GNSS module not detected.")  
                return False
            self.gnss.enable_power()  
            self.gnss.set_gnss(GPS_BeiDou_GLONASS)  
            self.gnss.rgb_on()   # turn on the onboard RGB LED (it may already be on by default)  

            # Check for backlog.txt in the logs directory and populate transmit_backlog if it exists
            backlog_path = os.path.join(os.path.dirname(__file__), '../logs/backlog.txt')
            if os.path.isfile(backlog_path):
                with open(backlog_path, 'r') as f:
                    try:
                        self.transmit_backlog = json.load(f)
                    except Exception:
                        self.transmit_backlog = []

            print("GNSS module initialized successfully.")  
            return True
        except Exception as e:
            print(f"Error in boot: {e}")
            return False

    def start(self):
        try:
            # Start GNSS tracking
            # I am going go have to do some tests on the pi for this
            # I would ideally like to have it turn on and off to save power
            print("enabling power")
            self.gnss.enable_power()
        except Exception as e:
            print(f"Error in start: {e}")

    def stop(self):
        try:
            # Stop GNSS tracking
            # I am going go have to do some tests on the pi for this
            # I would ideally like to have it turn on and off to save power
            print("disabling power")
            self.gnss.disable_power()
        except Exception as e:
            print(f"Error in stop: {e}")

    def get_gnss_dict(self, test_mode=False):
        """
        Retrieves and parses GNSS (Global Navigation Satellite System) data, returning a compact dictionary
        with key navigation and status fields.

        The function processes raw GNSS data (either from the device or test data), extracts the latest
        RMC (Recommended Minimum Specific GNSS Data) and GGA (Global Positioning System Fix Data) NMEA sentences,
        and parses them to obtain relevant information such as position, time, speed, course, fix quality,
        number of satellites, altitude, and horizontal dilution of precision.

        Args:
            test_mode (bool): If True, uses example NMEA sentences for testing instead of live GNSS data.

        Returns:
            dict: A dictionary containing the following keys:
                - 'utc': UTC timestamp as epoch seconds (int), or None if unavailable.
                - 'lat': Latitude in decimal degrees (rounded to 6 decimals), or None.
                - 'lon': Longitude in decimal degrees (rounded to 6 decimals), or None.
                - 'alt': Altitude in meters above mean sea level (rounded to 1 decimal), or None.
                - 'sog': Speed over ground in knots (rounded to 2 decimals), or None.
                - 'cog': Course over ground in degrees (rounded to 1 decimal), or None.
                - 'fx': GNSS fix quality (int, 0=no fix), or None.
                - 'hdop': Horizontal dilution of precision (rounded to 1 decimal), or None.
                - 'nsat': Number of satellites used in fix (int), or None.

        Notes:
            - Only the latest valid RMC and GGA sentences are used for extraction.
            - If parsing fails or data is missing, corresponding fields will be None.
        """

        # Get raw GNSS data
        try: 
            # 1) raw bytes (ints) -> text lines
            # TEST
            if test_mode:
                # Example NMEA sentences for testing
                all_gnss_data = [36, 71, 78, 71, 71, 65, 44, 49, 49, 51, 55, 49, 53, 46, 48, 48, 48, 44, 51, 52, 48, 56, 46, 51, 54, 53, 53, 51, 44, 83, 44, 48, 49, 56, 50, 51, 46, 53, 54, 54, 50, 48, 44, 69, 44, 49, 44, 49, 56, 44, 48, 46, 55, 44, 55, 56, 46, 55, 44, 77, 44, 51, 48, 46, 56, 44, 77, 44, 44, 42, 54, 52, 13, 10, 36, 71, 78, 71, 76, 76, 44, 51, 52, 48, 56, 46, 51, 54, 53, 53, 51, 44, 83, 44, 48, 49, 56, 50, 51, 46, 53, 54, 54, 50, 48, 44, 69, 44, 49, 49, 51, 55, 49, 53, 46, 48, 48, 48, 44, 65, 44, 65, 42, 53, 67, 13, 10, 36, 71, 78, 71, 83, 65, 44, 65, 44, 51, 44, 48, 49, 44, 48, 50, 44, 48, 51, 44, 48, 55, 44, 48, 56, 44, 49, 52, 44, 49, 55, 44, 49, 57, 44, 50, 50, 44, 51, 48, 44, 44, 44, 49, 46, 53, 44, 48, 46, 55, 44, 49, 46, 51, 44, 49, 42, 51, 55, 13, 10, 36, 71, 78, 71, 83, 65, 44, 65, 44, 51, 44, 48, 56, 44, 50, 57, 44, 51, 48, 44, 51, 54, 44, 52, 53, 44, 44, 44, 44, 44, 44, 44, 44, 49, 46, 53, 44, 48, 46, 55, 44, 49, 46, 51, 44, 52, 42, 51, 49, 13, 10, 36, 71, 78, 71, 83, 65, 44, 65, 44, 51, 44, 55, 56, 44, 56, 48, 44, 55, 57, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 49, 46, 53, 44, 48, 46, 55, 44, 49, 46, 51, 44, 50, 42, 51, 65, 13, 10, 36, 71, 80, 71, 83, 86, 44, 51, 44, 49, 44, 49, 50, 44, 48, 49, 44, 54, 53, 44, 49, 48, 55, 44, 50, 49, 44, 48, 50, 44, 51, 56, 44, 49, 51, 53, 44, 50, 49, 44, 48, 51, 44, 50, 48, 44, 48, 53, 53, 44, 51, 53, 44, 48, 54, 44, 48, 55, 44, 51, 51, 48, 44, 44, 48, 42, 54, 56, 13, 10, 36, 71, 80, 71, 83, 86, 44, 51, 44, 50, 44, 49, 50, 44, 48, 55, 44, 51, 50, 44, 51, 53, 52, 44, 50, 50, 44, 48, 56, 44, 49, 52, 44, 49, 49, 51, 44, 50, 56, 44, 49, 51, 44, 48, 54, 44, 50, 53, 54, 44, 44, 49, 52, 44, 54, 48, 44, 50, 49, 52, 44, 50, 55, 44, 48, 42, 54, 51, 13, 10, 36, 71, 80, 71, 83, 86, 44, 51, 44, 51, 44, 49, 50, 44, 49, 55, 44, 52, 53, 44, 50, 54, 48, 44, 50, 52, 44, 49, 57, 44, 50, 54, 44, 50, 55, 52, 44, 50, 55, 44, 50, 50, 44, 52, 48, 44, 50, 50, 52, 44, 50, 54, 44, 51, 48, 44, 53, 49, 44, 51, 49, 54, 44, 50, 54, 44, 48, 42, 54, 56, 13, 10, 36, 66, 68, 71, 83, 86, 44, 50, 44, 49, 44, 48, 54, 44, 48, 53, 44, 44, 44, 51, 49, 44, 48, 56, 44, 50, 54, 44, 49, 49, 48, 44, 50, 53, 44, 50, 57, 44, 55, 57, 44, 50, 51, 50, 44, 49, 54, 44, 51, 48, 44, 51, 55, 44, 49, 51, 53, 44, 50, 52, 44, 48, 42, 52, 65, 13, 10, 36, 66, 68, 71, 83, 86, 44, 50, 44, 50, 44, 48, 54, 44, 51, 54, 44, 53, 54, 44, 48, 50, 52, 44, 51, 52, 44, 52, 53, 44, 54, 55, 44, 50, 52, 49, 44, 50, 54, 44, 48, 42, 55, 54, 13, 10, 36, 71, 76, 71, 83, 86, 44, 50, 44, 49, 44, 48, 54, 44, 55, 56, 44, 50, 49, 44, 48, 52, 48, 44, 51, 52, 44, 56, 48, 44, 52, 53, 44, 50, 48, 55, 44, 50, 49, 44, 55, 57, 44, 55, 51, 44, 48, 54, 53, 44, 49, 57, 44, 56, 56, 44, 48, 53, 44, 49, 52, 52, 44, 44, 48, 42, 55, 57, 13, 10, 36, 71, 76, 71, 83, 86, 44, 50, 44, 50, 44, 48, 54, 44, 56, 49, 44, 54, 56, 44, 49, 54, 52, 44, 44, 54, 56, 44, 50, 50, 44, 50, 57, 48, 44, 44, 48, 42, 55, 69, 13, 10, 36, 71, 78, 82, 77, 67, 44, 49, 49, 51, 55, 49, 54, 46, 48, 48, 48, 44, 65, 44, 51, 52, 48, 56, 46, 51, 54, 53, 53, 51, 44, 83, 44, 48, 49, 56, 50, 51, 46, 53, 54, 54, 50, 49, 44, 69, 44, 48, 46, 48, 48, 44, 53, 55, 46, 52, 51, 44, 48, 50, 48, 57, 50, 53, 44, 44, 44, 65, 44, 86, 42, 50, 65, 13, 10, 36, 71, 78, 86, 84, 71, 44, 53, 55, 46, 52, 51, 44, 84, 44, 44, 77, 44, 48, 46, 48, 48, 44, 78, 44, 48, 46, 48, 48, 44, 75, 44, 65, 42, 49, 54, 13, 10, 36, 71, 78, 90, 68, 65, 44, 49, 49, 51, 55, 49, 54, 46, 48, 48, 48, 44, 48, 50, 44, 48, 57, 44, 50, 48, 50, 53, 44, 48, 48, 44, 48, 48, 42, 52, 53, 13, 10, 36, 71, 80, 84, 88, 84, 44, 48, 49, 44, 48, 49, 44, 48, 49, 44, 65, 78, 84, 69, 78, 78, 65, 32, 79, 75, 42, 51, 53, 13, 10]
            else:
                try:
                    all_gnss_data = self.gnss.get_all_gnss() or [] # get the raw byte array (ints)
                except Exception as e:
                    print(f"Error in get_gnss_dict: {e}")
                    all_gnss_data = []
            all_gnss_data_text = ''.join(chr(b) for b in all_gnss_data) # convert to text
            all_gnss_data_text = all_gnss_data_text.replace('\x00','') # drop zeros just in case

            rmc = None
            gga = None

            # 2) parse (Take a raw string (or bytes) and breaking it into structured 
            # fields according to a grammar or format - NMEA in this case) and 
            # keep the latest RMC & GGA
            for line in all_gnss_data_text.splitlines(): # step through lines
                # check that only NMEA sentences (start with '$')
                if not line.startswith('$'):
                    continue
                try:
                    # parse with checksum validation to get a pynmea2 object with attributes
                    msg = pynmea2.parse(line, check=True)
                except Exception:
                    continue
                st = getattr(msg, 'sentence_type', '')
                if st == 'RMC':
                    rmc = msg # keep latest RMC 
                elif st == 'GGA':
                    gga = msg # keep latest GGA

            # 3) extract from RMC (lat/lon/time, speed, course)
            utc = lat = lon = sog_k = cog = None
            if rmc:
                # time/date (UTC) as an epoch seconds (int) - seconds since 1970-01-01
                datestamp = getattr(rmc, 'datestamp', None)
                timestamp = getattr(rmc, 'timestamp', None)
                if datestamp and timestamp:
                    dt = datetime.combine(datestamp, timestamp).replace(tzinfo=timezone.utc) # dt = datetime.combine(rmc.datestamp, rmc.timestamp).replace(tzinfo=timezone.utc)
                    utc = int(dt.timestamp())   # epoch seconds (int)
                    if test_mode: #TEST
                        utc = int(time.time())  # override with current time in test mode
                # positions (float degrees)
                lat = getattr(rmc, 'latitude', None)
                lon = getattr(rmc, 'longitude', None)
                if test_mode: #TEST
                    lat = lat + (random.randint(0, 100) / 1_000_000) # add small random offset for testing
                # speed/course (may be blank)
                try:
                    sog_k = float(getattr(rmc, 'spd_over_grnd', 0) or 0.0)# float(rmc.spd_over_grnd) if rmc.spd_over_grnd else None
                except Exception:
                    sog_k = None
                try:
                    cog = float(getattr(rmc, 'true_course', 0) or 0.0)# float(rmc.true_course) if rmc.true_course else None
                except Exception:
                    cog = None

            # 4) extract from GGA (fix, hdop, sats, alt)
            fx = hdop = nsat = alt = None
            if gga:
                try:
                    fx = int(getattr(gga, 'gps_qual', 0) or 0)          # 0=no fix, 1=GPS, 2=DGPS, 4/5=RTK...
                except Exception:
                    fx = 0
                try:
                    nsat = int(getattr(gga, 'num_sats', 0) or 0)
                except Exception:
                    nsat = 0
                try:
                    alt = float(getattr(gga, 'altitude', 0) or 0.0)
                except Exception:
                    alt = None
                try:
                    hdop = float(getattr(gga, 'horizontal_dil', 0) or 0.0)
                except Exception:
                    hdop = None

            # 5) tiny rounding to keep JSON small but useful
            def r(x, n): return None if x is None else round(x, n)
            lat  = r(lat, 6) 
            lon  = r(lon, 6) 
            alt  = r(alt, 1)
            sog_k = r(sog_k, 2)    # knots (convert later if needed)
            cog  = r(cog, 1)
            hdop = r(hdop, 1)

            # 6) assemble compact dict
            gnss_dict = {
                'utc': utc,   # UTC timestamp as epoch seconds (int)
                'lat': lat,  # decimal degrees (6 decimals is ~10cm)
                'lon': lon,  # decimal degrees (6 decimals is ~10cm)
                'alt': alt,   # meters MSL (from GGA)
                'sog': sog_k,  # speed over ground in knots
                'cog': cog,      # course over ground in degrees
                'fx': fx,        # GGA fix quality (0=no fix)
                'hdop': hdop,   # horizontal dilution of precision (smaller is better, should be < 2.0)
                'nsat': nsat    # number of satellites used in fix (needs to be >= 4 for 3D fix)
            }
            return gnss_dict
        except Exception as e:
            print(f"get_gnss_dict: {e}")
            return {}
    
    def check_sats(self, gnss_dict):
        """
        Checks GNSS fix quality and number of satellites.

        Args:
            gnss_dict (dict): Dictionary from get_gnss_dict().

        Returns:
            tuple: (sat_available (bool), nsat (int or None))
        """
        try:
            fx = gnss_dict.get('fx', 0)         # Get fix quality from dictionary, default to 0 if missing
            nsat = gnss_dict.get('nsat', None)  # Get number of satellites from dictionary, default to None if missing
            sat_available = fx != 0             # sat_available set to True if fix quality is not zero (same as an if statement)
            return sat_available, nsat          # Return tuple: (satellite available, number of satellites)
        except Exception as e:
            print(f"Error in check_sats: {e}")
            return False, None
    
    def append_gnss_dict_send(self, gnss_dict_send, gnss_dict_current):
        """
        Append one GNSS fix (gnss_dict_current) to a batch dictionary (gnss_dict_send).

        - gnss_dict_send: dictionary holding multiple fixes (possibly empty at start)
        - gnss_dict_current: dictionary for the latest fix (one entry)

        Returns: updated gnss_dict_send with appended entry.
        """
        try:
            # If this is the first fix, initialise the container
            if not gnss_dict_send:
                gnss_dict_send = {"f": []}

            # Append the new fix
            gnss_dict_send["f"].append(gnss_dict_current)

            return gnss_dict_send
        except Exception as e:
            print(f"Error in append_gnss_dict_send: {e}")
            return gnss_dict_send
    
    def wait_for_send(self, last_gnss_time, search_rate):
        """
        Waits until the next GNSS search interval has elapsed.

        Args:
            last_gnss_time (float): Timestamp of the last GNSS reading.
            search_rate (int): GNSS search rate in seconds.

        Returns:
            None
        """
        try:
            elapsed = time.time() - last_gnss_time # time since last GNSS reading
            wait_time = max(0, search_rate - elapsed) # time to wait to maintain search rate
            if wait_time > 0: # only sleep if we need to (if more than serach_rate seconds has passed, no need to wait)
                time.sleep(wait_time) # wait the required time
        except Exception as e:
            print(f"Error in wait_for_send: {e}")

    def append_gnss_to_log(self, gnss_dict_current):
        """
        Append a GNSS dictionary entry to the transmit log file.

        Args:
            gnss_dict (dict): GNSS data dictionary to append.

        Returns:
            None
        """
        try:
            log_path = os.path.join(os.path.dirname(__file__), '../logs/gnss_log.txt')
            with open(log_path, 'a') as log_file:
                log_file.write(json.dumps(gnss_dict_current) + '\n')
            # Append gnss_dict to a log file for later transmission
            # Implement file handling and appending logic here
        except Exception as e:
            print(f"Error in append_gnss_to_log: {e}")

    def compress_gnss_dict(self, gnss_dict, scaled=True):
        """
        Convert GNSS dict with list of fixes into compact JSON.
        
        - gnss_dict: {'f':[ { 'utc':..., 'lat':..., ... }, {...} ]}
        - scaled=True: store floats as scaled ints (lat/lon ×1e6, alt×10, sog×100, cog×10, hdop×10)
        - scaled=False: keep original floats
        
        Returns: compact JSON string
        """
        try:
            compact_fixes = []
            for fix in gnss_dict.get("f", []):
                if scaled:
                    # scale to integers for compactness
                    utc   = int(fix.get("utc", 0))  # epoch seconds
                    lat   = int(round(fix.get("lat", 0) * 1e6))
                    lon   = int(round(fix.get("lon", 0) * 1e6))
                    alt   = int(round(fix.get("alt", 0) * 10))     # 0.1 m
                    sog   = int(round(fix.get("sog", 0) * 100))    # 0.01 knots
                    cog   = int(round(fix.get("cog", 0) * 10))     # 0.1 deg
                    fx    = int(fix.get("fx", 0))
                    hdop  = int(round(fix.get("hdop", 0) * 10))    # 0.1
                    nsat  = int(fix.get("nsat", 0))
                    compact_fixes.append([utc, lat, lon, alt, sog, cog, fx, hdop, nsat])
                else:
                    # keep original floats
                    compact_fixes.append([
                        fix.get("utc"),
                        fix.get("lat"),
                        fix.get("lon"),
                        fix.get("alt"),
                        fix.get("sog"),
                        fix.get("cog"),
                        fix.get("fx"),
                        fix.get("hdop"),
                        fix.get("nsat")
                    ])

            # Wrap in top-level dict with a single short key
            compact_dict = {"f": compact_fixes}

            # Return compact dictionary
            return compact_dict
        except Exception as e:
            print(f"Error in compress_gnss_dict: {e}")
            return {"f": []}

    def create_gnss_json(self, gnss_dict_send, unique_id, compact=False):
        """
        Create a GNSS JSON file with a unique ID.

        Args:
            gnss_dict_send (dict): Dictionary containing GNSS data to send.
            unique_id (str): Unique identifier for the JSON file.

        Returns:
            str: Path to the created JSON file.
        """
        try:
            # Convert to compact format if requested
            if compact:
                gnss_dict_send = self.compress_gnss_dict(gnss_dict_send, scaled=False)
            # Save to a JSON file
            json_path = os.path.join(os.path.dirname(__file__), f'../logs/gnss_{unique_id}.json')
            with open(json_path, 'w') as json_file:
                json.dump(gnss_dict_send, json_file, separators=(',', ':')) # compact JSON
            return json_path
        except Exception as e:
            print(f"Error in create_gnss_json: {e}")
            return ""
    
    def decompress_gnss_json(self, json_path, scaled=True):
        #THIS IS FOR TESTING PURPOSES and USE ON SERVER SIDE
        """
        Decompress a compact GNSS JSON string back into a list of fix dicts.

        - json_str: string from compress_gnss_dict()
        - scaled=True: assumes scaled ints (lat×1e5, etc.) and converts back to floats
        - scaled=False: values are already floats, returned as-is

        Returns: dict {"f": [ {full_fix}, ... ]}
        """
        try:
            # in the actual function, we would pass the json string directly
            # here we read from a file for testing purposes
            with open(json_path, 'r') as f:
                json_str = f.read()
            
            compact = json.loads(json_str)
            fixes = []

            for entry in compact.get("f", []):
                if scaled:
                    # entry is a list of 9 scaled integers
                    utc, lat, lon, alt, sog, cog, fx, hdop, nsat = entry
                    fix = {
                        "utc": int(utc),                      # epoch seconds
                        "lat": lat / 1e6,                     # degrees
                        "lon": lon / 1e6,                     # degrees
                        "alt": alt / 10.0,                    # meters
                        "sog": sog / 100.0,                   # knots
                        "cog": cog / 10.0,                    # degrees
                        "fx": int(fx),                        # fix quality
                        "hdop": hdop / 10.0,                  # dilution
                        "nsat": int(nsat)                     # satellites
                    }
                else:
                    # entry already has floats/ints in array order
                    utc, lat, lon, alt, sog, cog, fx, hdop, nsat = entry
                    fix = {
                        "utc": int(utc),
                        "lat": lat,
                        "lon": lon,
                        "alt": alt,
                        "sog": sog,
                        "cog": cog,
                        "fx": int(fx),
                        "hdop": hdop,
                        "nsat": int(nsat)
                    }
                fixes.append(fix)

            return {"f": fixes}
        except Exception as e:
            print(f"Error in decompress_gnss_json: {e}")
            return {"f": []}
    
    def json_file_exists(self, name, directory):
        """
        Check if a .json file with the given name exists in the specified directory.

        Args:
            name (str): The base name of the file (without .json extension).
            directory (str): Path to the directory to search.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        try:
            json_path = os.path.join(directory, f"{name}.json")
            return os.path.isfile(json_path)
        except Exception as e:
            print(f"Error in json_file_exists: {e}")
            return False
    
    def delete_json_file(self, name, directory):
        """
        Delete a .json file with the given name from the specified directory.

        Args:
            name (str): The base name of the file (without .json extension).
            directory (str): Path to the directory.

        Returns:
            bool: True if the file was deleted, False if it did not exist.
        """
        try:
            json_path = os.path.join(directory, f"{name}.json")
            if os.path.isfile(json_path):
                os.remove(json_path)
                return True
            return False
        except Exception as e:
            print(f"Error in delete_json_file: {e}")
            return False
    
    def add_to_transmit_backlog(self, current_utc_id):
        """
        Check if current_utc_id is in transmit_backlog; if not, add it to the end.
        
        Args:
            transmit_backlog (list): List of UTC IDs (strings).
            current_utc_id (int): The UTC ID to check/add.
        
        Returns:
            list: Updated transmit_backlog list.
        """
        try:
            # check if current_utc_id is already in the backlog
            if current_utc_id not in self.transmit_backlog:
                # check if the corresponding JSON file exists in the logs directory
                if self.json_file_exists(f"gnss_{current_utc_id}", os.path.join(os.path.dirname(__file__), '../logs/')):
                    self.transmit_backlog.append(current_utc_id)
        except Exception as e:
            print(f"Error in add_to_transmit_backlog: {e}")


    def remove_from_transmit_backlog(self, sent_utc_id):
        """
        Remove sent_utc_id from the transmit_backlog list and delete the corresponding JSON file from the logs directory.

        Args:
            transmit_backlog (list): List of UTC IDs (strings or ints).
            sent_utc_id (int or str): The UTC ID to remove and delete.

        Returns:
            list: Updated transmit_backlog list.
        """
        try:
            # Remove the sent_utc_id from the backlog if present
            if sent_utc_id in self.transmit_backlog:
                self.transmit_backlog.remove(sent_utc_id)
                # Delete the corresponding JSON file from the logs directory
                logs_dir = os.path.join(os.path.dirname(__file__), '../logs/')
                self.delete_json_file(f"gnss_{sent_utc_id}", logs_dir)
        except Exception as e:
            print(f"Error in remove_from_transmit_backlog: {e}")

    def check_enough_time_remaining(self, last_gnss_time, search_rate):
        """
        Check if there is enough time remaining in the current search interval.

        Args:
            start_time (float): Timestamp when the current GNSS search interval started.
            search_rate (int): GNSS search rate in seconds.

        Returns:
            bool: True if enough time remains, False otherwise.
        """
        try:
            elapsed = time.time() - last_gnss_time # time since start of current search interval

            #TEST
            print(f"enough time remaining: {elapsed < 0.95*search_rate}")

            return elapsed < 0.95*search_rate # True if we are still within the search rate interval
        except Exception as e:
            print(f"Error in check_enough_time_remaining: {e}")
            return False
    
    def update_backlog_file(self, transmit_backlog):
        """
        Persist the current transmit_backlog to logs/backlog.txt (overwrite existing).

        Args:
            transmit_backlog (list): List of UTC IDs representing GNSS JSON files that failed to transmit.

        Returns:
            None
        """
        try:
            # Persist the current transmit_backlog to logs/backlog.txt (overwrite existing)
            try:
                backlog_path = os.path.join(os.path.dirname(__file__), '../logs/backlog.txt')
                # Ensure logs directory exists
                os.makedirs(os.path.dirname(backlog_path), exist_ok=True)
                with open(backlog_path, 'w') as f:
                    json.dump(transmit_backlog, f)
            except Exception as e:
                print(f"Failed to write backlog.txt: {e}")
        except Exception as e:
            print(f"Error in update_backlog_file: {e}")

    def send_gnss_json(self, current_utc_id, cell, last_gnss_time):
        """
        Transmit GNSS JSON files, handling the current file and any backlog.

        Behavior
        - When no backlog exists, attempt to send the current file `gnss_{current_utc_id}.json`. On
          success, delete the file. On failure, ensure `current_utc_id` is appended to
          `transmit_backlog`.
        - When a backlog exists, attempt to send the oldest entry first. On success, delete the file
          and remove its ID from `transmit_backlog`.
        - If time remains in the current GNSS search interval (based on `last_gnss_time` and
          `self.search_rate`), the method may attempt additional sends (including recursively) until
          time runs out or the backlog is empty.

        Parameters
        ----------
        current_utc_id : int | str
            UTC ID for the most recent GNSS JSON file.
        cell : object
            Transport with a `send_file(path) -> bool` method used to transmit files.
        last_gnss_time : float
            Timestamp (seconds since epoch) of the last GNSS reading; used to respect the search interval.

        Returns
        -------
        bool
            True if the backlog is empty after processing; False otherwise.

        Side Effects
        ------------
        - Deletes successfully transmitted JSON files from `../logs/`.
        - Mutates `transmit_backlog` by adding failed current IDs and removing successfully sent oldest IDs.
        - May perform additional send attempts while time remains in the interval.
        """
        # Send the GNSS JSON file
        try: # very basic error handling
            # TEST
            print(f"entered into send_gnss_json with backlog: {self.transmit_backlog}")

            # check if the transmit_backlog is empty
            if not self.transmit_backlog: # backlog is empty
                # check if there is a current position json file to send in the logs directory
                # if there is send it and if not set transmit log to empty and return

                if self.json_file_exists(f"gnss_{current_utc_id}", os.path.join(os.path.dirname(__file__), '../logs/')):
                    # print(f"Sending current position gnss_{current_utc_id}.json")
                    # send the current position json file and return True if successful 
                    success_transmission = cell.send_file(os.path.join(os.path.dirname(__file__), '../logs', f"gnss_{current_utc_id}.json"))              

                    # if successful, delete the file and return transmit_backlog_empty = True
                    if success_transmission:
                        self.delete_json_file(f"gnss_{current_utc_id}", os.path.join(os.path.dirname(__file__), '../logs/'))
                        print(f"Deleted gnss_{current_utc_id}.json after successful transmission.")
                        # transmit_backlog_empty = True
                        # return True
                    else:
                        # check if current_utc_id is in the transmit_backlog and add if not
                        self.add_to_transmit_backlog(current_utc_id)
                        # TEST s2:
                        print(f"Failed to send gnss_{current_utc_id}.json, added to backlog.")
                        print(f"transmit_log: {self.transmit_backlog}")
                        #
                        # check if there is enough time remaining in the current search interval to
                        # send another json file from the transmit_backlog
                        if self.check_enough_time_remaining(last_gnss_time, self.search_rate):
                            #TEST s2:
                            print("enough time to try again.")
                            #
                            self.send_gnss_json(current_utc_id, cell, last_gnss_time)

                        # transmit_backlog is not empty
                        # self.update_backlog_file(self.transmit_backlog)
                        # return False
                    
                else:
                    print("Log empty and no current json, Nothing to send.")
                    # reset and transmit_backlog_empty = True
                    # return True
                
            else: # backlog is not empty
                print("Backlog in transmit log... trying to send oldest entry.")
                # check if current_utc_id is in the transmit_backlog and add if not
                self.add_to_transmit_backlog(current_utc_id)
                # get the oldest entry in the transmit_backlog
                oldest_utc_id = self.transmit_backlog[0]
                # check if the json file exists in the logs directory
                if self.json_file_exists(f"gnss_{oldest_utc_id}", os.path.join(os.path.dirname(__file__), '../logs/')):
                    # print(f"Sending backlog gnss_{oldest_utc_id}.json")
                    # send the oldest entry in the transmit_backlog and return True if successful
                    success_transmission = cell.send_file(os.path.join(os.path.dirname(__file__), '../logs', f"gnss_{oldest_utc_id}.json"))
                    
                    # if successful, remove the entry from the transmit_backlog and delete the file
                    if success_transmission:
                        self.remove_from_transmit_backlog(oldest_utc_id)
                else:
                    # if the file does not exist, remove the entry from the transmit_backlog
                    print(f"File gnss_{oldest_utc_id}.json not found, removing from backlog.")
                    self.remove_from_transmit_backlog(oldest_utc_id)
                
                # check if there is enough time remaining in the current search interval to
                # send another json file from the transmit_backlog
                if self.check_enough_time_remaining(last_gnss_time, self.search_rate):
                    self.send_gnss_json(current_utc_id, cell, last_gnss_time)

            if self.transmit_backlog:
                # transmit_backlog is not empty
                self.update_backlog_file(self.transmit_backlog)
                return False
            else:
                # transmit_backlog is empty
                self.update_backlog_file(self.transmit_backlog)
                # TEST s2:
                print(F"Transmit backlog {self.transmit_backlog}")
                #
                return True
            
        except Exception as e:
                print(f"Error in send_gnss_json: {e}")
                return False
        
    def send_current_position(self, cell, gnss_dict_current, last_gnss_time, compact = False):
        """
        Send the current position as a temporary JSON file.

        - Create a temporary JSON in `../logs/` from `gnss_dict_current`.
        - Attempt to send it via `cell.send_file()`.
        - On success: delete the temp file and try to send any backlog using `send_gnss_json`.
        - On failure: briefly retry if time permits; otherwise delete the temp file.

        Returns:
            bool: False if the backlog is not empty or failed to send current (which means it reamains not empty), otherwise True.
        """
        try:
            #TEST
            print("Entered send_current_position")
            #

            tmp_transmit_backlog_empty = False # assume backlog is has contents unless we find otherwise (otherwise we would not be in send current position)

            # Paths and temp filename (avoid clashing with batch files like gnss_{id}.json)
            logs_dir = os.path.join(os.path.dirname(__file__), '../logs')
            os.makedirs(logs_dir, exist_ok=True)
            temp_name = f"tmp_gnss.json"
            temp_path = os.path.join(logs_dir, temp_name)

            # Convert to same format as the send dict and convert to compact format if required
            gnss_dict_current = {"f": [gnss_dict_current]}
            if compact:
                gnss_dict_current = self.compress_gnss_dict(gnss_dict_current, scaled=False)

            # create a temp .json file in the log from the current gnss dict
            try:
                with open(temp_path, 'w') as f:
                    json.dump(gnss_dict_current, f, separators=(',', ':')) # compact json
            except Exception as e:
                print(f"Failed to write temp current position file: {e}")
                return False

            # attempt to send it using cell.send_file()
            def _try_send(path):
                try:
                    return cell.send_file(path)
                except Exception as e:
                    print(f"Error sending temp current position file: {e}")
                    return False

            # create a loop to try send file while there is enough time remaining
            enough_time = self.check_enough_time_remaining(last_gnss_time, self.search_rate)
            while enough_time == True:

                # try to send current location temp file
                success = _try_send(temp_path)

                if success:
                    # if success then delete the file and attempt to send any backlog (use send_gnss_json)
                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        print(f"Failed to delete temp file after send: {e}")

                    try:
                        # Attempt to send any backlog; use current time as the reference
                        tmp_transmit_backlog_empty = self.send_gnss_json(self.transmit_backlog[0], cell, last_gnss_time)
                    except Exception as e:
                        # Don't fail the current send result if backlog processing errors
                        print(f"Backlog send attempt failed: {e}")

                    return tmp_transmit_backlog_empty
                
                enough_time = self.check_enough_time_remaining(last_gnss_time, self.search_rate)

                # # if unsuccessful then check if enough time to try again 
                # if self.check_enough_time_remaining(last_gnss_time, self.search_rate):
                #     tmp_transmit_backlog_empty = self.send_current_position(cell, gnss_dict_current, last_gnss_time, compact=compact)
                #     return tmp_transmit_backlog_empty
            
            return tmp_transmit_backlog_empty
        except Exception as e:
            print(f"Error in send_current_position: {e}")
            return False



class GNSS_lora(GNSS):
    def __init__(self, search_rate=1, lora_config=None):
        try:
            super().__init__(search_rate)
            self.lora_config = lora_config
        except Exception as e:
            print(f"Error in GNSS_lora.__init__: {e}")

    def transmit_current_position(self):
        try:
            # Transmit position over LoRa
            # use compact binary packet for the lora transmission
            pass
        except Exception as e:
            print(f"Error in transmit_current_position: {e}")
