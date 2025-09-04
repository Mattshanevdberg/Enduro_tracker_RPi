#### for running in vscode (comment out when on Raspberry Pi)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
####
VSCODE_TEST = True # set to False when running on Raspberry Pi

# regular imports
import numpy as np
import yaml
import json
import os

# Load configuration from JSON file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../configs/config.yaml')
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

# Import other modules (uncomment as needed)
# from DFRobot_GNSS import *
from src.gps import *
# from lora import *
# from rfid import *
# from utils import *

def main():
    print("Starting Enduro Tracker...")

    # set the globals
    GNSS_SEARCH_RATE = config['global']['GNSS_SEARCH_RATE']
    

    # initialize GNSS
    try:
        gnss = GNSS(search_rate=GNSS_SEARCH_RATE)
    except Exception as e:
        print(f"Error initializing GNSS: {e}")
        return
    
    if not VSCODE_TEST:
        # boot the GNSS
        try:
            boot_success = False
            while not boot_success:
                boot_success = gnss.boot()
                if not boot_success:
                    print("GNSS boot failed, retrying in 5 seconds...")
                    time.sleep(5)
        except Exception as e:
            print(f"Error during GNSS boot: {e}")
            return

    running = True
    while running:

        # turn on GNSS
        # here I need to test the power cycling
        # gnss.enable_power()

        # Fetch position
        gnss_dict = gnss.get_gnss_dict(test_mode=VSCODE_TEST)

        # set the timestamp
        last_gnss_time = time.time()

        # Main loop logic goes here
        print("Main loop running...")
        running = False  # Remove or modify for actual loop

if __name__ == "__main__":
    main()