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
from src.cellular import *
# from lora import *
# from rfid import *
# from utils import *

def main():
    print("Starting Enduro Tracker...")

    # set the globals 
    #(set in config file)
    GNSS_SEARCH_RATE = config['global']['GNSS_SEARCH_RATE'] # rate that we get GNSS readings in seconds
    GNSS_SEND_BATCH_SIZE = config['global']['GNSS_SEND_BATCH_SIZE'] # number of GNSS readings to send in one batch
    SEND_COMPACT = config['global']['SEND_COMPACT'] # whether to send compact JSON
    TRANSMIT_MODE =  config['global']['TRANSMIT_MODE'] # Options: "lora", "cellular", "dual"
    # LORA_SEND_RATE = config['global']['LORA_SEND_RATE']
    # other globals...
    last_gnss_time = 0
    sat_available = False
    gnss_send_count = 0
    transmit_backlog_empty = True
    gnss_dict_send = {}
    transmit_backlog = []
    

    # initialize GNSS
    try:
        gnss = GNSS(search_rate=GNSS_SEARCH_RATE)
    except Exception as e:
        print(f"Error initializing GNSS: {e}")
        return
    
    # initialize Cellular
    if TRANSMIT_MODE in ["cellular", "dual"]:
        try:
            cell = Cellular()
        except Exception as e:
            print(f"Error initializing Cellular: {e}")
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
        gnss_dict_current = gnss.get_gnss_dict(test_mode=VSCODE_TEST)

        # set the timestamp
        last_gnss_time = time.time()

        # Check satellite availability (potentially use this to send a signal or something)
        sat_available, _ = gnss.check_sats(gnss_dict_current)

        # Append the GNSS data to a log file
        gnss.append_gnss_to_log(gnss_dict_current)
        
        # append the current gnss dict to the send gnss dict
        if gnss_send_count == 0:
            gnss_dict_send = {} # initialize empty dict if first time
        gnss_dict_send = gnss.append_gnss_dict_send(gnss_dict_send, gnss_dict_current)

        # get the current utc send id
        current_utc_id = gnss_dict_current['utc'] # get the UTC of the last fix in the current dict

        # check if there is a backlog of transmissions to send
        if transmit_backlog_empty:
            # if there is no backlog, check if we have reached the batch size to send
            if gnss_send_count >= (GNSS_SEND_BATCH_SIZE - 1): # -1 because we start counting from 0
                # reached the batch size
                # create the .json file with unique ID and send
                gnss.create_gnss_json(gnss_dict_send, unique_id=current_utc_id, compact=SEND_COMPACT)
                    # test = gnss.decompress_gnss_json("/home/matthew/Desktop/Master_Dev/Enduro_Tracker_RPi/logs/gnss_1756813036_test_compressed_scaled.json") # for testing purposes
                
                # send the data, reset the gnss counter and transmit_backlog_empty = True
                gnss_send_count, transmit_backlog_empty = gnss.send_gnss_json(transmit_backlog, current_utc_id, cell, last_gnss_time) 

                # wait until the next GNSS search interval has elapsed
                gnss.wait_for_send(last_gnss_time, GNSS_SEARCH_RATE)
                continue  # Breaks out of the current iteration of the loop and starts the next iteration (get next GNSS reading)

            else:
                # if not, increment gnss_send_count and wait until the next GNSS search interval has elapsed
                gnss_send_count += 1
                gnss.wait_for_send(last_gnss_time, GNSS_SEARCH_RATE)
                continue  # Breaks out of the current iteration of the loop and starts the next iteration (get next GNSS reading)
        else:
            pass
        





        # Main loop logic goes here
        print("Main loop running...")
        running = False  # Remove or modify for actual loop

if __name__ == "__main__":
    main()