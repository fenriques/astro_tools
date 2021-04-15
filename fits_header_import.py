""" README:
    This script reads parameters from Ekos Analyze log file (.analyze)
    and writes them as keywords into fits files header section.

    As of now can be imported: HFR, Eccentricity, Stars, Median (background)
    
# Operation:
    After an imaging session and before moving any fits file,
    launch the script: 
        - python fits_header_import.py 
        - Enter the .analyze file location

# Configuration:
    After a first run and only if needed edit the fits_header_import_config.ini
    - fitsFileIndex is the position (comma separated) of the fits file in the
      CaptureComplete row of the analyze log
    - fitsKeyword are the position/label of fits keyword
    
# Notes:
    - This script doesn't delete any file. It just update or overwrite fits keywords
    - Tested on Linux only.
    - .analyze default location on linux: ~/.local/share/kstars/analyze/
    - Requires: Python3, Astropy, Kstars v.3.5.0+ 
    - As soon as Ekos will write these keywords to a fits file, this
    script will be obsolete.
"""

import sys
import os
import configparser
import json

# Astropy package is needed
try:
    from astropy.io import fits
except:
    print("Astropy lib needed, try: pip install astropy")
    exit(0)

# CONFIGURATION:
# Read / create config file
fconfig = {}
try:
    with open('fits_header_import_config.ini', 'r') as config:
        config = json.load(config)
except (json.decoder.JSONDecodeError, IOError):
    # Template config for first run only. Do not edit below.
    # If needed change the json config file.
    fconfig['analyzeFile'] = "~/.local/share/kstars/analyze/"
    # Position of fits filename in the .analyze row, hopefully never changes.
    fconfig['fitsFileIndex'] = "5"
    # Which fits header to import? key: position in .analyze file, val: label for fits header
    # Check CaptureComplete row in your .analyze file if some value looks weird
    fconfig['fitsKeyword'] = {"4": "HFR",
                              "6": "NSTARS",
                              "7": "MEDIAN",
                              "8": "ECC"}

    with open('fits_header_import_config.ini', "w") as f:
        json.dump(fconfig, f)
    with open('fits_header_import_config.ini', 'r') as config:
        config = json.load(config)

# Open fits file using full path or read from script current directory
fullPath = True
# Path separator. Not tested on Windows, try \\
separator = "/"
# Row counter
counter = 0
# END CONFIGURATION

# Class for message colors


class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


# Input .analyze file
analyzeFile = input(
    "Enter full path to .analyze file  (default: " + config['analyzeFile'] + "):")
if len(analyzeFile) == 0:
    analyzeFile = config['analyzeFile']

try:
    with open(os.path.join(analyzeFile), "r") as file:
        lines = file.readlines()
    print(bc.OKBLUE+"File found"+bc.ENDC)
except EnvironmentError:
    print(bc.FAIL + "Please enter a valid path to a .analyze file"+bc.ENDC)
    exit(0)

# Update config
config['analyzeFile'] = analyzeFile
with open('fits_header_import_config.ini', 'w') as f:
    json.dump(config, f)

# Ask for confirmation
v = str(list(config['fitsKeyword'].values()))
confirm = input(bc.BOLD +
                "Press any key to write " + v + " into the fits header [q=quit] " + bc.ENDC)
# Exit script
if confirm in ['exit', 'quit', 'q']:
    exit(0)

fitsFileIndex = int(config['fitsFileIndex'])

# Parsing .analyze file
for row, val in enumerate(lines):

    # We just need the captureComplete rows
    # that store relevant information
    if "CaptureComplete" in val:
        line = val.split(",")
        if fullPath:
            fitsFile = line[fitsFileIndex]
        else:
            fitsFile = line[config['fitsFileIndex']].split(separator)[-1]

        # and there must be a fits filename in that row
        if fitsFile != "":
            try:
                counter += 1
                keyCounter = 0
                print(str(counter) + " - file: " + fitsFile)
                for key in config['fitsKeyword']:
                    try:
                        val = float(line[int(key)])
                        keyCounter += 1

                        # Writing the keywords into FITS headers
                        fits.setval(
                            fitsFile,
                            config['fitsKeyword'][key],
                            value=val)

                        print(str(config['fitsKeyword'][key]) + " = "+str(val))
                    except IndexError:
                        print(bc.WARNING+"Index "+str(key) +
                              " is not listed in .analyze file" + bc.ENDC)

                print(bc.OKGREEN+str(keyCounter) +
                      " FITS keywords updated"+bc.ENDC)

            except FileNotFoundError:
                print(bc.FAIL+"File not found"+bc.ENDC)
                pass
            print("")
