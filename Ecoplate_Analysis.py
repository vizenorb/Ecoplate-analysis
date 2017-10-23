'''
Description:    Ecoplate analysis software to calculate AWCD for ecoplate scans.
'''
import csv
import os
import sys
import Plate
from datetime import *

__author__ = "Brady Vizenor"
__date__ = "10/4/2017"
# Ask Dr. Anderson if we can change the way the outputs are named to be consistent
# variablename = open(filename,"r")
#  'date'_'plateID'.txt      ex: 20180106_P001701.txt
# I see in the master file that the current plate IDs aren't all P#####, it could just be any combination of six letters/numbers.

'''
SECTION 1: Important information
'''
# explain how the plateDict is set up
# explain how Plate class works



'''
SECTION 2: Defining functions
'''

def calcAWCD(currentPlate):
    '''
    Description: Calculates the 
    Preconditions:  
    Postconditions: 
    '''
    absorbanceList = [sample-currentPlate[0][0] for sample in currentPlate]
    return sum(absorbanceList)
    



'''
SECTION 3:  Initializing variables and importing data.
        >> This is currently being written as if I can get a standardized plate name. Otherwise, I can do a check based upon if a certain format is detected, namely:
            529
            1   2   3   4   5   6   7   ...
                etc.
            This code is already written in Plate.py, I just need to port it over and change the detection mechanism to that. Again, I would ideally like a standardized plate name
        >> Maybe edit the way I detect/store a date by using the audit information that *should* be at the end of every file. 
           I could have sworn that I saw ones that were missing it, though.
'''
#Initialize the dictionary that will hold each plate's information.
plateDict = {}
# Navigate to directory provided by the user.
os.chdir(sys.argv[1])
# Imports each text file in the current working directory that matches the naming scheme "YYYYMMDD_PXXXXXX" where XXXXXX is the plate ID.
# Also does not open "(copy)" files, so we should be able to use it in old/crowded directories.
fileList = [x for x in os.listdir() if x[0:7].isdigit and x[8:9] == "_P" and x[10:15].isdigit and len(x) == 20]
# Next, check if the plateID already exists in the dictionary. If it does not exist as a key, add the plateID to the dictionary as a key.
for filename in fileList:
    if item[9:15] not in plateDict.keys():
        plateDict[item[9:15]] = None
# Now, we add each text file to its plateID.
# Each item in the list will be a 2-item list with the format [date,PlateObject].
for filename in fileList:
    newDate = date(filename[0:3],filename[4:5],filename[6:7])
    plateDict[filename[9:15]].append([newDate,Plate(open(filename,"r"))]

'''
SECTION 4: Analyzing data.
'''


'''
SECTION 5: Exporting results.
'''
