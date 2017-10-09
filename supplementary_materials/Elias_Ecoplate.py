
# coding: utf-8

# In[ ]:

from __future__ import print_function, division
import numpy as np
import csv
import matplotlib.pyplot as plt
import openpyxl

from astropy.table import Table
from glob import glob
from datetime import datetime


# In[ ]:

alltxt = glob('*.txt')
#This part includes code to filter the files coming in, if the
#file names are standardized this shouldnt be needed
keepers = []
for index, file in enumerate(alltxt):
    if '(' in file:
        keepers.append(file)
#This part reads in an excell file that contains the locations
#of each sample to create a dictionary
#that houses these locations in tuple form

xlsxfile = openpyxl.load_workbook('Ecoplates master file.xlsx')
data_info = xlsxfile.get_sheet_by_name('Sheet1')
plates = [int(str(el[0].value)[1:4]) for el in data_info['A3':'A14']]
slot1 = [int(el[0].value) for el in data_info['B3':'B14']]
slot2 = [int(el[0].value) for el in data_info['C3':'C14']]
slot3 = [int(el[0].value) for el in data_info['D3':'D14']]

sample_dict = {}
for pos, slot in enumerate((slot1, slot2, slot3)):
    for index, el in enumerate(slot):
        sample_dict[el] = (plates[index], pos)

#This part creates a dictionary for the well designations and thier location and carbon source
#This is very messey, maybe a way of improving it using the pyxl thing. Or just make a ecoplate class or object thing
well_dict = {}
well_dict['A1'] = [(0,0), 'No carbon source']
well_dict['A2'] = [(0,1), 'beta-Methyl-D-Glucoside']
well_dict['A3'] = [(0,2), 'D-Galactonic Acid gamma-Lactone']
well_dict['A4'] = [(0,3), 'L-Arginine']
well_dict['B1'] = [(1,0), 'Pyruvic Acid Methyl Ester']
well_dict['B2'] = [(1,1), 'D-Xylose']
well_dict['B3'] = [(1,2), 'D-Galacturonic Acid']
well_dict['B4'] = [(1,3), 'L-Asparagine']
well_dict['C1'] = [(2,0), 'Tween 40']
well_dict['C2'] = [(2,1), 'i-Erythritol']
well_dict['C3'] = [(2,2), '2-Hydroxy Benzoic Acid']
well_dict['C4'] = [(2,3), 'L-Phenylalanine']
well_dict['D1'] = [(3,0), 'Tween 80']
well_dict['D2'] = [(3,1), 'D-Mannitol']
well_dict['D3'] = [(3,2), '4-Hydroxy Benzoic Acid']
well_dict['D4'] = [(3,3), 'L-Serine']
well_dict['E1'] = [(4,0), 'alpha-Cyclodextrin']
well_dict['E2'] = [(4,1), 'N-Acetyl-D-Glucosamine']
well_dict['E3'] = [(4,2), 'gamma-Hydroxybutyric']
well_dict['E4'] = [(4,3), 'L-Threonine']
well_dict['F1'] = [(5,0), 'Glycogen']
well_dict['F2'] = [(5,1), 'D-Glucosaminic Acid']
well_dict['F3'] = [(5,2), 'Itaconic Acid']
well_dict['F4'] = [(5,3), 'Glycyl-L-Glutamic Acid']
well_dict['G1'] = [(6,0), 'D-Cellobiose']
well_dict['G2'] = [(6,1), 'Glucose-1-Phosphate']
well_dict['G3'] = [(6,2), 'alpha-Ketobutyric']
well_dict['G4'] = [(6,3), 'Phenylethyl-amine']
well_dict['H1'] = [(7,0), 'alpha-D-Lactose']
well_dict['H2'] = [(7,1), 'D,L-apha-Glycerol Phosphate']
well_dict['H3'] = [(7,2), 'D-Malic Acid']
well_dict['H4'] = [(7,3), 'Putrescine']

top_row = ['','1','2','3','4']
other_rows = []
for let in ('A','B','C','D','E','F','G','H'):
    row = [let]
    for num in ('1','2','3','4'):
        row.append(well_dict[let+num][1])
    other_rows.append(row)
well_layout = Table(rows = other_rows, names=top_row)


#This loop orginizes the files by the samples that they represent
file_plates = []
for file in keepers:
    start = file.index('(')+1
    end = file.index(')')
    plate = file[start:end]
    if 'P' in plate:
        plate = file[start+1:end]
    file_plates.append(int(plate))

#Makes a list for each of the samples that contains off of the
#file names pretaining to that sample
plates = [[] for el in range(max(file_plates))]
for index, plate in enumerate(file_plates):
    plates[plate-1].append(keepers[index])


# In[ ]:

def slice_samples(raw_list, wavelength):
    """
    Description: This function takes the output from reading a
                dillimited text file from the plate reader and
                returns the measurements (wavelength dependant)
                of the three samples in the plate image.

    Preconditions: raw_list is the output of reading a
                   dillimited file with sections containing the
                   absorbance measurements of an ecoplate.
                   Wavelength must be an integer (probably
                   either 720 or 590)

    Postconditions: returns three arrays represneting the three
                    samples contained in the plate
    """
    for index, el in enumerate(raw_list):
        if el == [str(wavelength)]:
            if raw_list[index+1] != []:
                eco_plate = raw_list[index+2:index+10]
                initial_array = np.zeros((8,12))
                for index, el in enumerate(eco_plate):
                    float_row = [float(i) for i in el[1:13]]
                    initial_array[index,:] = float_row
    sample_1 = initial_array[:,0:4]
    sample_2 = initial_array[:,4:8]
    sample_3 = initial_array[:,8:12]
    return sample_1, sample_2, sample_3

def get_sample(base_array, sample, sample_dict):
    """
    Description: This function is meant to return all of the
                 data for a given sample

    Preconditions: base_array must be a 2D array containing
                   3 1D arrays that contain 1 2D arrays.
                   plate_num must be an integer, sample_index
                   must be an integer

    Postconditions: returns a 1-dimensional array that
                    represents the number of days since
                    innoculation each index in the array is an
                    array representing the plate readings of that
                    sampleon that day. If a plate was not read on
                    a particular day that index will be None.
    """
    plate_num, sample_index = sample_dict[sample]
    to_return = np.empty(len(base_array[:,0]), dtype = np.ndarray)
    for index, el in enumerate(base_array[:,plate_num-1]):
        if el == None:
            to_return[index] = el
        else:
            to_return[index] = el[sample_index]
    return to_return

def avg_wcd(sample_data):
    """
    Description: This function calculates the average well color
                 development of a given sample over time

    Preconditions: sample_data is a 1D array. Each element of
                   the array is either None or a 2D array
                   representing a given sample on a given day

    Postconditions: Returns a 1D array the same length as the
                    one passed into the function. Each element
                    in this array is a float representing average
                    well color development
    """
    awcd = np.zeros(len(sample_data))
    for index, day in enumerate(sample_data):
        if day == None:
            awcd[index] = None
        else:
            calib_well = day[0,0]
            calib_sample = day - calib_well
            awcd[index] = np.mean(calib_sample)
    return awcd

def relative_wcd(sample_data, well):
    """
    Description:This function calculates the relative individual well color developtment of a sample
    Preconditions:
    Postconditions:
    """
    awcd = avg_wcd(sample_data)
    relative_wcd = np.zeros(len(sample_data))
    for index, day in enumerate(sample_data):
        if day == None:
            relative_wcd[index] = None
        else:                      #Need to let people pass the tuple or the string designation for the well
            calib_well = day[0,0]
            desired_well = day[well_dict[well][0]]

            relative_wcd[index] = (desired_well - calib_well)/awcd[index]
    return relative_wcd

def wcd(sample_data, well):
    """
    Description:This function calculates the individual well color developtment of a sample
    Preconditions:
    Postconditions:
    """
    wcd = np.zeros(len(sample_data))
    for index, day in enumerate(sample_data):
        if day == None:
            wcd[index] = None
        else:                      #Need to let people pass the tuple or the string designation for the well
            calib_well = day[0,0]
            desired_well = day[well_dict[well][0]]

            wcd[index] = (desired_well - calib_well)
    return wcd


# In[ ]:

"""
This next little part just lets the user make corrections in case a plate was not read on the same day it was innoculated.
Simply enter:  offset_list[(plate number - 1)] = number of days first reading was after innoculation
"""

plate_nums = list(set(file_plates))
offset_list = [0 for el in plate_nums]
#Remember, python indexing starts at 0, so the first plate in
#the plate_nums (plate number 1) would be at index 0
offset_list[4] = 3 #Plate 5 offset 3 days
offset_list[5] = 3 #Plate 6 offset 3 days
offset_list[6] = 3 #Plate 7 offset 3 days

"""
Just a generalized way of determining number of days plates are being read for. If one plate is read for two weeks all of the
plates will be placed into a base array with a length 14 days.
"""
num_dates = 0
for plate in plates:
    if len(plate) > num_dates:
        num_dates = len(plate)
#print(num_dates)
base_array = np.empty(((num_dates),len(plates)),
                      dtype=np.ndarray)

for plate in range(len(base_array[0,:])):
    dates_read = [datetime(int(file[0:4]),int(file[4:6]),
                           int(file[6:8])) for file in plates[plate]]

    read_times = [(date-dates_read[0]).days for date in dates_read]
    for index, time in enumerate(read_times):
        t = open(plates[plate][index], 'r')
        raw = csv.reader(t, delimiter = '\t')
        raw_list = []
        for el in raw:
            raw_list.append(el)
        sample_1, sample_2, sample_3 = slice_samples(raw_list, '590')
        sample_array = np.array([sample_1, sample_2, sample_3])
        base_array[time+offset_list[plate],plate] = sample_array


# In[ ]:

samples_similar_awcd = {}
for index, sample in enumerate(sample_dict):
    diff = 10
    sample_data = get_sample(base_array, sample, sample_dict)
    for day, awcd in enumerate(avg_wcd(sample_data)):
        new_diff = 2 - awcd
        if new_diff < diff:
            diff = new_diff
            samples_similar_awcd[sample] = awcd, (sample_data[day] - sample_data[day][0,0])/awcd

sample_nums = sorted([key for key in sample_dict])
sample_rows = []
for sample in sample_nums:
    sample_row = [sample]
    sample_data = samples_similar_awcd[sample]
    sample_row.append(np.round(sample_data[0], 3))
    source_names = ['Sample', 'AWCD']
    for let in ('A','B','C','D','E','F','G','H'):
        for num in ('1','2','3','4'):
            sample_row.append(np.round(sample_data[1][well_dict[let+num][0]], 3))
            if sample == sample_nums[-1]:
                source_names.append(well_dict[let+num][1])
    sample_row.pop(2)
    sample_rows.append(sample_row)
source_names.pop(2)
awcd_data = Table(rows = sample_rows, names=source_names)


# In[ ]:




# In[ ]:

def get_choice(menu):
    for el in menu:
        print(el)
    choice = input('Please enter the number of your choice: ')
    while choice.isdigit() == False:
        choice = input('Your choice must be an integer')
    return choice

main_menu = ['EcoPlate Analysis Menu', '1. Sample Analysis',
             '2. Cross-Sample Analysis', '3. Write AWCD data to file', '4. Exit']

sample_analysis_menu = ['1. Average Well Color Development', '2. Individual'+
                        ' Well Analysis', '3. Relative Individual Well Analysis', '4. Print Well Layout', '5. Back']

choice = int(get_choice(main_menu))
while choice != 4:
    if choice == 1:
        sample = int(input('Please enter the sample number \n Example: 16001 \n'))
        while sample not in sample_dict.keys():
            sample = int(input('Sample not found, please enter a different sample: '))
        sample_data = get_sample(base_array, sample, sample_dict)
        choice = int(get_choice(sample_analysis_menu))
        while choice != 5:


            if choice == 1:
                awcd = avg_wcd(sample_data)
                plt.plot(awcd, 'o')
                plt.title(str(sample)+' Average Well Colour Development')
                plt.show()
            elif choice == 2:
                well = input('Enter the well designation: ')
                if well not in well_dict.keys():
                    well = input('Designation not found. A1 thourgh H4')
                print('Well Carbon Source: '+well_dict[well][1])
                well_cd = wcd(sample_data, well)
                plt.plot(well_cd, 'o')
                plt.title(well+' Color Development')
                plt.show()
            elif choice == 3:
                well = input('Enter the well designation: ')
                if well not in well_dict.keys():
                    well = input('Designation not found. A1 thourgh H4. Try again: ')
                print('Well Carbon Source: '+well_dict[well][1])
                well_rcd = relative_wcd(sample_data, well)
                plt.plot(well_rcd, 'o')
                plt.title(well+' Color Development')
                plt.show()
            elif choice == 4:
                well_layout.pprint(max_width = 1000)
            else:
                print('Input is out of range, try again: ')
            choice = int(get_choice(sample_analysis_menu))


    elif choice == 2:
        print('Does the second thing')
    elif choice == 3:
        file_name = input('Data will be saved as an ascii.csv file in the current directory \n Please enter a file name: ')
        awcd_data.write(file_name+'.csv', format='ascii.csv')
    else:
        print('Input is out of range')
    choice = int(get_choice(main_menu))


# In[ ]:




# In[ ]:




# In[ ]:
