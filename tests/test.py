#### for running in vscode (comment out when on Raspberry Pi)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
####

from src.gps import *

gnss = GNSS()