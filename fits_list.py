""" README:
This scripts recursively reads FIT file header and print to terminal.
You can customize which keyword is printed.

Using this script: 
- Install python. Any recent version works on Linux, Windows or MacOS
- Install astropy lib: pip install astropy
- The script can be placed anywhere on your file system (e.g. /home/scripts/fits_list.py)
- Open a terminal and move to your images directory: e.g. /home/astrophoto/NGC_1313
- Launch the script with its full path: python /home/scripts/fits_list.py

"""
import os
import readline

try:
    from astropy.io import fits
except:
    print("Astropy lib needed, try: pip install astropy")
    exit(1)

# FIT keywords are listed as description:key_name pairs.
# Any keyword can be added / changes. Description is only used for readability in the output, can be empty though.
fits_keywords = {'' : 'object', 'Filter:' : 'filter', 'Exp:' : 'exptime', 'Date:' : 'date-obs', 'RA:' : 'ra','DEC:' : 'dec'}

# On Windows probably is \\
dir_separator = "/" 
# Change this on Windows
sourceDirName = "." 
# Some softwares save FIT as .fit so change this.
parse_file = ".fits" 

#Only a file counter
nfile = 0

#sourceDirName = input( "Enter full path to source fits files and press enter:")

for root, dirs, files in os.walk(sourceDirName):

    for rowCounter, fitsFile in enumerate(files):
        nfile += 1
        print(str(nfile) + ' ', end = '')

        if not fitsFile.endswith(parse_file):
            continue
        
        try:
            #print(fitsFile)
            hdul = fits.open(os.path.join(root, fitsFile))
            header = hdul[0].header
            keyword_list = []
            for fits_keyword in fits_keywords:
                try:
                    print( str(fits_keyword) + ' ' + str(header[fits_keywords[fits_keyword]]) + ', ', end = "")
                except KeyError:
                    pass
                except:
                    pass
            print('')
            
        except FileNotFoundError:
            pass
        except:
            pass

