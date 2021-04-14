""" README:
    This script reads parameters from Ekos Analyze log file (.analyze)
    and writes them as keywords to matching fits files header section.
    As of now can be imported: HFR, Eccentricity, Stars, Median (background)

    Operation:
    After an imaging session and before moving any fits file,
    launch the script specifying the .analyze file path:
    python fits_header_import.py
    or with arg:
    python fits_header_import.py <full_path_to_analyze_session_file>.analyze

    Notes:
    - Tested on Linux only.
    - This script needs configuration (read below).
    - .analyze default location: ~/.local/share/kstars/analyze/
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
    fconfig['analyzeFile'] = "~/.local/share/kstars/analyze/"
    # /home/ferrante/Downloads/analyze/ekos-2021-04-01T21-04-31.analyze
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

# Class for messages color


class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


# Open .analyze file
# Input
analyzeFile = input(
    "Enter full path to .analyze file  (default: " + config['analyzeFile'] + "):")
if len(analyzeFile) == 0:
    analyzeFile = config['analyzeFile']

try:
    with open(os.path.join(analyzeFile), "r") as file:
        lines = file.readlines()

except EnvironmentError:
    print(bc.FAIL + "Please enter a valid path to a .analyze file"+bc.ENDC)
    exit(0)

# Update config
config['analyzeFile'] = analyzeFile
with open('fits_header_import_config.ini', 'w') as f:
    json.dump(config, f)

fitsFileIndex = int(config['fitsFileIndex'])

# Parsing .analyze file
for row, val in enumerate(lines):

    # We just need the captureComplete rows
    if "CaptureComplete" in val:
        line = val.split(",")
        if fullPath:
            fitsFile = line[fitsFileIndex]
        else:
            fitsFile = line[config
                            ['fitsFileIndex']].split(separator)[-1]

        # and there must be a fits filename in that row
        if fitsFile != "":
            try:
                counter += 1
                keyCounter = 0
                print(bc.OKBLUE+str(counter) + " - file: " + fitsFile+bc.ENDC)
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
