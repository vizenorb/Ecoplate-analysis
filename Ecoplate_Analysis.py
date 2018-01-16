import csv
import os
import sys
import re
import datetime
import gspread
from time import sleep
from oauth2client.service_account import ServiceAccountCredentials

# gspread authorization 
# needs to be replaced with user-specific key, maybe create a master key
scope = ['https://spreadsheets.google.com/feeds']
auth_path = '/home/brady/Documents/research/ecoplate_analysis/gspread_api-a3dd38e5d3e8.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_path, scope)
gc = gspread.authorize(credentials)


__author__ = "Brady Vizenor"
__date__ = "01/08/2017"


'''
Some useful functions.
'''

def calcAWCD(currentSample):
    '''
    Description: Calculates the AWCD of a sample.
    Preconditions: currentSample is a list of lists, where each "sublist" is a row in the sample's entries
    Postconditions: Returns a float containing the AWCD for the sample
    '''
    returnList = []
    control = currentSample[0][0]
    for row in currentSample:
        returnList.extend([ent-control for ent in row])
    return sum(returnList)/31

def getFileList(dirPath, recursionCheck = False):
    '''
    Description: Gets a list of pathnames for files in a directory.
    Preconditions: dirPath is a valid pathname to a directory, recursionCheck is a boolean value indicating if you want \
    the program to check directories inside of the initial directory.
    Postconditions: Returns a list of file pathnames.
    '''
    fileList = [dirPath+fi for fi in os.listdir(dirPath) if fi[0:8].isdigit and fi.lower().endswith(".txt")]
    if recursionCheck:
        subdirList = [dirPath+subdir for subdir in os.listdir(dirPath) if os.path.isdir(dirPath+subdir)]
        for subdir in subdirList:
            fileList.extend(getFileList(subdir, True))
    return fileList





'''
Getting file list.
'''
# Initialize the dictionary that will hold each sample's information.
sampleDict = dict()
# Import the list of filenames
if "-r" in sys.argv[2:]:
    fileList = getFileList(sys.argv[1], True)
else:
    fileList = getFileList(sys.argv[1])




'''
Getting samplesIDs for each plate from master spreadsheet on Google Drive.
'''
# Open the master file spreadsheet
master_file = gc.open("Ecoplates master file")
master_wks = master_file.worksheet("Sheet2")
# Gets a list of columns for the master sheet, where the first sublist is plate ids, and each subsequent sublist is a sampleID..
# So each index for a list will equal one row in the worksheet.
# I think it's faster to get columns instead of downloading the entire spreadsheet, or iterating over the entire spreadsheet to make a list of rows.
masterList = [master_wks.col_values(1), master_wks.col_values(2), master_wks.col_values(3), master_wks.col_values(4)]
plateDict = dict()

for col in masterList:
    del[col[0]]; del[col[0]]
# This will throw an indexError if the end of the file is uneven, stops incomplete data from being analysed.
for linenum in range(max(len(masterList[0]),len(masterList[1]),len(masterList[2]),len(masterList[3]))):
    # Checks to make sure an entry exists in the column containing plate IDs, so it doesn't add empty entries
    # If that cell has a value, the check will return True. If it's an empty string, None, or False, the check will return False.
    # So each entry will be plateDict[plateID] = [sampleID1, sampleID2, sampleID3]
    if masterList[0][linenum]:
        plateDict[masterList[0][linenum]] = [masterList[1][linenum], masterList[2][linenum], masterList[3][linenum]]




for fileName in fileList:
    '''
    Getting ecoplate data from files.
    '''
    #plateID is indicated by the text after the space in the filename
    #So split by space, which should give you just the plate ID, then remove the .txt extension.
    plateID =  fileName.split()[1].replace(".txt","")
    #create a reader for the file.
    rd = open(fileName,"r")

    # Initialize the data matrix and get a list of lines.
    dataMatrix = []
    rawdataList = rd.read().split("\n")
    # Searches for the line that reads "590", which indicates the beginning of the useful data, then isolates the data we want to look at using that index.
    dataList = rawdataList[rawdataList.index("590")+2:rawdataList.index("590")+10]
    # Splits each line up into data entries, creates a matrix of lists.
    for dataLine in dataList:
        dataMatrix.append(dataLine.split('\t'))
    # Removes the letter at the beginning, and the "590" that appears to be at the end of every line by removing the first and last entries.
    for line in dataMatrix:
        del line[-1]
        del line[0]
    
    # Turn everything into a float so we can use it.
    for r in range(len(dataMatrix)):
        for c in range(len(dataMatrix[r])):
            dataMatrix[r][c] = float(dataMatrix[r][c])


    '''
    Determining date and time of read.
    '''
    # Get a date and time.
    # Do this by finding the last line of the data audit trail.
    dateList = rawdataList[rawdataList.index("Data Audit Trail"):]
    for dLine in dateList:
        if "Plate read successfully completed" in dLine:
            dateLine = dLine
    # Split the line into two lists, one for the date and one for the time.
    # Organized such that dateVals = [y, m, d] and timeVals = [h, m, s].
    dateVals = dateLine.split()[0].split("/")
    timeVals = dateLine.split()[1].split(":")
    # Gets time from 12 hour to 24 hour format.
    if "PM" in dateLine and " 12:" not in dateLine:
        timeVals[0] = int(timeVals[0]) + 12
    if "AM" in dateLine and " 12:" in dateLine:
        timeVals[0] = 0
    # Finally, create a datetime object.
    newdate = datetime.datetime(int(dateVals[2]),int(dateVals[0]),int(dateVals[1]),int(timeVals[0]),int(timeVals[1]),int(timeVals[2]))

    # Close the file.
    rd.close()



    '''
    Storing data.
    '''
    # Initialize the lists used for sorting sample data.
    sampleMatrix1 = []
    sampleMatrix2 = []
    sampleMatrix3 = []
    # Create an array using values from dataMatrix.
    for row in dataMatrix:
        sampleMatrix1.append(row[0:4])  #wells in 1,2,3,4
        sampleMatrix2.append(row[4:8])  #wells in 5,6,7,8
        sampleMatrix3.append(row[8:12]) #wells in 9,10,11,12

    # If the sampleID does not yet exist in sampleDict, assign it to an empty list.
    for sampleID in plateDict[plateID]:
        if sampleID not in plateDict.keys():
            sampleDict[sampleID] = []

    # Appends this new read to the sample's entry in the dictionary.
    # [datetime.datetime(Date of Reading), list(Sample Matrix)]
    sampleDict[plateDict[plateID][0]].append([newdate, sampleMatrix1])
    sampleDict[plateDict[plateID][1]].append([newdate, sampleMatrix2])
    sampleDict[plateDict[plateID][2]].append([newdate, sampleMatrix3])



'''
Analyzing data.
'''
# Deletes the data coming from empty wells.
del sampleDict["empty"]
goodData = []
for sampleID in sampleDict.keys():
    # Sorts entries in each sample by date.
    sampleDict[sampleID] = sorted(sampleDict[sampleID], key=lambda item: item[0])
    # Goes through in order of date.
    for scan in sampleDict[sampleID]:
        awcd = calcAWCD(scan[1])
        # Appends a list to goodData in the format ['sampleID',[sampleMatrix]] if data is good.
        if awcd >= 0.4 and awcd <= 0.6 and sampleID != "empty":
            print(awcd)
            goodData.append([sampleID]+[scan[1]])
            # Breaks out of the for loop if a good read was obtained from a sample.
            break



'''
Exporting results.
'''
# Sort goodData by sampleID.
goodData = sorted(goodData, key=lambda item: item[0])
# Create a new CSV file and writer object.
csvfilename = datetime.datetime.now().strftime("./%Y%m%d_%H%M_viableAWCD.csv")
with open(csvfilename, 'w') as csvfile:
    # Creates writer object and header, then writes header.
    fileWriter = csv.writer(csvfile, delimiter=',')
    header = ["Sample ID"] + ["C"+str(i) for i in range(1,32)]
    fileWriter.writerow(header)

    for sample in goodData:
        # Make one long list in the format of [sampleID, C1, C2, C3 ... C31]
        writeList = [sample[0]]
        for wcd in sample[1]:
            writeList.extend([x-sample[1][0][0] for x in wcd])
        # Removes the control from each sample, then writes the line.
        del writeList[1]
        fileWriter.writerow(writeList)

    csvfile.close()
print("Wrote results to'",csvfilename+"'.")