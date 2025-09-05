# imports
import time  
from src.DFRobot_GNSS import DFRobot_GNSS_UART, GPS_BeiDou_GLONASS
import pynmea2
from datetime import datetime, timezone
import os
import json

class GNSS:
    def __init__(self, search_rate=2 ):
        self.search_rate = search_rate
        # Initialize GNSS in UART mode at 9600 baud  
        #self.gnss = DFRobot_GNSS_UART(9600)
        print(f"GNSS initialized with search rate: {self.search_rate} seconds")

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
        # Boot up GNSS module
        if not self.gnss.begin():  
            print("No Devices! GNSS module not detected.")  
            return False
        self.gnss.enable_power()  
        self.gnss.set_gnss(GPS_BeiDou_GLONASS)  
        self.gnss.rgb_on()   # turn on the onboard RGB LED (it may already be on by default)  
        print("GNSS module initialized successfully.")  
        return True

    def start(self):
        # Start GNSS tracking
        # I am going go have to do some tests on the pi for this
        # I would ideally like to have it turn on and off to save power
        pass

    def stop(self):
        # Stop GNSS tracking
        # I am going go have to do some tests on the pi for this
        # I would ideally like to have it turn on and off to save power
        pass

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
        # 1) raw bytes (ints) -> text lines
        if test_mode:
            # Example NMEA sentences for testing
            all_gnss_data = [36, 71, 78, 71, 71, 65, 44, 49, 49, 51, 55, 49, 53, 46, 48, 48, 48, 44, 51, 52, 48, 56, 46, 51, 54, 53, 53, 51, 44, 83, 44, 48, 49, 56, 50, 51, 46, 53, 54, 54, 50, 48, 44, 69, 44, 49, 44, 49, 56, 44, 48, 46, 55, 44, 55, 56, 46, 55, 44, 77, 44, 51, 48, 46, 56, 44, 77, 44, 44, 42, 54, 52, 13, 10, 36, 71, 78, 71, 76, 76, 44, 51, 52, 48, 56, 46, 51, 54, 53, 53, 51, 44, 83, 44, 48, 49, 56, 50, 51, 46, 53, 54, 54, 50, 48, 44, 69, 44, 49, 49, 51, 55, 49, 53, 46, 48, 48, 48, 44, 65, 44, 65, 42, 53, 67, 13, 10, 36, 71, 78, 71, 83, 65, 44, 65, 44, 51, 44, 48, 49, 44, 48, 50, 44, 48, 51, 44, 48, 55, 44, 48, 56, 44, 49, 52, 44, 49, 55, 44, 49, 57, 44, 50, 50, 44, 51, 48, 44, 44, 44, 49, 46, 53, 44, 48, 46, 55, 44, 49, 46, 51, 44, 49, 42, 51, 55, 13, 10, 36, 71, 78, 71, 83, 65, 44, 65, 44, 51, 44, 48, 56, 44, 50, 57, 44, 51, 48, 44, 51, 54, 44, 52, 53, 44, 44, 44, 44, 44, 44, 44, 44, 49, 46, 53, 44, 48, 46, 55, 44, 49, 46, 51, 44, 52, 42, 51, 49, 13, 10, 36, 71, 78, 71, 83, 65, 44, 65, 44, 51, 44, 55, 56, 44, 56, 48, 44, 55, 57, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 49, 46, 53, 44, 48, 46, 55, 44, 49, 46, 51, 44, 50, 42, 51, 65, 13, 10, 36, 71, 80, 71, 83, 86, 44, 51, 44, 49, 44, 49, 50, 44, 48, 49, 44, 54, 53, 44, 49, 48, 55, 44, 50, 49, 44, 48, 50, 44, 51, 56, 44, 49, 51, 53, 44, 50, 49, 44, 48, 51, 44, 50, 48, 44, 48, 53, 53, 44, 51, 53, 44, 48, 54, 44, 48, 55, 44, 51, 51, 48, 44, 44, 48, 42, 54, 56, 13, 10, 36, 71, 80, 71, 83, 86, 44, 51, 44, 50, 44, 49, 50, 44, 48, 55, 44, 51, 50, 44, 51, 53, 52, 44, 50, 50, 44, 48, 56, 44, 49, 52, 44, 49, 49, 51, 44, 50, 56, 44, 49, 51, 44, 48, 54, 44, 50, 53, 54, 44, 44, 49, 52, 44, 54, 48, 44, 50, 49, 52, 44, 50, 55, 44, 48, 42, 54, 51, 13, 10, 36, 71, 80, 71, 83, 86, 44, 51, 44, 51, 44, 49, 50, 44, 49, 55, 44, 52, 53, 44, 50, 54, 48, 44, 50, 52, 44, 49, 57, 44, 50, 54, 44, 50, 55, 52, 44, 50, 55, 44, 50, 50, 44, 52, 48, 44, 50, 50, 52, 44, 50, 54, 44, 51, 48, 44, 53, 49, 44, 51, 49, 54, 44, 50, 54, 44, 48, 42, 54, 56, 13, 10, 36, 66, 68, 71, 83, 86, 44, 50, 44, 49, 44, 48, 54, 44, 48, 53, 44, 44, 44, 51, 49, 44, 48, 56, 44, 50, 54, 44, 49, 49, 48, 44, 50, 53, 44, 50, 57, 44, 55, 57, 44, 50, 51, 50, 44, 49, 54, 44, 51, 48, 44, 51, 55, 44, 49, 51, 53, 44, 50, 52, 44, 48, 42, 52, 65, 13, 10, 36, 66, 68, 71, 83, 86, 44, 50, 44, 50, 44, 48, 54, 44, 51, 54, 44, 53, 54, 44, 48, 50, 52, 44, 51, 52, 44, 52, 53, 44, 54, 55, 44, 50, 52, 49, 44, 50, 54, 44, 48, 42, 55, 54, 13, 10, 36, 71, 76, 71, 83, 86, 44, 50, 44, 49, 44, 48, 54, 44, 55, 56, 44, 50, 49, 44, 48, 52, 48, 44, 51, 52, 44, 56, 48, 44, 52, 53, 44, 50, 48, 55, 44, 50, 49, 44, 55, 57, 44, 55, 51, 44, 48, 54, 53, 44, 49, 57, 44, 56, 56, 44, 48, 53, 44, 49, 52, 52, 44, 44, 48, 42, 55, 57, 13, 10, 36, 71, 76, 71, 83, 86, 44, 50, 44, 50, 44, 48, 54, 44, 56, 49, 44, 54, 56, 44, 49, 54, 52, 44, 44, 54, 56, 44, 50, 50, 44, 50, 57, 48, 44, 44, 48, 42, 55, 69, 13, 10, 36, 71, 78, 82, 77, 67, 44, 49, 49, 51, 55, 49, 54, 46, 48, 48, 48, 44, 65, 44, 51, 52, 48, 56, 46, 51, 54, 53, 53, 51, 44, 83, 44, 48, 49, 56, 50, 51, 46, 53, 54, 54, 50, 49, 44, 69, 44, 48, 46, 48, 48, 44, 53, 55, 46, 52, 51, 44, 48, 50, 48, 57, 50, 53, 44, 44, 44, 65, 44, 86, 42, 50, 65, 13, 10, 36, 71, 78, 86, 84, 71, 44, 53, 55, 46, 52, 51, 44, 84, 44, 44, 77, 44, 48, 46, 48, 48, 44, 78, 44, 48, 46, 48, 48, 44, 75, 44, 65, 42, 49, 54, 13, 10, 36, 71, 78, 90, 68, 65, 44, 49, 49, 51, 55, 49, 54, 46, 48, 48, 48, 44, 48, 50, 44, 48, 57, 44, 50, 48, 50, 53, 44, 48, 48, 44, 48, 48, 42, 52, 53, 13, 10, 36, 71, 80, 84, 88, 84, 44, 48, 49, 44, 48, 49, 44, 48, 49, 44, 65, 78, 84, 69, 78, 78, 65, 32, 79, 75, 42, 51, 53, 13, 10]
        else:
            all_gnss_data = self.gnss.get_all_gnss() or [] # get the raw byte array (ints)
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
            # positions (float degrees)
            lat = getattr(rmc, 'latitude', None)
            lon = getattr(rmc, 'longitude', None)
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
    
    def check_sats(self, gnss_dict):
        """
        Checks GNSS fix quality and number of satellites.

        Args:
            gnss_dict (dict): Dictionary from get_gnss_dict().

        Returns:
            tuple: (sat_available (bool), nsat (int or None))
        """
        fx = gnss_dict.get('fx', 0)         # Get fix quality from dictionary, default to 0 if missing
        nsat = gnss_dict.get('nsat', None)  # Get number of satellites from dictionary, default to None if missing
        sat_available = fx != 0             # sat_available set to True if fix quality is not zero (same as an if statement)
        return sat_available, nsat          # Return tuple: (satellite available, number of satellites)
    
    def append_gnss_dict_send(self, gnss_dict_send, gnss_dict_current):
        """
        Append one GNSS fix (gnss_dict_current) to a batch dictionary (gnss_dict_send).

        - gnss_dict_send: dictionary holding multiple fixes (possibly empty at start)
        - gnss_dict_current: dictionary for the latest fix (one entry)

        Returns: updated gnss_dict_send with appended entry.
        """

        # If this is the first fix, initialise the container
        if not gnss_dict_send:
            gnss_dict_send = {"f": []}

        # Append the new fix
        gnss_dict_send["f"].append(gnss_dict_current)

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
        elapsed = time.time() - last_gnss_time # time since last GNSS reading
        wait_time = max(0, search_rate - elapsed) # time to wait to maintain search rate
        if wait_time > 0: # only sleep if we need to (if more than serach_rate seconds has passed, no need to wait)
            time.sleep(wait_time) # wait the required time

    def append_gnss_to_log(self, gnss_dict_current):
        """
        Append a GNSS dictionary entry to the transmit log file.

        Args:
            gnss_dict (dict): GNSS data dictionary to append.

        Returns:
            None
        """
        log_path = os.path.join(os.path.dirname(__file__), '../logs/gnss_log.txt')
        with open(log_path, 'a') as log_file:
            log_file.write(json.dumps(gnss_dict_current) + '\n')
        # Append gnss_dict to a log file for later transmission
        # Implement file handling and appending logic here

class GNSS_lora(GNSS):
    def __init__(self, search_rate=1, lora_config=None):
        super().__init__(search_rate)
        self.lora_config = lora_config

    def transmit_position(self):
        # Transmit position over LoRa
        # use compact binary packet for the lora transmission
        pass