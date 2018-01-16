I'll get around to formally writing this eventually, I promise.
For now, all you need to do is get an OAuth2 key here: http://gspread.readthedocs.io/en/latest/oauth2.html, then replace the auth_key variable with your auth .json file.
Run the program using "python Ecoplate_Analysis.py /path/to/directory [-r]", where you use -r if you want the program to recursively look in directories present in the provided directory.
If you just want the files in the initial directory ran, not any subdirs, then do not use -r.

Files must be formatted in the following manner:
description_of_plate_and_scan P1234.txt, where a space separates the description and the plate ID. 
Each file name should have one and only one space.