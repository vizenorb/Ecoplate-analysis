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
HI REMEMBER TO REMOVE ME AND REPLACE WITH A PROJECT-SPECIFIC KEY THAT SARA CAN MAKE
'''
# gspread authorization 
scope = ['https://spreadsheets.google.com/feeds']
auth_path = '/home/brady/Documents/research/ecoplate_analysis/gspread_api-a3dd38e5d3e8.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_path, scope)
gc = gspread.authorize(credentials)
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
    retList = []
    for row in currentSample:
        retList.append([int(i)-2 for i in row])
    return sum(retList)

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
fileList = [x for x in os.listdir() if ".txt" in x and x[0:7].isdigit() and "copy" not in x.lower()]
# Open the master file spreadsheet
master_file = gc.open("Ecoplates master file")
master_wks = master_file.get_worksheet(1)


for fileName in fileList:
    #creates a date object using the date in the filename, with format:  date(YYYY,MM,DD)
    newdate = date(int(fileName[0:4]),int(fileName[4:6]),int(fileName[6:8]))
    #grabs the plate ID defined as any digit in the second half of the file name
    plateID = ''.join([n for n in fileName.split()[1] if n.isdigit()])
    
    #opens the file in read mode
    rd = open(fileName,"r")
    lineMatrix = []
    # Splits the file into a list of lines
    rawdataList = rd.read().split("\n")

    # Searches for the line that reads "590", which indicates the beginning of the useful data, then isolates the data we want to look at using that index
    dataList = rawdataList[rawdataList.index("590")+1:rawdataList.index("590")+9]
    # Splits each line in that isolated data block into a list of data entries
    for i in range(len(dataList)):
        lineMatrix.append(dataList[i].split('\t'))
        # Removes the "590" that appears to be at the end of every line

    del(lineMatrix[-1])
    del(lineMatrix[0])
    dataMatrix = []
    for row in lineMatrix:
        dataMatrix.append([i for i in row if not i.isalpha()])
    print(dataMatrix)
    # At this point each item in our new data matrix is still typed as a string, change them to ints to make it easier to calculate AWCD
    for r in range(len(dataMatrix)):
        for c in range(len(dataMatrix[r])):
            dataMatrix[r][c] = float(dataMatrix[r][c])

    # Creates a regular expression 
    plate_re = re.compile("*"+plateID)
    # > ignore me for now:      ^[A-Za-z]+
    # Finds the numerical
    cellrow = master_wks.find(plate_re).row

    sampleIDList = [master_wks.cell(cellrow,2),master_wks.cell(cellrow,3),master_wks.cell(cellrow,4)]

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
    sampleDict[sampleID].sort(key=lambda item: item[0])
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
# Sort goodData by sampleID.
goodData.sort(key=lambda item: item[0])
# Create new CSV file
csvfilename = "./{0:4d}{1:2d}{2:2d}_viableAWCD.csv".format(datetime.now().year,datetime.now().month,datetime.now().day)
with open(csvfilename,'wb') as csvfile:
    fileWriter = csv.writer(csvfile, delimiter=',',quotechar='|',quoting=csv.QUOTE_MINIMAL)
    # Creates a header for the file
    firstLine = ["Sample ID"] + ["C"+str(i) for i in range(1,32)]
    fileWriter.writerow(firstLine)

    # Starts writing out viable data
    for sample in goodData:
        fileWriter.writerow([goodData[0]]+sum(goodData[1],[]))






'''
'''


# go through the weird manual file
# sample ID


# wants sample ID C1 C2 C3 C4 -- normalized
# just use the first day that it works for, then no more
