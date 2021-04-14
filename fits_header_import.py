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
# Astropy package is needed
try:
    from astropy.io import fits
except:
    print("Astropy lib needed, try: pip install astropy")
    exit(0)

# CONFIGURATION:
# if analyzeFile is left empty an arg must be passed to the script
analyzeFile = "~/.local/share/kstars/analyze/<analyze filename>"
# Open fits file using full path or read from script current directory
fullPath = True
# Path separator. Not tested on Windows, try \\
separator = "/"
# Position of fits filename in the .analyze row, hopefully never changes.
fitsFileIndex = 5
# Which fits header to import? key: position in .analyze file, val: label for fits header
# Check CaptureComplete row in your .analyze file if some value looks weird
fitsArray = {"4": "HFR", "6": "NSTARS", "7": "MEDIAN", "8": "ECC"}
# Row counter
counter = 0

# Open .analyze file
try:
    with open(os.path.join(sys.argv[1]), "r") as file:
        lines = file.readlines()
except IndexError:
    try:
        with open(os.path.join(analyzeFile), "r") as file:
            lines = file.readlines()

    except EnvironmentError:
        print("Please enter a valid path to a .analyze file")
        exit(0)

# Parse the .analyze file
for row, val in enumerate(lines):
    # We just need the captureComplete rows
    if "CaptureComplete" in val:

        line = val.split(",")
        if fullPath:
            fitsFile = line[fitsFileIndex]
        else:
            fitsFile = line[fitsFileIndex].split(separator)[-1]

        # and there must be a fits filename in that row
        if fitsFile != "":
            counter += 1
            print(counter)
            try:
                print("Read file: " + fitsFile)
                for key in fitsArray:
                    val = float(line[int(key)])
                    # Writing the keywords in the FITS headers
                    fits.setval(
                        fitsFile,
                        fitsArray[key],
                        value=val)

                    print(str(fitsArray[key]) + ": "+str(val))
                print("FITS keywords updated")
            except FileNotFoundError:
                print(fitsFile+" doesn't exist")
                exit(0)
            print("----------------------")
