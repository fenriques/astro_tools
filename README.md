# astro_tools
A collection of  tools for astronomy software

1) fits_manager.py
    This script allows operation (move or delete) on fits files based on meta-information stored 
    in fits keyword.
    Any custom condition can be set by the user on all fits keyword.
    For example:
    - ECC > 0.6 will move/delete files with Eccentricity too high
    - GAIN == 200 and FILTER == 'H_Alpha will move files having these Gain and Filter to another dir

    Operation:
    - Download fits_manager.py
    - Execute from terminal: python fits_manager.py
    - Set a source directory containing fits file
    - Set a destination directory (even in case of deleting files)
    - Write a condition matching your criteria
    - Move / Delete single or multiple files

    Requirements:
    - Tested on Linux only, should work on Win/Mac too.
    - Python3, astropy

2) fits_header_import.py

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
