'''
Description:    Ecoplate analysis software to calculate AWCD for ecoplate scans.
'''
import csv
import os
import sys
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, timedelta  #maybe fix this when I'm not lazy

'''
HI REMEMBER TO REMOVE ME AND REPLACE WITH A PROJECT-SPECIFIC KEY THAT SARA MAKES
'''
# gspread authorization 
scope = ['https://spreadsheets.google.com/feeds']
auth_path = ~/Documents/research/ecoplate_analysis/'gspread api-a3dd38e5d3e8.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_path, scope)
gc = gspread.authorize()
'''
END IMPORTANT THING
'''


__author__ = "Brady Vizenor"
__date__ = "10/28/2017"

'''
SECTION 1: Setup

use in format 'python3 Ecoplate_Analysis.py /path/to/dir/of/files/to/be/read
'''

def calcAWCD(currentSample):
    '''
    Description: Calculates the 
    Preconditions: currentSample is a list of lists, where each "sublist" is a row in the sample's entries
    Postconditions: Returns a float containing the AWCD for the sample
    '''
    return sum([sum(item) for item in currentSample])/31
    

'''
SECTION 2:  Importing data.
'''
#Initialize the dictionary that will hold each sample's information.
sampleDict = {}
# Navigate to directory provided by the user.
os.chdir(sys.argv[1])
# Imports each text file in the current working directory that matches the naming scheme "YYYYMMDD_somechars (P1037)" or similar, where YYYYMMDD is the date,
# and the plate ID is anything else as long as it contains a unique number of any length
# Also does not open copies of files, so it works in the old crowded directories it will probably be used in.
fileList = [x for x in os.listdir() if ".txt" in x and x[0:7].isdigit() and "copy" not in x.lower]
# Open the master file spreadsheet
master_file = gc.open("1BazLeWBEKBvHJB98Mf_lg6yj8eHuFe6UVOvUT0QYa78".sheet2)


for fileName in fileList:
    #creates a date object using the date in the filename, with format:  date(YYYY,MM,DD)
    newdate = date(fileName[0:3],fileName[4:5],fileName[6:7])
    #grabs the plate ID defined as any digit in the second half of the file name
    plateID = ''.join([n for n in fileName.split()[1] if n.isdigit()])

    
    #opens the file in read mode
    rawdata = open(file,"r"")
    dataMatrix = []
    # Splits the file into a list of lines
    rawdataList = rawdata.split("\n")
    # Searches for the line that reads "590", which indicates the beginning of the useful data, then isolates the data we want to look at using that index
    dataList = rawdataList[rawdataList[rawdataList.index("590")+1:rawdataList.index("590")+9]
    # Splits each line in that isolated data block into a list of data entries
    for i in range(len(dataList)):
        dataMatrix.append([dataList[i].split('\t')])
        # Removes the "590" that appears to be at the end of every line
        if dataMatrix[i][-1] == "590":
            del dataMatrix[i][-1]
    # At this point each item in our new data matrix is still typed as a string, change them to ints to make it easier to calculate AWCD
    for r in range(len(dataMatrix)):
        for c in range(len(dataMatrix[r])):
            dataMatrix[r][c] = int(dataMatrix[r][c])

    # Creates a regular expression 
    plate_re = re.compile(#???+plateID)
    cellrow = master_file.find(plate_re)[0]

    sampleIDList = [master_file.cell(cellrow,2),master_file.cell(cellrow,3),master_file.cell(cellrow,4)]

    # at this point we have a list of sampleIDs named sampleIDList
    sampleMatrix1 = []
    sampleMatrix2 = []
    sampleMatrix3 = []
    # creates 2D lists containing data for each sample
    for row in dataMatrix:
        sampleMatrix1.append(row[0:4])
        sampleMatrix2.append(row[5:8])
        sampleMatrix3.append(row[9:11])

    # add each sampleID to the dictionary if the sampleID is not in the dictionary already
    for sampleID in sampleIDList:
        if sampleID not in sampleDict.keys():
            sampleDict[sampleID] = []

    # append each new reading to the sample's dictionary entry with the format
    # [date(Date of Reading), [Sample Matrix], float(AWCD)]
    sampleDict[sampleIDList[0]].append([newdate, sampleMatrix1, calcAWCD(sampleMatrix1)])
    sampleDict[sampleIDList[1]].append([newdate, sampleMatrix2, calcAWCD(sampleMatrix2)])
    sampleDict[sampleIDList[2]].append([newdate, sampleMatrix3, calcAWCD(sampleMatrix3)])


'''
SECTION 3: Analyzing data.
'''

goodData = []
for sampleID in sampleDict.keys():
    #sorts entries in each sample by date
    sampleDict[sampleID].sort(key=lambda item: item[0]))
    #goes through in order of newly sorted entries
    for entry in sampleDict[sampleID]:
        if calcAWCD(entry[1]) <= 0.6 and calcAWCD(entry[1]) >= 0.4:
            # appends a list to goodData in the format ['sampleID',[sampleMatrix]]
            goodData.append([sampleID]+entry[1])
            # breaks to the next sample ID when this happens, so no subsequent scans will be added to our output
            break


    
    

'''
SECTION 4: Exporting results.
'''

goodData.sort(key=lambda item: item[0])





'''
'''


# go through the weird manual file
# sample ID


# wants sample ID C1 C2 C3 C4 -- normalized
# just use the first day that it works for, then no more
