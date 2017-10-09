'''
plate class
'''

'''
Description:    
Preconditions:  
Postconditions: 
'''

#create plate class 
class Plate:
    sourceMatrix = []

    def __init__(self, rawdata):
        '''
        Description:    
        Preconditions:  "rawdata" is a string containing an ecoplate scan output
        Postconditions: None
        '''
        dataMatrix = []
        #splits the initial string input into a list where each item is a single line
        rawdataList = rawdata.split("\n")
        #selects out the data we want to use, which starts at the "529" wavelength header
        dataList = rawdataList[rawdataList.index("529")+1:rawdataList.index("529")+9]
        #splits each line into a list containing a single reading, puts them into another list \
        # to act as a 2D array, then removes the useless number at the end of each line
        for i in range(len(dataList)):
            dataMatrix.append([dataList[i].split('\t')])
            del dataMatrix[i][-1]

    def getSources():
        '''
        Description:    Prints out the name of the carbon sources being used
        Preconditions:  None
        Postconditions: returns a large, multiline string
        '''
        colList = [chr(x) for x in range(65+len(sourceMatrix))]
        colList.insert(0,"\t")
        rowList = [x+1 for x in range(len(sourceMatrix[0]))]
        colList.insert(0,"\t")

    def __str__(self):
        '''
        Description:    Overrides print() with a readable output
        Preconditions:  None
        Postconditions: Returns a large, multiline string
        '''
        returnStr = ''
        x = 0
        #Create a string that has a number of formatted values
        for row in self.dataMatrix:
            for i in range(x,x+len(row)):
                returnStr += "$"+str(i)+".30s "
                x += 1
            returnStr +="\n"
        #Create a list that will contain the values we will assign to each format variable
        sourceFormatList = []
        for row in dataMatrix:
            for entry in dataMatrix:
                sourceFormatList += entry       
        return returnStr.format(sourceFormatList)

    def __len__(self):
        '''
        Description: overrides len() and returns how many entries are on each plate
        Preconditions: None
        Postconditions: None
        '''
        return sum(len(l) for l in dataMatrix)

    