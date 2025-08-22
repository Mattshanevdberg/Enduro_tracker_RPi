# Enduro Tracker
## Description of project
Low-cost endurance/motocross tracker (GNSS @ 2 s), with LoRa or cellular uplink, and RFID timing.
Develop on Debian (VS Code + Conda), deploy to Raspberry Pi (autostart via crontab).

## Quick start
- Create Conda env: `conda env create -f environment.yml && conda activate enduro`
- Install packages: `pip install -r requirements.txt`
- Run: `python src/main.py`

## Repo layout
src/ # modules: main, gps, lora, rfid, utils
tests/ # unit tests
configs/ # config.example.json -> copy to config.json and edit
logs/ # runtime logs (gitignored)

## Deploy (Pi)
- Clone repo, create env, set crontab:
