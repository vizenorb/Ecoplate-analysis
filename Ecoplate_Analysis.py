'''
Description:    Ecoplate analysis software to calculate AWCD for ecoplate scans.
                Created by Brady Vizenor for use by Dr. Sara Anderson, Minnesota State University Moorhead.
'''
import csv
import os
import sys
import Plate
from datetime import *

__author__ = "Brady Vizenor"
__date__ = "10/4/2017"
# variablename = open(filename,"r")
#  'date'_'plateID'.txt      ex: 20180106_P001701.txt

'''
SECTION 1: Important information
'''
# explain how the plateDict is set up
# explain how Plate class works



'''
SECTION 2: Defining functions
'''
def calcAWCD():
    



'''
SECTION 3:  Initializing variables and importing data.
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
