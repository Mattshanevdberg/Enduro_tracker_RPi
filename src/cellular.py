# imports
import time
import os
import json


class Cellular:
    def __init__(self):
        # Initialize GNSS in UART mode at 9600 baud  
        #self.gnss = DFRobot_GNSS_UART(9600)
        print(f"Cellular module initialized.")

        # TEST For testing purposes
        self.test_send_success = False
        self.test_counter = 0

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
        pass

    def send_file(self, json_path):
        """
        Sends data over the cellular network.

        This function is a placeholder for sending data via a cellular module. The actual implementation
        will depend on the specific cellular hardware and library being used.

        Args:
            data (str): The data to be sent over the cellular network.

        Returns:
            bool: True if the data was sent successfully, False otherwise.
        """
        # TEST test sending the file by reading it and printing its contents
        with open(json_path, 'r') as f:
            data = f.read()
        print(f"Attempting to send data: {data}")
        # Simulate sending delay
        time.sleep(0.5)
        # Implement actual sending logic here

        # return False if failed and true if successful
        # TEST s1 always successful
        #if self.test_counter >= 0:
        # # TEST s2 fail first 1 times then succeed
        # if self.test_counter >= 1:
        #     self.test_send_success = True
        #     print(f"Cell: send pass. On send attempt {self.test_counter}")
        # TEST s3 fail first 3 times then succeed
        if self.test_counter >= 5:
            self.test_send_success = True
        
        if self.test_counter >= 30:
            self.test_send_success = False

        if self.test_counter >= 300:
            self.test_send_success = True

        if self.test_counter >= 310:
            self.test_send_success = False

        if self.test_counter >= 1500:
            self.test_send_success = True

        if self.test_counter >= 1550:
            self.test_send_success = False

        if self.test_counter >= 1600:
            self.test_send_success = True

        if not self.test_send_success:
            print(f"Cell: send fail. On send attempt {self.test_counter}")
        else:
            print(f"Cell: send success. On send attempt {self.test_counter}")

        #TEST
        self.test_counter += 1

        return self.test_send_success