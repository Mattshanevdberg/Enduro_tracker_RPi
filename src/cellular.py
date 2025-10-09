# imports
import time
import os
import json
import socket
import requests
from typing import Optional


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

    def send_test_wifi(self, json_path: str, server_base: str, device_id: Optional[str] = None, token: Optional[str] = None) -> bool:
        """
        Send a local JSON file to the web application over Wi-Fi (HTTP POST).

        Parameters
        ----------
        json_path : str
            Absolute or relative path to the JSON file to send (e.g., logs/gnss_123.json).
        server_base : str
            Base URL of the server (e.g., "http://192.168.1.50:5000").
        device_id : str | None
            Optional Unique identifier for this device (e.g., "pi-001").
        token : str | None
            Optional short token for lightweight auth; sent as X-Device-Key header.

        Returns
        -------
        bool
            True if the server accepted >=1 fixes (HTTP 200), otherwise False.

        Notes
        -----
        - This mirrors the behavior of Cellular.send_file(path) → bool, but uses Wi-Fi/HTTP.
        - Future: you can reuse this function with a cellular PDP context simply by changing
        `server_base` to your remote URL (no code change).
        """
        try:
            # 1) Quick local file checks
            if not os.path.isfile(json_path):
                print(f"[send_test_wifi] File not found: {json_path}")
                return False

            # 2) Load file content as JSON
            with open(json_path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            # 3) Ensure device_id is present (server requires it)
            # we don't need this because it is added in the create_gnss_json function
            # payload["pid"] = device_id

            # 4) Build URL and headers
            url = server_base.rstrip("/") + "/api/v1/upload"
            # can potentially remove the header later
            # see under some_notes
            headers = {"Content-Type": "application/json"}
            if token:
                headers["X-Device-Key"] = token  # optional lightweight auth

            # 5) POST with a short timeout
            resp = requests.post(url, json=payload, headers=headers, timeout=8)

            if resp.status_code == 200:
                # Removed the json in the response because the server does not send any json back (keep payload small)
                # body = resp.json()
                # accepted = int(body.get("accepted", 0))
                # ok = accepted > 0
                print(f"[send_test_wifi] Server accepted fixes")
                return True
            else:
                print(f"[send_test_wifi] HTTP {resp.status_code}: {resp.text[:200]}")
                return False

        except (requests.RequestException, socket.timeout) as net_err:
            print(f"[send_test_wifi] Network error: {net_err}")
            return False
        except (ValueError, json.JSONDecodeError) as json_err:
            print(f"[send_test_wifi] JSON error: {json_err}")
            return False
        except Exception as e:
            print(f"[send_test_wifi] Unexpected error: {e}")
            return False

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
        self.test_send_success = self.send_test_wifi(json_path, "http://127.0.0.1:5000", "test-device")

        # return False if failed and true if successful
        # TEST s1 always successful
        #if self.test_counter >= 0:
        # # TEST s2 fail first 1 times then succeed
        # if self.test_counter >= 1:
        #     self.test_send_success = True
        #     print(f"Cell: send pass. On send attempt {self.test_counter}")
        # TEST s3 fail first 3 times then succeed

        # TEST CODE BELOW: change the pattern of success/failure as needed
        # if self.test_counter >= 5:
        #     self.test_send_success = True
        
        # if self.test_counter >= 30:
        #     self.test_send_success = False

        # if self.test_counter >= 300:
        #     self.test_send_success = True

        # if self.test_counter >= 310:
        #     self.test_send_success = False

        # if self.test_counter >= 1500:
        #     self.test_send_success = True

        # if self.test_counter >= 1550:
        #     self.test_send_success = False

        # if self.test_counter >= 1600:
        #     self.test_send_success = True

        # if not self.test_send_success:
        #     print(f"Cell: send fail. On send attempt {self.test_counter}")
        # else:
        #     print(f"Cell: send success. On send attempt {self.test_counter}")

        # #TEST
        # self.test_counter += 1

        return self.test_send_success