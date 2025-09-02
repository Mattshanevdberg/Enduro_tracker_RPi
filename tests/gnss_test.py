import time  
from src.DFRobot_GNSS import DFRobot_GNSS_UART, GPS_BeiDou_GLONASS  

# Initialize GNSS in UART mode at 9600 baud  
gnss = DFRobot_GNSS_UART(9600)  
if not gnss.begin():  
    print("No Devices! GNSS module not detected.")  
    exit(1)  

# Turn on GNSS power and configure constellations (use GPS+BeiDou+GLONASS)  
gnss.enable_power()  
gnss.set_gnss(GPS_BeiDou_GLONASS)  
gnss.rgb_on()   # turn on the onboard RGB LED (it may already be on by default)  
print("GNSS module initialized successfully. Reading data...")  

while True:  
    # Fetch data from GNSS  
    utc = gnss.get_utc()       # current time (UTC)  
    date = gnss.get_date()     # current date  
    lat = gnss.get_lat()       # latitude  
    lon = gnss.get_lon()       # longitude  
    sats = gnss.get_num_sta_used()  # number of satellites used  
    alt = gnss.get_alt()       # altitude  
    cog = gnss.get_cog()       # course over ground
    sog = gnss.getsog()        # speed over ground
    mode = gnss.get_gnss_mode() # GNSS mode (conselation used)

    # Print out the readings  
    print(f"Date: {date.year}-{date.month:02d}-{date.date:02d}  Time: {utc.hour:02d}:{utc.minute:02d}:{utc.second:02d} UTC")  
    print(f"Latitude: {lat.latitude_degree:.6f}° {lat.lat_direction},  Longitude: {lon.lonitude_degree:.6f}° {lon.lon_direction}")  
    print(f"Satellites Used: {sats},  Altitude: {alt} m")
    print(f"course over ground: {cog}")
    print(f"speed over ground: {sog}")
    print(f"GNSS mode (conselation used): {mode}")  
    print("----")  
    print("Get all gnss data:")
    print(gnss.get_all_gnss())
    time.sleep(1)  
