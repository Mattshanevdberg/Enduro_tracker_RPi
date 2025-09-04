# imports
import time  
from src.DFRobot_GNSS import DFRobot_GNSS_UART, GPS_BeiDou_GLONASS
import pynmea2
from datetime import datetime, timezone

class GNSS:
    def __init__(self, search_rate=2 ):
        self.search_rate = search_rate
        # Initialize GNSS in UART mode at 9600 baud  
        #self.gnss = DFRobot_GNSS_UART(9600)
        print(f"GNSS initialized with search rate: {self.search_rate} seconds")

    def boot(self):
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
            'utc': utc,   # e.g. "2025-09-04T12:34:56Z"
            'lat': lat,
            'lon': lon,
            'alt': alt,   # meters MSL (from GGA)
            'sog': sog_k,  # speed over ground in knots
            'cog': cog,      # course over ground in degrees
            'fx': fx,        # GGA fix quality (0=no fix)
            'hdop': hdop,
            'nsat': nsat
        }
        return gnss_dict

class GNSS_lora(GNSS):
    def __init__(self, search_rate=1, lora_config=None):
        super().__init__(search_rate)
        self.lora_config = lora_config

    def transmit_position(self):
        # Transmit position over LoRa
        pass