""" README:
    This script allows operation (move or delete) on fits files
    based on their stored fits keyword.
    Any condition can be set by the user on all fits keyword.
    For example:
    - delete file with Eccentricity too high
    - move files having same Gain and Offset to another dir

"""
import sys
import os
import ast
import configparser

try:
    from astropy.io import fits
except:
    print("Astropy lib needed, try: pip install astropy")
    exit(1)

# CONFIGURATION:
# Read / create config file
config = configparser.ConfigParser()
try:
    with open('test.ini') as f:
        config.read_file('config.ini')

except IOError:
    config.add_section('default')
    config['default']['sourceDirName'] = "."
    config['default']['destinationDirName'] = "."
    config['default']['fitsExpression'] = ""
    with open('config.ini', 'w') as f:
        config.write(f)
    config.read('config.ini')

# File extension (fit|fits)
extension = "fits"
# Interactive mode: ask for confirmation before deleting files:
bInteractive = True
# END CONFIGURATION

# Class for messages color


class bc:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


# Input source directory for fits files
sourceDirName = input(
    "Enter full path to source fits files and press enter (default: " + config['default']['sourceDirName'] + "):")
if len(sourceDirName) == 0:
    sourceDirName = config['default']['sourceDirName']

# Get the files from specified directory
relPath = os.path.abspath(os.path.dirname(__file__))
try:
    files = [f for f in os.listdir(os.path.join(
        relPath, sourceDirName)) if f.endswith('.'+extension)]
except EnvironmentError:
    print(bc.FAIL+"Please enter a valid path"+bc.ENDC)
    exit(1)

# Manage empty directories
if len(files) == 0:
    print(bc.WARNING + "No "+extension+" file found in this directory"+bc.ENDC)
    exit(1)
else:
    print(bc.OKBLUE + str(len(files)) +
          " fits files found in this directory\n"+bc.ENDC)

# Input destination directory
destinationDirName = input(
    "Enter full path to destination directory (default: " + config['default']['destinationDirName']+"):")
if len(destinationDirName) == 0:
    destinationDirName = config['default']['destinationDirName']

# Check if directory exists
if not os.path.exists(destinationDirName):
    print(bc.WARNING + "Directory doesn't exist. Create a destination directory and try again."+bc.ENDC)
    exit(1)

# Prints confirmation mesg
print(bc.OKBLUE + "Destination directory set to " +
      destinationDirName + "\n"+bc.ENDC)

# Fits keyowrd condition.
fitsExpression = input(
    "Enter an expression (default: " + config['default']['fitsExpression']+"):")
if len(fitsExpression) == 0:
    fitsExpression = config['default']['fitsExpression']

# Extract fits keywords from expression
try:
    varExpression = [
        node.id for node in ast.walk(ast.parse(fitsExpression))
        if isinstance(node, ast.Name)
    ]
except SyntaxError:
    print(bc.FAIL+"Expression contains errors: " +
          str(fitsExpression)+" "+bc.ENDC)
    exit(1)

# Remove duplicate keywords
varExpression = list(set(varExpression))

# Update config
config['default']['sourceDirName'] = sourceDirName
config['default']['destinationDirName'] = destinationDirName
config['default']['fitsExpression'] = fitsExpression
with open('config.ini', 'w') as f:
    config.write(f)

# Help commands
print("Commands:")
print("d = delete single file")
print("D = delete all files matching the condition")
print("m = move single file to destination directory")
print(
    "M = move all files matching the condition to destination directory")
print("enter = skip to next file")
print("q = exit the script\n")

# If dir has contents, iterate over files
for rowCounter, fitsFile in enumerate(files):
    bKeywordNotFound = False
    try:
        print(bc.OKBLUE +
              "File ("+str(rowCounter+1)+"/" +
              str(len(files))+"): " + fitsFile+bc.ENDC)

        # Read fits headers
        hdul = fits.open(os.path.join(sourceDirName, fitsFile))
        header = hdul[0].header

        # Create global variables corrisponding to fits keywords
        # (not smart but effective)
        for fk in enumerate(varExpression):
            try:
                globals()[fk[1]] = header[fk[1]]
                print(str(fk[1])+" = "+str(header[fk[1]]))
            except KeyError:
                print(bc.FAIL+"Keyword "+str(fk[1])+" not found"+bc.ENDC)
                print("Moving to next file\n")
                bKeywordNotFound = True

        # if a keyword is not in the headers we skip this file
        if bKeywordNotFound == True:
            continue
        bFileOperation = False

        # Test if condition is met
        try:
            if eval(fitsExpression):
                print("Condition \"" + fitsExpression+"\" is met")
                bFileOperation = True
            else:
                print("Condition \"" + fitsExpression+"\" is not met")
        except SyntaxError:
            print(bc.FAIL+"Expression error "+str(fitsExpression)+" "+bc.ENDC)
            exit(1)

        # If the condition is met perform user action
        if bFileOperation == True:
            # If the script is in interactive mode asks for user input
            if bInteractive == True:
                actionInput = input(
                    bc.BOLD+"Action on this file [d|D|m|M|enter=no|q]? " + bc.ENDC)

                # Set interaction off, no further confirmation asked
                if actionInput == 'D' or actionInput == 'M':
                    bInteractive = False

                # Exit script
                if actionInput in ['exit', 'quit', 'q']:
                    exit(0)

            # Delete, Move or Skip files
            if actionInput == 'd' or actionInput == 'D':
                try:
                    os.remove(os.path.join(sourceDirName, fitsFile))
                    print(bc.OKGREEN + "File " + fitsFile+" deleted!"+bc.ENDC)
                except:
                    print(bc.FAIL + "Error deleting file " + fitsFile+bc.ENDC)

            elif actionInput == 'm' or actionInput == 'M':
                try:
                    os.replace(os.path.join(sourceDirName, fitsFile),
                               os.path.join(destinationDirName, fitsFile))
                    print(bc.OKGREEN + "File moved to " +
                          destinationDirName+bc.ENDC)
                except:
                    print(bc.FAIL + "Error moving file " + fitsFile+bc.ENDC)

            else:  # Do nothing
                print(bc.OKBLUE + "File " +
                      fitsFile+" skipped"+bc.ENDC)
        else:
            print(bc.OKBLUE + "File "+fitsFile+" skipped"+bc.ENDC)

    except FileNotFoundError:
        print(bc.FAIL + fitsFile+" doesn't exist"+bc.ENDC)
        exit(0)
    print("")
