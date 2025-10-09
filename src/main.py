#### for running in vscode (comment out when on Raspberry Pi)
import sys
import os

VSCODE_TEST = True  # set to False when running on Raspberry Pi

if VSCODE_TEST:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
####

# regular imports
import yaml
from pathlib import Path

# Load configuration from JSON file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../configs/config.yaml')
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

# send log outputs to a file
# Make sure log directory exists
Path("logs").mkdir(parents=True, exist_ok=True)
# Redirect all prints to logs/output.txt
sys.stdout = open("logs/output.txt", "a")  # "a" = append mode
sys.stderr = sys.stdout                    # send errors there too

# Import other modules (uncomment as needed)
# from DFRobot_GNSS import *
from src.gps import *
from src.cellular import *
# from lora import *
# from rfid import *
# from utils import *

def main():
    try:
        print("Starting Enduro Tracker...")

        # set the globals 
        #(set in config file)
        GNSS_SEARCH_RATE = config['global']['GNSS_SEARCH_RATE'] # rate that we get GNSS readings in seconds
        GNSS_SEND_BATCH_SIZE = config['global']['GNSS_SEND_BATCH_SIZE'] # number of GNSS readings to send in one batch
        SEND_COMPACT = config['global']['SEND_COMPACT'] # whether to send compact JSON
        TRANSMIT_MODE =  config['global']['TRANSMIT_MODE'] # Options: "lora", "cellular", "dual"
        PI_ID = config['global']['PI_ID'] # unique ID for the tracker
        # LORA_SEND_RATE = config['global']['LORA_SEND_RATE']
        # other globals...
        last_gnss_time = 0
        sat_available = False
        gnss_send_count = 0
        transmit_backlog_empty = True
        gnss_dict_send = {}

        # initialize GNSS
        try:
            gnss = GNSS(search_rate=GNSS_SEARCH_RATE, test_mode=VSCODE_TEST)
        except Exception as e:
            print(f"Error initializing GNSS: {e}")
            return
        #
        # initialize Cellular
        cell = None
        if TRANSMIT_MODE in ["cellular", "dual"]:
            try:
                cell = Cellular()
            except Exception as e:
                print(f"Error initializing Cellular: {e}")
                return
        
        # boot the GNSS (loops on hardware, single attempt in VSCode test mode)
        try:
            boot_success = False
            while not boot_success:
                boot_success = gnss.boot()
                if boot_success or VSCODE_TEST:
                    break
                print("GNSS boot failed, retrying in 5 seconds...")
                time.sleep(5)
        except Exception as e:
            print(f"Error during GNSS boot: {e}")
            return

        running = True
        while running:
            try:

                # turn on GNSS
                # here I need to test the power cycling
                # gnss.start()

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

                # TEST
                print(f"gnss_count: {gnss_send_count}")

                # check if there is a backlog of transmissions to send
                if transmit_backlog_empty:
                    # if there is no backlog, check if we have reached the batch size to send
                    # TEST
                    print(f" enter backlog empty")

                    if gnss_send_count >= (GNSS_SEND_BATCH_SIZE - 1): # -1 because we start counting from 0
                        # reached the batch size

                        # TEST
                        print(f"reached batch size")
                        #  
                        # create the .json file with unique ID and send
                        gnss.create_gnss_json(gnss_dict_send, unique_id=current_utc_id, pi_id=PI_ID, compact=SEND_COMPACT)
                            # test = gnss.decompress_gnss_json("/home/matthew/Desktop/Master_Dev/Enduro_Tracker_RPi/logs/gnss_1756813036_test_compressed_scaled.json") # for testing purposes
                        
                        # send the data and transmit_backlog_empty = True
                        transmit_backlog_empty = gnss.send_gnss_json(current_utc_id, cell, last_gnss_time) 

                        # TEST
                        print(f"transmit_backlog_empty in main: {transmit_backlog_empty}")

                        # reset the gnss counter
                        gnss_send_count = 0

                        # wait until the next GNSS search interval has elapsed
                        # switch the gnss off while we wait to save power
                        # gnss.stop()
                        gnss.wait_for_send(last_gnss_time, GNSS_SEARCH_RATE)
                        continue  # Breaks out of the current iteration of the loop and starts the next iteration (get next GNSS reading)

                    else:
                        # if not, increment gnss_send_count and wait until the next GNSS search interval has elapsed
                        gnss_send_count += 1
                        # switch the gnss off while we wait to save power
                        # gnss.stop()
                        gnss.wait_for_send(last_gnss_time, GNSS_SEARCH_RATE)
                        continue  # Breaks out of the current iteration of the loop and starts the next iteration (get next GNSS reading)
                else:
                    # the transmit backlog is not empty, so we need to try send that inbeteween the GNSS readings

                    # TEST
                    print(f"enter backlog NOT empty")

                    # first check if we have reached the batch size to send
                    if gnss_send_count >= (GNSS_SEND_BATCH_SIZE - 1): # -1 because we start counting from 0
                        # reached the batch size
                        # TEST
                        print(f"reached batch size with backlog not empty")
                        #
                        # create the .json file with unique ID and send
                        gnss.create_gnss_json(gnss_dict_send, unique_id=current_utc_id, pi_id=PI_ID, compact=SEND_COMPACT)
                            # test = gnss.decompress_gnss_json("/home/matthew/Desktop/Master_Dev/Enduro_Tracker_RPi/logs/gnss_1756813036_test_compressed_scaled.json") # for testing purposes
                        
                        # send the data and transmit_backlog_empty = True
                        transmit_backlog_empty = gnss.send_gnss_json(current_utc_id, cell, last_gnss_time)

                        # TEST
                        print(f"transmit_backlog_empty in main: {transmit_backlog_empty}")

                        # reset the gnss counter
                        gnss_send_count = 0

                        # wait until the next GNSS search interval has elapsed
                        # switch the gnss off while we wait to save power
                        # gnss.stop()
                        gnss.wait_for_send(last_gnss_time, GNSS_SEARCH_RATE)
                        continue  # Breaks out of the current iteration of the loop and starts the next iteration (get next GNSS reading)
                    else:
                        # because we will try send the current position and the backlog between the GNSS readings
                        #TEST 
                        print(f"try send current position with backlog not empty")

                        transmit_backlog_empty = gnss.send_current_position(cell, gnss_dict_current, last_gnss_time, compact=SEND_COMPACT)

                        # TEST
                        print(f"transmit_backlog_empty in main: {transmit_backlog_empty}")
                        
                        # increment gnss_send_count and wait until the next GNSS search interval has elapsed
                        gnss_send_count += 1
                        # switch the gnss off while we wait to save power
                        # gnss.stop()
                        gnss.wait_for_send(last_gnss_time, GNSS_SEARCH_RATE)
                        continue  # Breaks out of the current iteration of the loop and starts the next iteration (get next GNSS reading)
            except Exception as e:
                print(f"main loop iteration: {e}")
                os.system("sudo reboot") # reboot the system if there is an error in the main loop
                break

    except Exception as e:
        print(f"main: {e}")
        os.system("sudo reboot") # reboot the system if there is an error in the main function

if __name__ == "__main__":
    main()
