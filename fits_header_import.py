""" README:
    This script reads parameters from Ekos Analyze log file (.analyze)
    and writes them as keywords into fits files header section.

    As of now can be imported: HFR, Eccentricity, Stars, Median (background)

# Operation:
    After an imaging session launch the script:
        - python fits_header_import.py
        - Enter the .analyze file location
        - Enter the directory where the fits files are located.

# Configuration:
    If the format of your .analyze log differs, try to fix fits_header_import_config.ini
    - fitsFileIndex is the position (comma separated) of the fits file in the
      CaptureComplete row of the analyze log
    - fitsKeyword are the position/label of fits keyword
    In any case open a ticket on github.

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
import json
import glob
import readline

# Astropy package is needed
try:
    from astropy.io import fits
except:
    print("Astropy lib needed, try: pip install astropy")
    exit(0)


readline.set_completer_delims(' \t\n=')
readline.parse_and_bind("tab: complete")

# CONFIGURATION:
# Read / create config file
fconfig = {}
try:
    with open('fits_header_import_config.ini', 'r') as config:
        config = json.load(config)
except (json.decoder.JSONDecodeError, IOError):
    # Template config for first run only. Do not edit below.
    # If needed change the json config file.
    fconfig['analyzeDir'] = "~/.local/share/kstars/analyze/"
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

# Path separator. Not tested on Windows, try \\
separator = "/"

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


def listFits(config, lines, separator, overrideFitsDir, mode):
    fitsFileIndex = int(config['fitsFileIndex'])

    # Row counter
    counter = 0
    # Parsing .analyze file
    for row, val in enumerate(lines):

        # We just need the captureComplete rows
        # that store relevant information
        if "CaptureComplete" in val:
            line = val.split(",")
            fitsFile = line[fitsFileIndex]

            # and there must be a fits filename in that row
            if fitsFile != "":
                if overrideFitsDir != "":
                    fitsFile = os.path.join(
                        overrideFitsDir, fitsFile.split(separator)[-1])
                try:
                    counter += 1
                    keyCounter = 0
                    print(str(counter) + " - file: " + fitsFile)
                    for key in config['fitsKeyword']:
                        try:
                            val = float(line[int(key)])
                            keyCounter += 1

                            if mode == 'write':
                                # Writing the keywords into FITS headers
                                fits.setval(
                                    fitsFile,
                                    config['fitsKeyword'][key],
                                    value=val)

                            print(str(config['fitsKeyword']
                                      [key]) + " = "+str(val))
                        except IndexError:
                            print(bc.WARNING+"Index "+str(key) +
                                  " is not listed in .analyze file" + bc.ENDC)

                    if mode == 'write':
                        print(bc.OKGREEN+str(keyCounter) +
                              " FITS keywords updated"+bc.ENDC)

                except FileNotFoundError:
                    print(bc.FAIL+"File not found"+bc.ENDC)
                    pass
                print("")
    return counter


# MAIN
# Input .analyze directory
analyzeDir = input(
    "Enter full path to .analyze log files directory (default: " + config['analyzeDir'] + "):")
if len(analyzeDir) == 0:
    analyzeDir = config['analyzeDir']

# Read .analyze files from directory
analyzeFiles = glob.glob(analyzeDir+"/*.analyze")
analyzeFiles.sort(key=os.path.getmtime, reverse=True)

# Exit if there are no .analyze file
if len(analyzeFiles) == 0:
    print(bc.FAIL + "There are no .analyze files in this directory"+bc.ENDC)
    exit(0)
else:
    print(bc.OKGREEN+str(len(analyzeFiles)) +
          " analyze log files found\n"+bc.ENDC)

# Fits file could have been move to another location, the log will not find
# these files unless we set the new location.
overrideFitsDir = input(
    "If you moved fits files from their original location, enter the new path.\n" +
    "Else leaving blank will read the original location from .analyze log file:")

# Update config
config['analyzeDir'] = analyzeDir
with open('fits_header_import_config.ini', 'w') as f:
    json.dump(config, f)


# iterate over all analyze file in the directory
for analyzeFile in enumerate(analyzeFiles):
    actionInput = input(bc.OKGREEN + str(analyzeFile[0]+1)+"/" + str(len(analyzeFiles)) +
                        " Parsing file "+str(analyzeFile[1].split(separator)[-1]) +
                        " [enter=list fits files|s=skip|q=quit]"+bc.ENDC)

    # Skip to next file
    if actionInput == 's':
        continue

    # Exit script
    elif actionInput in ['exit', 'quit', 'q']:
        exit(0)

    # Open and read the analyze file
    try:
        with open(os.path.join(analyzeFile[1]), "r") as file:
            lines = file.readlines()
    except EnvironmentError:
        print(bc.FAIL + "Please enter a valid path to a .analyze file"+bc.ENDC)
        exit(0)

    # List the fits files
    counter = listFits(config, lines, separator, overrideFitsDir, mode='show')

    if counter > 0:
        # Ask for action
        v = str(list(config['fitsKeyword'].values()))
        confirm = input(bc.BOLD +
                        "Press any key to write " + v +
                        " into the fits header [enter=write|s=skip]q=quit] " + bc.ENDC)
        # Exit script
        if confirm in ['exit', 'quit', 'q']:
            exit(0)

        # if not Skiping move to next file
        if confirm == 's':
            continue
    else:
        print("No fits file found")
    listFits(config, lines, separator, overrideFitsDir, mode='write')
