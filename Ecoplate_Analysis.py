'''
Description:    Ecoplate analysis software to calculate AWCD for ecoplate scans.
'''
import csv
import os
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import *

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
__date__ = "10/4/2017"

'''
SECTION 1: Important information
'''


'''
SECTION 2: Defining functions
'''

def calcAWCD(currentSample):
    '''
    Description: Calculates the 
    Preconditions: currentSample is a list of lists, where each "sublist" is a row in the sample's entries
    Postconditions: Returns a float containing the AWCD for the sample
    '''
    return sum([sum(item) for item in currentSample])/31
    



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
#Initialize the dictionary that will hold each sample's information.
sampleDict = {}
# Navigate to directory provided by the user.
os.chdir(sys.argv[1])
# Imports each text file in the current working directory that matches the naming scheme "YYYYMMDD_somechars (P1037)" or similar, where YYYYMMDD is the date,
# and the plate ID is anything else as long as it contains a unique number of any length
# Also does not open copies of files, so it works in the old crowded directories it will probably be used in.
fileList = [x for x in os.listdir() if ".txt" in x and x[0:7].isdigit() and "copy" not in x.lower]


for fileName in fileList:
    #creates a date object using the date in the filename, with format:  date(YYYY,MM,DD)
    newdate = date(fileName[0:3],fileName[4:5],fileName[6:7])
    #grabs the plate ID defined as any digit in the second half of the file name
    plateNum = ''.join([n for n in fileName.split()[1] if n.isdigit()])
    
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

    # parse ecoplate master file and make a three-item list, where each item is a sample name
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
SECTION 4: Analyzing data.
'''

goodData = []
for sampleID in sampleDict.keys():
    
    #sampleID.sort(do lambda thing)
    sampleDict[sampleID].sort(key=lambda item: item[0]))
    for sample in sampleDict[sampleID]:
        if calcAWCD(sample[1]) <= 0.6 and calcAWCD(sample[1]) >= 0.4:
            #write to csv file here
            #OR add to a list and then sort the list by sample ID, write at end <<< do that
            goodData.append([sampleID]+sample)
            continue


    
    

'''
SECTION 5: Exporting results.
'''

goodData.sort(key=lambda item: item[0])





'''
'''


# go through the weird manual file
# sample ID


# wants sample ID C1 C2 C3 C4 -- normalized
# just use the first day that it works for, then no more
