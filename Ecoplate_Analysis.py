'''
Description:    Ecoplate analysis software to calculate AWCD for ecoplate scans.
'''
import csv
import os
import sys
import re
import datetime
import gspread
from time import sleep
from oauth2client.service_account import ServiceAccountCredentials

'''
HI REMEMBER TO REMOVE ME AND REPLACE WITH SARA'S KEY
'''

# gspread authorization 
scope = ['https://spreadsheets.google.com/feeds']
# replace this auth_path variable here with the path to your OAuth2 authentication .json file
# you can create one here:   http://gspread.readthedocs.io/en/latest/oauth2.html
auth_path = '/home/brady/Documents/research/ecoplate_analysis/gspread_api-a3dd38e5d3e8.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(auth_path, scope)
gc = gspread.authorize(credentials)

'''
END IMPORTANT THING
'''


__author__ = "Brady Vizenor"
__date__ = "01/08/2018"



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
    fileList = [dirpath+fi for fi in os.listdir(dirPath) if fi[0:8].isdigit and fi.lower().endswith(".txt")]
    if recursionCheck:
        subdirList = [dirPath+subdir for subdir in os.listdir(dirPath) if os.path.isdir(dirPath+subdir)]
        for subdir in subdirList:
            fileList.extend(getFileList(subdir, True)
    return fileList



'''
SECTION 1:  Importing data.
'''
# Initialize the dictionary that will hold each sample's information.
sampleDict = {}
# Get list of data files, either recursively or not depending on if recursive tag is supplied
if "-r" in sys.argv[2:]:
    fileList = getFileList(sys.argv[1], True)
else:
    fileList = getFileList(sys.argv[1])


# Open the master file spreadsheet
master_file = gc.open("Ecoplates master file")
master_wks = master_file.worksheet("Sheet2")


print("\n","WARNING! This program takes some time to run.\n")
sleep(3)

for fileName in fileList:
    #grabs the plate ID defined as any digit in the second half of the file name
            #change this so it looks for all values after the space if unique IDs with letters are wanted
    plateID = ''.join([n for n in fileName.split()[1] if n.isdigit()])
    
    #opens the file in read mode
    rd = open(fileName,"r")
    lineMatrix = []
    # Splits the file into a list of lines
    rawdataList = rd.read().split("\n")
    
    # Searches for the line that reads "590", which indicates the beginning of the useful data, then isolates the data we want to look at using that index
    dataList = rawdataList[rawdataList.index("590")+1:rawdataList.index("590")+11]
    # Splits each line in that isolated data block into a list of data entries
    for i in range(len(dataList)):
        lineMatrix.append(dataList[i].split('\t'))
        # Removes the "590" that appears to be at the end of every line

    del(lineMatrix[-1])
    del(lineMatrix[0])
    dataMatrix = []
    for row in lineMatrix:
        dataMatrix.append([i for i in row if not i.isalpha()])

    # At this point each item in our new data matrix is still typed as a string, change them to floats to make it easier to calculate AWCD
    for r in range(len(dataMatrix)):
        for c in range(len(dataMatrix[r])):
            dataMatrix[r][c] = float(dataMatrix[r][c])

    print(fileName)

    # Next, get a date/time
    dateList = rawdataList[rawdataList.index("Data Audit Trail"):]
    for dLine in dateList:
        if "Plate read successfully completed" in dLine:
            dateLine = dLine
    dateVals = dateLine.split()[0].split("/")
    timeVals = dateLine.split()[1].split(":")
    if "PM" in dateLine and " 12:" not in dateLine:
        timeVals[0] = int(timeVals[0]) + 12
    if "AM" in dateLine and " 12:" in dateLine:
        timeVals[0] = 0
    newdate = datetime.datetime(int(dateVals[2]),int(dateVals[0]),int(dateVals[1]),int(timeVals[0]),int(timeVals[1]),int(timeVals[2]))

    
    # Close the file.
    rd.close()


    # Creates a regular expression
    # Can't really explain how it works, but looks for at least one character that is A-Z or a-z at the beginning of the string.
                        # Can't remember what ID format was decided on, get back to this.
    plate_re = re.compile("^[A-Za-z]+"+plateID)

    # Finds the numerical value for the cell row.
    cellrow = master_wks.find(plate_re).row
    #cellrow = master_wks.find("P"+plateID)
  
    #Creates a list of sample IDs that are present in 
    sampleIDList = [str(master_wks.cell(cellrow,2).value),str(master_wks.cell(cellrow,3).value),str(master_wks.cell(cellrow,4).value)]
    print(sampleIDList,"\n")

    # at this point we have a list of sampleIDs named sampleIDList
    sampleMatrix1 = []
    sampleMatrix2 = []
    sampleMatrix3 = []
    # creates 2D lists containing data for each sample
    for row in dataMatrix:
        sampleMatrix1.append(row[0:4])  #0123
        sampleMatrix2.append(row[4:8])  #4567
        sampleMatrix3.append(row[8:12]) #8901

    # add each sampleID to the dictionary if the sampleID is not in the dictionary already
    for sampleID in sampleIDList:
        if sampleID not in sampleDict.keys():
            sampleDict[sampleID] = []

    # append each new reading to the sample's dictionary entry with the format
    # [datetime.datetime(Date of Reading), list(Sample Matrix)]
    sampleDict[sampleIDList[0]].append([newdate, sampleMatrix1])
    sampleDict[sampleIDList[1]].append([newdate, sampleMatrix2])
    sampleDict[sampleIDList[2]].append([newdate, sampleMatrix3])



'''
SECTION 2: Analyzing data.
'''

goodData = []
for sampleID in sampleDict.keys():
    #sorts entries in each sample by date
    sampleDict[sampleID] = sorted(sampleDict[sampleID], key=lambda item: item[0])
    #goes through in order of newly sorted entries
    for entry in sampleDict[sampleID]:
        awcd = calcAWCD(entry[1])
        if awcd <= 0.6 and awcd >= 0.4 and sampleID != "empty":
            # appends a list to goodData in the format ['sampleID',[sampleMatrix]]
            goodData.append([sampleID]+[entry[1]])
            # breaks to the next sample ID when this happens, so no subsequent scans will be added to our output
            break


    
    

'''
SECTION 3: Exporting results.
'''
# Sort goodData by sampleID.
goodData = sorted(goodData, key=lambda item: item[0])
# Create new CSV file and writer object
csvfilename = datetime.datetime.now().strftime("./%Y%m%d_%H%M_viableAWCD.csv")
with open(csvfilename,'w') as csvfile:
    fileWriter = csv.writer(csvfile, delimiter=',')
    # Create and write header to csv file
    header = ["Sample ID"] + ["C"+str(i) for i in range(1,32)]
    fileWriter.writerow(header)

    for sample in goodData:
        # Make one long list in the format of [sampleID, C1, C2, C3, ... C31]
        writeList = [sample[0]]
        for ss in sample[1]:
            writeList.extend([x-sample[1][0][0] for x in ss)])
        # Remove the control from each sample.
        del writeList[1]
        # And write out the final product!
        fileWriter.writerow(writeList)

    csvfile.close()




