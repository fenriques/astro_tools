# astro_tools
A collection of tools for astronomy software

# 1) fits_manager.py
    This terminal based script allows operation (move or delete) on fits files
     based on meta-information stored in fits keyword.
    Any custom condition can be set by the user on all fits keyword.
    For example:
    - ECC > 0.6 will move/delete files with Eccentricity too high
    - GAIN == 200 and FILTER == 'H_Alpha' will move files having these Gain 
    and Filter values to another dir
    - TEMP > 0 and TEMP <10 will move matching files to corresponding 
    directories.

# Operation:
    - Download fits_manager.py
    - Execute from terminal: python fits_manager.py
    - Set a source directory containing fits file
    - Set a destination directory (even in case of deleting files)
    - Write a condition matching your criteria
    - Move / Delete single or multiple files

# Requirements:
    - Tested on Linux only, should work on Win/Mac too.
    - Python3, astropy

# WARNING:
    This script allows to delete files! 
    It's best at first to always move files to a 'backup' directory
    and later remove it.

![image 1](/documentation/fits_manager1.png?raw=true)

# 2) fits_header_import.py

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
